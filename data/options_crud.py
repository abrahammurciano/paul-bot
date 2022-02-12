from typing import Iterable, Mapping
import asyncpg
from datetime import datetime
import pytz
from application.option import Option
from data import sql
from data.cruds import Crud


class OptionsCrud(Crud):
	def __init__(self, pool: asyncpg.pool.Pool):
		super().__init__(pool)

	async def add(self, options: Iterable[Option]) -> Mapping[int, int]:
		"""Adds options of a poll to the database.

		Args:
			labels (Iterable[str]): The labels of the options.
			poll (Poll): The poll the options belong to.
			author_id (Optional[int]): The ID of the person who added the option. If this option existed since the poll's creation, this should be None. (Default is None)

		Returns:
			Mapping[int, int]: A mapping of the option index to the option's ID as assigned by the database.
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

	async def archive(self, id: int):
		"""Archive an option in the database.

		Args:
			id (int): The ID of the option to archive.
		"""
		archived_datetime = datetime.now(pytz.utc)

		record = await sql.update(
			self.pool,
			"options",
			set={"archived": archived_datetime},
			where={"id": id},
		)

		return record