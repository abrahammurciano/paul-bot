from typing import Any, Dict, Generator, List, Sequence, Tuple


def where(columns: Sequence[str]) -> str:
	"""Construct a where clause where if `columns` contains the columns A, B, C, ..., the resulting string would look like " WHERE A = $1 AND B = $2 AND C = $3 AND ..."

	Args:
		columns (Sequence[str]): A sequence of column names to be included in the where clause.

	Returns:
		str: A string containing the where clause.
	"""
	expressions = " AND ".join(
		f"{column} = ${i}" for i, column in enumerate(columns, start=1)
	)
	return "" if not columns else f" WHERE {expressions}"


def prepare_kwargs(kwargs: Dict[str, Any]) -> Tuple[Tuple[str, ...], Tuple[Any, ...]]:
	"""Create two tuples from the provided kwargs.

	The first tuple is the keys of the kwargs. The second tuple is the values.

	Args:
		kwargs (Dict[str, Any]): A dictionary of keyword arguments.

	Returns:
		Tuple[Tuple[str], Tuple[Any]]: A tuple containing a tuple of the keys from the kwargs in the first index and a tuple of the values from the kwargs in the second index.
	"""
	keys = tuple(kwargs.keys())
	values = tuple(kwargs[key] for key in keys)
	return keys, values


def placeholders(n: int) -> Generator[str, None, None]:
	"""Get n placeholders for asyncpg. E.g. $1, $2, etc.

	Args:
		n (int): The number of placeholders to get.

	Returns:
		Generator[str]: The placeholders.
	"""
	return (f"${i + 1}" for i in range(n))