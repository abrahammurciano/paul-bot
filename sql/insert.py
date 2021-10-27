from typing import Any
import asyncpg
from . import util


async def insert(
	conn: asyncpg.Connection,
	table: str,
	on_conflict: str = None,
	returning: str = None,
	**fields,
) -> Any:
	"""Run an insert statement on the given table.

	For security reasons it is important that the only user input passed into this function is via the values of `**fields`.

	Args:
		table (str): The name of the table to insert into.
		returning (str, optional): The name of the column whose value to return from the inserted row. Commonly this would be the auto-incremented ID but doesn't have to be. By default the function returns None.
		fields: The values to insert into the given table.

	Returns:
		Any: The value of the column `returning` in the newly inserted row, or None if no column was specified.
	"""
	keys, values, placeholders = util.prepare_kwargs(fields)
	query = (
		f"INSERT INTO {table} ({', '.join(keys)}) VALUES"
		f" ({', '.join(placeholders)})"
		f" {'ON CONFLICT ' + on_conflict if on_conflict else ''}"
		f" {('RETURNING ' + returning) if returning else ''}"
	)
	async with conn.transaction():
		return await conn.fetchval(query, *values)