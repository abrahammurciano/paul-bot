import asyncpg
from . import util


async def delete(pool: asyncpg.Pool, table: str, **conditions):
	"""Delete the rows that satisfy the given conditions from the given table.

	Note, if no kwargs are passed to `conditions`, all rows will be deleted.

	For security reasons it is important that the only user input passed into this function is via the values of `**conditions`.

	Args:
		table (str): The name of the table to delete rows from.
		**conditions:  Keyword arguments specifying constraints on the select statement. For a kwarg A=B, the select statement will only match rows where the column named A has the value B.
	"""
	columns, values = util.prepare_kwargs(conditions)
	query = f"DELETE FROM {table}{util.where(columns)}"
	async with pool.acquire() as conn:
		async with conn.transaction():
			await conn.execute(query, *values)
