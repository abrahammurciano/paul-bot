import collections
from typing import Iterator, Mapping, Protocol, TypeVar

K = TypeVar("K")
V = TypeVar("V", covariant=True)


class ReadableMapping(Protocol[K, V]):
	def __getitem__(self, key: K) -> V:
		...

	def __len__(self) -> int:
		...

	def __iter__(self) -> Iterator[K]:
		...


class ReadableDict(ReadableMapping[K, V]):
	def __init__(self, data: Mapping[K, V]):
		self.__data = data

	def __getitem__(self, key: K) -> V:
		return self.__data[key]

	def __len__(self) -> int:
		return len(self.__data)

	def __iter__(self) -> Iterator[K]:
		return iter(self.__data)
