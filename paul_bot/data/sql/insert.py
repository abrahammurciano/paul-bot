from itertools import chain
from typing import Any, Iterable, Sequence, overload

import asyncpg

from . import util


@overload
async def one(
    pool: asyncpg.Pool,
    table: str,
    *,
    on_conflict: str | None = None,
    returning: str,
    **fields: Any,
) -> Any: ...


@overload
async def one(
    pool: asyncpg.Pool,
    table: str,
    *,
    on_conflict: str | None = None,
    returning: Iterable[str],
    **fields: Any,
) -> tuple: ...


@overload
async def one(
    pool: asyncpg.Pool,
    table: str,
    *,
    on_conflict: str | None = None,
    returning: None = None,
    **fields: Any,
) -> None: ...


async def one(
    pool: asyncpg.Pool,
    table: str,
    *,
    on_conflict: str | None = None,
    returning: str | Iterable[str] | None = None,
    **fields: Any,
) -> Any:
    """Run an insert statement on the given table.

    For security reasons it is important that the only user input passed into this function is via the values of `**fields`.

    Args:
        pool: The connection pool to send the query to.
        table: The name of the table to insert into.
        on_conflict: The on_conflict clause to add to the query. For example can be "DO NOTHING" to suppress errors if the record already exists.
        returning: Either a column name to return just that value, or an iterable of column names to return a tuple of those values, or None to return None. Typically this would be the name of the serial primary key column but doesn't have to be. By default the function returns None.
        fields: The values to insert into the given table.

    Returns:
        If according to the `returning` clause, the insert statement returns a single value, this function returns said value. If the insert statement returns a row of values, this function returns a tuple of the values. If the insert statement returns nothing, this function returns None.
    """
    keys, values = util.split_dict(fields)
    results = await many(
        pool, table, keys, (values,), on_conflict=on_conflict, returning=returning
    )
    return results[0] if results is not None else None


@overload
async def many(
    pool: asyncpg.Pool,
    table: str,
    columns: Iterable[str],
    records: Sequence[Sequence],
    *,
    on_conflict: str | None = None,
    returning: str,
) -> list[Any]: ...


@overload
async def many(
    pool: asyncpg.Pool,
    table: str,
    columns: Iterable[str],
    records: Sequence[Sequence],
    *,
    on_conflict: str | None = None,
    returning: Iterable[str],
) -> list[asyncpg.Record]: ...


@overload
async def many(
    pool: asyncpg.Pool,
    table: str,
    columns: Iterable[str],
    records: Sequence[Sequence],
    *,
    on_conflict: str | None = None,
    returning: None = None,
) -> None: ...


async def many(
    pool: asyncpg.Pool,
    table: str,
    columns: Iterable[str],
    records: Sequence[Sequence],
    *,
    on_conflict: str | None = None,
    returning: str | Iterable[str] | None = None,
) -> list[asyncpg.Record] | list[Any] | None:
    """Insert many rows into a database.

    Args:
        pool: The connection pool to send the query to.
        table: The name of the table to insert into.
        columns: The column names for which to insert values. The order of the columns must match the order of the values in the parameter `records`.
        records: An sequence containing the rows to insert. Each row must be a sequence of values in the order specified in the `columns` parameter.
        on_conflict: The on_conflict clause to add to the query. For example can be "DO NOTHING" to suppress errors if the record already exists.
        returning: Either a column name to return a list with just that value for each inserted record, or an iterable of column names to return a tuple of those values, or None to return None. Typically this would be the name of the serial primary key column but doesn't have to be. By default the function returns None.

    Returns:
        If according to the returning clause multiple columns are returned by the database, then this function returns a list of said records. If the database returns one column, then a list of said items is returned. If the insert statement returns no records, then None is returned.
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
    async with pool.acquire() as conn:
        async with conn.transaction():
            results = await conn.fetch(query, *chain(*records))
            if returning is None:
                return None
            if results and len(results[0]) > 1:
                return results
            return [result[0] for result in results]


def __with_conflict_returning(
    query: str,
    on_conflict: str | None,
    returning: str | Iterable[str] | None,
) -> str:
    """Return a query with an ON CONFLICT clause and a RETURNING clause if specified.

    Args:
        query: The original query to be used.
        on_conflict: The ON CONFLICT clause to be added. If None, there will be no ON CONFLICT clause.
        returning: The RETURNING clause to be added. If None, there will be no RETURNING clause.

    Returns:
        The new query with the requested clauses.
    """
    if on_conflict:
        query += f" ON CONFLICT {on_conflict}"
    if returning:
        query += (
            " RETURNING"
            f" {returning if isinstance(returning, str) else ' (' + ', '.join(returning) + ')'}"
        )
    return query
