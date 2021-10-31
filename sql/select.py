from typing import (
	Any,
	Coroutine,
	Iterable,
	List,
	Optional,
	Protocol,
	TypeVar,
)
import asyncpg
from . import util


async def many(
	pool: asyncpg.Pool, table: str, columns: Iterable[str] = ("*",), **conditions
) -> List[asyncpg.Record]:
	"""Select all rows in a table matching the kwargs `conditions`.

	For security reasons it is important that the only user input passed into this function is via the values of `**conditions`.

	Args:
		pool (asyncpg.Pool): The connection pool to select rows from.
		table (str): The name of the table to select from.
		columns (Iterable[str], optional): The names of columns to select. Defaults to all columns.
		**conditions: Keyword arguments specifying constraints on the select statement. For a kwarg A=B, the select statement will only match rows where the column named A has the value B.

	Returns:
		List[asyncpg.Record]: A list of the records in the table.
	"""
	return await __select(table, columns, pool.fetch, **conditions)


async def one(
	pool: asyncpg.Pool, table: str, columns: Iterable[str] = ("*",), **conditions
) -> Optional[asyncpg.Record]:
	"""Select a single row from a table matching the kwargs `conditions`.

	For security reasons it is important that the only user input passed into this function is via the values of `**conditions`.

	Args:
		pool (asyncpg.Pool): The connection pool to select from.
		table (str): The name of the table to select from.
		columns (Iterable[str], optional): The names of the columns to select. Defaults to all columns.
		**conditions: Keyword arguments specifying constraints on the select statement. For a kwarg A=B, the select statement will only match rows where the column named A has the value B.

	Returns:
		Optional[asyncpg.Record]: The selected row if one was found, or None otherwise.
	"""
	return await __select(table, columns, pool.fetchrow, **conditions)


async def value(pool: asyncpg.Pool, table: str, column: str = "*", **conditions) -> Any:
	"""Select a single cell from a table where the column is the one specified and the row matches the kwargs `conditions`.

	For security reasons it is important that the only user input passed into this function is via the values of `**conditions`.

	Args:
		pool (asyncpg.Pool): The connection pool to select from.
		table (str): The name of the table to select from.
		column (str, optional): The names of the columns to select. Defaults to the first column.
		**conditions: Keyword arguments specifying constraints on the select statement. For a kwarg A=B, the select statement will only match rows where the column named A has the value B.

	Returns:
		Optional[Any]: The value of the selected cell if one was found, or None otherwise.
	"""
	return await __select(table, (column,), pool.fetchval, **conditions)


T = TypeVar("T", covariant=True)


class Fetcher(Protocol[T]):
	def __call__(self, query: str, *values: Any) -> Coroutine[Any, Any, T]:
		...


async def __select(
	table: str, columns: Iterable[str], fetcher: Fetcher[T], **conditions
) -> T:
	filtered_columns, values = util.prepare_kwargs(conditions)
	query = f"SELECT {', '.join(columns)} FROM {table}{util.where(filtered_columns)}"
	return await fetcher(query, *values)
