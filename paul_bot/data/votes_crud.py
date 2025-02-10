import asyncpg

from . import sql
from .cruds import Crud


class VotesCrud(Crud):
    def __init__(self, pool: asyncpg.Pool) -> None:
        super().__init__(pool)

    async def add(self, option_id: int, voter_id: int) -> None:
        await sql.insert.one(
            self.pool,
            "votes",
            on_conflict="DO NOTHING",
            option_id=option_id,
            voter_id=voter_id,
        )

    async def delete_users_votes_from_poll(self, poll_id: int, voter_id: int) -> None:
        """Delete all votes from the given user on the given poll.

        Args:
            poll_id: The poll ID to delete votes from.
            voter_id: The ID of the user whose votes to delete.
        """
        await sql.delete(
            self.pool,
            "votes",
            f"option_id in (select id from options where poll_id = {poll_id})",
            voter_id=voter_id,
        )

    async def delete_users_votes_from_option(
        self, option_id: int, voter_id: int
    ) -> None:
        """Delete a vote from the given user on the given option.

        Args:
            option_id: The option ID to delete the vote from.
            voter_id: The ID of the user whose vote to delete.
        """
        await sql.delete(
            self.pool,
            "votes",
            option_id=option_id,
            voter_id=voter_id,
        )
