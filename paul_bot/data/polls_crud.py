from datetime import datetime
from typing import TYPE_CHECKING, AsyncIterator, Iterable

import asyncpg

from ..application.mention import Mention
from ..application.option import Option
from . import sql
from .cruds import Crud

if TYPE_CHECKING:
    from paul_bot.application.poll import Poll


class PollsCrud(Crud):
    def __init__(self, pool: asyncpg.pool.Pool) -> None:
        super().__init__(pool)

    async def add(self, poll: "Poll") -> int:
        """Add a poll to the database.

        Args:
            poll: The poll to add to the database.

        Returns:
            The poll's ID.
        """
        poll_id: int = await sql.insert.one(
            self.pool,
            "polls",
            returning="id",
            question=poll.question,
            author=poll.author_id,
            expires=poll.expires,
            allow_multiple_votes=poll.allow_multiple_votes,
            message=poll.message_id,
            channel=poll.channel_id,
        )
        await self.__insert_permissions(
            "allowed_vote_viewers", poll.allowed_vote_viewers, poll_id
        )
        await self.__insert_permissions(
            "allowed_editors", poll.allowed_editors, poll_id
        )
        await self.__insert_permissions("allowed_voters", poll.allowed_voters, poll_id)
        return poll_id

    async def delete(self, poll_id: int) -> None:
        """Delete a poll from the database.

        Args:
                poll_id (int): The ID of the poll to delete.
        """
        await sql.delete(self.pool, "polls", id=poll_id)

    async def __insert_permissions(
        self, table: str, mentions: Iterable[Mention], poll_id: int
    ):
        await sql.insert.many(
            self.pool,
            table,
            ("poll_id", "mention_prefix", "mention_id"),
            [(poll_id, mention.prefix, mention.mentioned_id) for mention in mentions],
            on_conflict="DO NOTHING",
        )

    def fetch_all(self) -> AsyncIterator["Poll"]:
        """Get an async iterator over all the polls from the database."""
        records = sql.select.many(
            self.pool,
            "polls_extended_view",
            (
                "id",
                "question",
                "expires",
                "author",
                "allow_multiple_votes",
                "message",
                "channel",
                "closed",
                "options",
                "allowed_editors",
                "allowed_vote_viewers",
                "allowed_voters",
            ),
        )
        return (self.__init_poll(r) async for r in records)

    async def update_expiry(
        self, poll: "Poll", expires: datetime, closed: bool
    ) -> None:
        """Update the expiry date of a poll and set its closed status accordingly.

        Args:
            poll: The poll to update.
            expires: The new expiry date.
            closed: Whether the poll has been closed.
        """
        await sql.update(
            self.pool,
            "polls",
            set={"expires": expires, "closed": closed},
            where={"id": poll.poll_id},
        )

    def __parse_options(
        self,
        poll: "Poll",
        options: list[tuple[int, str, int | None, Iterable[int] | None, int]],
    ) -> list[Option]:
        """Construct a list of options for a poll given a list of tuples returned from the database.

        The format of these tuples is as follows. The first element is the option' ID. The second element is the option's label. The third is the author's id if the option was added after the poll's creation. The fourth element is a collection of the IDs of the people who voted on the option. The fifth element is the index of the option within the poll.

        Args:
            poll: The polls that these options belong to.
            options: The list of options to construct. Each option is a tuple in the format mentioned above.

        Returns:
            A list of the options of the given poll.
        """
        return [
            Option(
                option_id=option[0],
                label=option[1],
                votes=option[3] or (),
                poll=poll,
                index=option[4],
                author_id=option[2],
            )
            for option in options
        ]

    def __init_poll(self, record: asyncpg.Record) -> "Poll":
        # must be imported here to avoid circular imports
        from ..application.poll import Poll

        poll = Poll(
            record["id"],
            record["question"],
            record["expires"],
            record["author"],
            record["allow_multiple_votes"],
            (
                Mention(mention[0], mention[1])
                for mention in record["allowed_vote_viewers"]
            ),
            (Mention(mention[0], mention[1]) for mention in record["allowed_editors"]),
            (Mention(mention[0], mention[1]) for mention in record["allowed_voters"]),
            record["message"],
            record["channel"],
            record["closed"],
        )
        for option in self.__parse_options(poll, record["options"]):
            poll.add_option(option)
        return poll
