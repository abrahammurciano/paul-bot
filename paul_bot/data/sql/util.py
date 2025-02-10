from itertools import count
from typing import Any, Generator, Sequence


def where(columns: Sequence[str]) -> str:
    """Construct a where clause where if `columns` contains the columns A, B, C, ..., the resulting string would look like " WHERE A = $1 AND B = $2 AND C = $3 AND ..."

    Args:
        columns: A sequence of column names to be included in the where clause.

    Returns:
        A string containing the where clause.
    """
    expressions = " AND ".join(
        f"{column} = ${i}" for i, column in enumerate(columns, start=1)
    )
    return "" if not columns else f" WHERE {expressions}"


def split_dict(dictionary: dict[str, Any]) -> tuple[tuple[str, ...], tuple[Any, ...]]:
    """Create two tuples from the provided dictionary.

    The first tuple is the keys of the dictionary. The second tuple is the values. They are guaranteed to be in matching order.

    Args:
        dictionary: A dictionary to split.

    Returns:
        A tuple containing a tuple of the keys from the dictionary in the first index and a tuple of the values from the dictionary in the second index.
    """
    keys = tuple(dictionary.keys())
    values = tuple(dictionary[key] for key in keys)
    return keys, values


def placeholders(n: int | None = None) -> Generator[str, None, None]:
    """Get n placeholders for asyncpg. E.g. $1, $2, etc.

    Args:
        n: The number of placeholders to get. Default is unlimited.

    Returns:
        A generator yielding placeholders as strings.
    """
    return (f"${i + 1}" for i in (range(n) if n is not None else count()))
