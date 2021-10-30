from typing import Iterable, List, Optional, Sequence, overload
import asyncpg
from . import util
from itertools import chain


@overload
async def one(
	conn: asyncpg.Connection,
	table: str,
	*,
	on_conflict: Optional[str] = None,
	returning: str,
	**fields,
) -> asyncpg.Record:
	...


@overload
async def one(
	conn: asyncpg.Connection,
	table: str,
	*,
	on_conflict: Optional[str] = None,
	returning: None = None,
	**fields,
) -> None:
	...


async def one(
	conn: asyncpg.Connection,
	table: str,
	*,
	on_conflict: Optional[str] = None,
	returning: Optional[str] = None,
	**fields,
) -> Optional[asyncpg.Record]:
	"""Run an insert statement on the given table.

	For security reasons it is important that the only user input passed into this function is via the values of `**fields`.

	Args:
		conn (asyncpg.Connection): The connection to send the query to.
		table (str): The name of the table to insert into.
		on_conflict (Optional[str], optional): The on_conflict clause to add to the query. For example can be "DO NOTHING" to suppress errors if the record already exists.
		returning (Optional[str], optional): The returning clause to add to the query. This can be a single column name, several column names, or any other valid SQL expression. Commonly this would be the name of the serial primary key column but doesn't have to be. By default the function returns None.
		fields: The values to insert into the given table.

	Returns:
		Optional[asyncpg.Record]: A record containing whatever was specified in the `returning` parameter, or None if nothing was specified.
	"""
	keys, values = util.prepare_kwargs(fields)
	result = await many(
		conn, table, keys, (values,), on_conflict=on_conflict, returning=returning
	)
	if result is None:
		return None
	else:
		return result[0]


@overload
async def many(
	conn: asyncpg.Connection,
	table: str,
	columns: Iterable[str],
	records: Sequence[Sequence],
	*,
	on_conflict: Optional[str] = None,
	returning: str,
) -> asyncpg.Record:
	...


@overload
async def many(
	conn: asyncpg.Connection,
	table: str,
	columns: Iterable[str],
	records: Sequence[Sequence],
	*,
	on_conflict: Optional[str] = None,
	returning: None = None,
) -> None:
	...


async def many(
	conn: asyncpg.Connection,
	table: str,
	columns: Iterable[str],
	records: Sequence[Sequence],
	*,
	on_conflict: Optional[str] = None,
	returning: Optional[str] = None,
) -> Optional[List[asyncpg.Record]]:
	"""Insert many rows into a database.

	Args:
		conn (asyncpg.Connection): The connection to send the query to.
		table (str): The name of the table to insert into.
		columns (Iterable[str]): The column names for which to insert values. The order of the columns must match the order of the values in the parameter `records`.
		records (Sequence[Sequence]): An sequence containing the rows to insert. Each row must be a sequence of values in the order specified in the `columns` parameter.
		on_conflict (Optional[str], optional): The on_conflict clause to add to the query. For example can be "DO NOTHING" to suppress errors if the record already exists.
		returning (Optional[str], optional): The returning clause to add to the query. This can be a single column name, several column names, or any other valid SQL expression. Commonly this would be the name of the serial primary key column but doesn't have to be. By default the function returns None.

	Returns:
		Optional[List[asyncpg.Record]]: A list of records containing whatever was specified in the `returning` parameter, or None if nothing was specified.
	"""
	placeholders = util.placeholders()
	values = ", ".join(
		f"({', '.join(next(placeholders) for _ in columns)})" for _ in records
	)
	if values == "":
		return []
	query = __with_conflict_returning(
		f"INSERT INTO {table} ({', '.join(columns)}) VALUES {values}",
		on_conflict,
		returning,
	)
	async with conn.transaction():
		result = await conn.fetch(query, *chain(*records))
		return result if returning is not None else None


def __with_conflict_returning(
	query: str, on_conflict: Optional[str], returning: Optional[str]
) -> str:
	"""Return a query with an ON CONFLICT clause and a RETURNING clause if specified.

	Args:
		query (str): The original query to be used.
		on_conflict (Optional[str]): The ON CONFLICT clause to be added. If None, there will be no ON CONFLICT clause.
		returning (Optional[str]): The RETURNING clause to be added. If None, there will be no RETURNING clause.

	Returns:
		str: The new query with the requested clauses.
	"""
	if on_conflict:
		query += f" ON CONFLICT {on_conflict}"
	if returning:
		query += f" RETURNING {returning}"
	return query