from typing import Iterable, Mapping

import asyncpg

from ..application.option import Option
from . import sql
from .cruds import Crud


class OptionsCrud(Crud):
    def __init__(self, pool: asyncpg.pool.Pool) -> None:
        super().__init__(pool)

    async def add(self, options: Iterable[Option]) -> Mapping[int, int]:
        """Adds options of a poll to the database.

        Args:
            labels: The labels of the options.
            poll: The poll the options belong to.
            author_id: The ID of the person who added the option. If this option existed since the poll's creation, this should be None. (Default is None)

        Returns:
            A mapping of the option index to the option's ID as assigned by the database.
        """
        records = await sql.insert.many(
            self.pool,
            "options",
            ("label", "poll_id", "author", "index"),
            [
                (option.label, option.poll.poll_id, option.author_id, option.index)
                for option in options
            ],
            returning="id, index",
        )
        return {r["index"]: r["id"] for r in records}
