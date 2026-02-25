from collections.abc import Iterable, Mapping

from paul_bot.application.option import Option

from . import sql
from .cruds import Crud


class OptionsCrud(Crud):
    async def add(self, options: Iterable[Option]) -> Mapping[int, int]:
        """Add options of a poll to the database.

        Args:
            options: The options to add to the database.

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
            returning=("id", "index"),
        )
        return {r["index"]: r["id"] for r in records}
