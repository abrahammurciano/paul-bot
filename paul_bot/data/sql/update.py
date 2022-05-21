import asyncpg
from typing import Any
from . import util


async def update(
    pool: asyncpg.Pool, table: str, set: dict[str, Any], where: dict[str, Any]
):
    """Update rows in a table setting the values determined by the dictionary `set` of the columns which match the conditions defined in the `where` dictionary.

    Args:
            pool (asyncpg.Pool): The connection pool to use.
            table (str): The table whose records to update.
            set (dict[str, Any]): A dictionary whose keys are the column names to update and whose values are the values to set for its respective column.
            where (dict[str, Any]): A dictionary whose keys are column names and whose values are values that must be matched in the database for each row to be updated.
    """
    set_columns, set_values = util.split_dict(set)
    placeholders = util.placeholders()
    set_clause = ", ".join(f"{column} = {next(placeholders)}" for column in set_columns)
    where_columns, where_values = util.split_dict(where) if where else ("1", 1)
    where_clause = ", ".join(
        f"{column} = {next(placeholders)}" for column in where_columns
    )
    query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(query, *set_values, *where_values)
