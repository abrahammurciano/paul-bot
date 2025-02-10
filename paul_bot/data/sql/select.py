from typing import Any, Coroutine, Iterable, Protocol

import asyncpg

from . import util


async def many(
    pool: asyncpg.Pool, table: str, columns: Iterable[str] = ("*",), **conditions: Any
) -> list[asyncpg.Record]:
    """Select all rows in a table matching the kwargs `conditions`.

    For security reasons it is important that the only user input passed into this function is via the values of `**conditions`.

    Args:
        pool: The connection pool to select rows from.
        table: The name of the table to select from.
        columns: The names of columns to select. Defaults to all columns.
        **conditions: Keyword arguments specifying constraints on the select statement. For a kwarg A=B, the select statement will only match rows where the column named A has the value B.

    Returns:
        A list of the records in the table.
    """
    return await __select(table, columns, pool.fetch, **conditions)


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
    return await __select(table, columns, pool.fetchrow, **conditions)


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
    return await __select(table, (column,), pool.fetchval, **conditions)


class Fetcher[T](Protocol):
    def __call__(self, query: str, *values: Any) -> Coroutine[Any, Any, T]: ...


async def __select[
    T
](table: str, columns: Iterable[str], fetcher: Fetcher[T], **conditions) -> T:
    filtered_columns, values = util.split_dict(conditions)
    query = f"SELECT {', '.join(columns)} FROM {table}{util.where(filtered_columns)}"
    return await fetcher(query, *values)
