from typing import Any, Dict, Sequence, Tuple


def where(columns: Sequence[str], placeholders: Sequence[str]) -> str:
	"""Construct a where clause where if the ith and jth elements of `columns` are A and B respectively, and X and Y are the ith and jth elements of `placeholders`, the resulting string would look like " WHERE A = X AND B = Y"

	Args:
		columns (Sequence[str]): A sequence of column names to be included in the where clause.
		placeholders (Sequence[str]): A sequence of placeholders to place as the values of their corresponding columns.

	Returns:
		str: A string containing the where clause.
	"""
	expressions = " AND ".join(
		f"{column} = {placeholder}"
		for column, placeholder in zip(columns, placeholders)
	)
	return "" if not columns else f" WHERE {expressions}"


def prepare_kwargs(
	kwargs: Dict[str, Any]
) -> Tuple[Sequence[str], Sequence[Any], Sequence[str]]:
	"""Create three sequences from the provided kwargs.

	The first sequence is the keys of the kwargs. The second sequence is the values. The third sequence is the placeholders for the SQL prepared statements (e.g. $1, $2, etc).

	Args:
		kwargs (Dict[str, Any]): A dictionary of keyword arguments.

	Returns:
		Tuple[Sequence[str], Sequence[Any], Sequence[str]]: A tuple containing a sequence of the keys from the kwargs in the first index, a sequence of the values from the kwargs in the second index, and a sequence of the placeholders for the SQL prepared statements in the third index.
	"""
	keys, values, placeholders = (
		zip(*[(key, kwargs[key], f"${index}") for index, key in enumerate(kwargs, 1)])
		if kwargs
		else ((), (), ())
	)
	return keys, values, placeholders