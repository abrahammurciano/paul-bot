import asyncpg
from datetime import datetime
from typing import Iterable, List, Optional, Set, Tuple, TYPE_CHECKING
from . import sql
from .cruds import Crud
from ..application.mention import Mention
from ..application.option import Option

if TYPE_CHECKING:
	from application.poll import Poll


class PollsCrud(Crud):
	def __init__(self, pool: asyncpg.pool.Pool):
		super().__init__(pool)

	async def add(self, poll: "Poll") -> int:
		"""Add a poll to the database.

		Args:
			pool (asyncpg.Pool): The database connection pool.
			poll (Poll): The poll to add to the database.

		Returns:
			int: The poll's ID.
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

	async def delete(self, poll_id: int):
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

	async def fetch_all(self) -> Set["Poll"]:
		"""Get all the polls from the database.

		Args:
			pool (Pool): The connection pool to use to fetch the polls.

		Returns:
			Set[Poll]:	A set of Poll objects.
		"""
		records = await sql.select.many(
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

		# must be imported here to avoid circular imports
		from ..application.poll import Poll

		polls = set()
		for r in records:
			poll = Poll(
				r["id"],
				r["question"],
				r["expires"],
				r["author"],
				r["allow_multiple_votes"],
				(
					Mention(mention[0], mention[1])
					for mention in r["allowed_vote_viewers"]
				),
				(Mention(mention[0], mention[1]) for mention in r["allowed_editors"]),
				(Mention(mention[0], mention[1]) for mention in r["allowed_voters"]),
				r["message"],
				r["channel"],
				r["closed"],
			)
			for option in self.__parse_options(poll, r["options"]):
				poll.add_option(option)
			polls.add(poll)
		return polls

	async def update_expiry(self, poll: "Poll", expires: datetime, closed: bool):
		"""Update the expiry date of a poll and set its closed status accordingly.

		Args:
			poll (Poll): The poll to update.
			expires (datetime): The new expiry date.
			closed (bool): Whether the poll has been closed.
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
		options: List[Tuple[int, str, Optional[int], Optional[Iterable[int]], int]],
	) -> List[Option]:
		"""Construct a list of options for a poll given a list of tuples returned from the database.

		The format of these tuples is as follows. The first element is the option' ID. The second element is the option's label. The third is the author's id if the option was added after the poll's creation. The fourth element is a collection of the IDs of the people who voted on the option. The fifth element is the index of the option within the poll.

		Args:
			poll (Poll): The polls that these options belong to.
			options (List[Tuple]): The list of options to construct. Each option is a tuple in the format mentioned above.

		Returns:
			List[Option]: A list of the options of the given poll.
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