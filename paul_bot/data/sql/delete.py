from typing import Any

import asyncpg

from . import util


async def delete(
    pool: asyncpg.Pool, table: str, *other_conditions: str, **equals_conditions: Any
) -> None:
    """Delete the rows that satisfy the given conditions from the given table.

    Note, if no kwargs are passed to `other_conditions` or `equals_conditions`, all rows will be deleted.

    For security reasons it is important that the only user input passed into this function is via the values of `**equals_conditions`.

    Args:
        pool: The asyncpg pool to use for the database connection.
        table: The name of the table to delete rows from.
        *other_conditions: Each of these conditions specify a condition in the WHERE clause. For example, for conditions A,B the function will produce a query containing WHERE A AND B
        **equals_conditions:  Keyword arguments specifying constraints on the select statement. For a kwarg A=B, the select statement will only match rows where the column named A has the value B.
    """
    columns, values = util.split_dict(equals_conditions)
    other_conditions_str = (
        f" AND {' AND '.join(other_conditions)}" if other_conditions else ""
    )
    query = f"DELETE FROM {table}{util.where(columns)}{other_conditions_str}"
    async with pool.acquire() as conn, conn.transaction():  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        await conn.execute(query, *values)  # pyright: ignore[reportUnknownMemberType]
