from typing import Any, AsyncIterator, Iterable, cast

import asyncpg

from . import util


async def many(
    pool: asyncpg.Pool, table: str, columns: Iterable[str] = ("*",), **conditions: Any
) -> AsyncIterator[asyncpg.Record]:
    """Select all rows in a table matching the kwargs `conditions`.

    For security reasons it is important that the only user input passed into this function is via the values of `**conditions`.

    Args:
        pool: The connection pool to select rows from.
        table: The name of the table to select from.
        columns: The names of columns to select. Defaults to all columns.
        **conditions: Keyword arguments specifying constraints on the select statement. For a kwarg A=B, the select statement will only match rows where the column named A has the value B.

    Returns:
        An async generator yielding the selected rows.
    """
    query, values = __build_query(table, columns, **conditions)
    async with pool.acquire() as connection:
        conn = cast(asyncpg.Connection, connection)
        async with conn.transaction(readonly=True):
            async for record in conn.cursor(query, *values):
                yield record


async def one(
    pool: asyncpg.Pool, table: str, columns: Iterable[str] = ("*",), **conditions: Any
) -> asyncpg.Record | None:
    """Select a single row from a table matching the kwargs `conditions`.

    For security reasons it is important that the only user input passed into this function is via the values of `**conditions`.

    Args:
        pool: The connection pool to select from.
        table: The name of the table to select from.
        columns: The names of the columns to select. Defaults to all columns.
        **conditions: Keyword arguments specifying constraints on the select statement. For a kwarg A=B, the select statement will only match rows where the column named A has the value B.

    Returns:
        The selected row if one was found, or None otherwise.
    """
    query, values = __build_query(table, columns, **conditions)
    return await pool.fetchrow(query, *values)


async def value(
    pool: asyncpg.Pool, table: str, column: str = "*", **conditions: Any
) -> Any:
    """Select a single cell from a table where the column is the one specified and the row matches the kwargs `conditions`.

    For security reasons it is important that the only user input passed into this function is via the values of `**conditions`.

    Args:
        pool: The connection pool to select from.
        table: The name of the table to select from.
        column: The name of the column to select. Defaults to the first column.
        **conditions: Keyword arguments specifying constraints on the select statement. For a kwarg A=B, the select statement will only match rows where the column named A has the value B.

    Returns:
        The value of the selected cell if one was found, or None otherwise.
    """
    query, values = __build_query(table, (column,), **conditions)
    return await pool.fetchval(query, *values)


def __build_query(
    table: str, columns: Iterable[str], **conditions: Any
) -> tuple[str, tuple[Any, ...]]:
    filtered_columns, values = util.split_dict(conditions)
    query = f"SELECT {', '.join(columns)} FROM {table}{util.where(filtered_columns)}"
    return query, values
