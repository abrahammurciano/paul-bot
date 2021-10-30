from typing import Iterable, List, Optional, Set

import asyncpg
import sql


class Option:
	"""Represents an option that a user can choose in a poll."""

	def __init__(
		self,
		option_id: int,
		label: str,
		votes: Iterable[int],
		author_id: Optional[int] = None,
	):
		"""Construct a Option object.

		Args:
			option_id (int): The unique identifier for the option.
			label (str): The label for the option.
			author (Optional[int], optional): The ID of the member who added the option. If the option existed from poll creation, this should be None. Default is None.
			votes (Iterable[int]): The disnake IDs of the members who voted for this option.
		"""
		self.__option_id = option_id
		self.__label = label
		self.__author_id = author_id
		self.__votes = set(votes)

	@property
	def option_id(self) -> int:
		"""The id of the option."""
		return self.__option_id

	@property
	def label(self) -> str:
		"""The label of the option."""
		return self.__label

	@property
	def author_id(self) -> Optional[int]:
		"""The ID of the member who added the option, or None if the option existed from poll creation."""
		return self.__author_id

	@property
	def votes(self) -> Set[int]:
		"""The set of IDs of members who voted on this option."""
		return self.__votes.copy()

	@property
	def vote_count(self) -> int:
		"""Get the number of votes for this option."""
		return len(self.__votes)

	async def add_vote(self, conn: asyncpg.Connection, voter_id: int):
		await sql.insert.one(conn, "votes", option_id=self.option_id, voter_id=voter_id)

	@classmethod
	async def get_voters(cls, conn: asyncpg.Connection, option_id: int) -> Set[int]:
		"""Fetch the IDs of all the voters for a given option from the database.

		Args:
			option_id (int): The ID of the option to fetch the voters for.

		Returns:
			List[int]: A list of the IDs of the members who voted on the option.
		"""
		return {
			r["voter_id"]
			for r in await sql.select.many(
				conn, "votes", ("voter_id",), option_id=option_id
			)
		}

	@classmethod
	async def create_options(
		cls,
		conn: asyncpg.Connection,
		labels: Iterable[str],
		poll_id: int,
		author_id: Optional[int] = None,
	) -> List["Option"]:
		"""Create new Option objects for the given poll and add them to the database.

		Args:
			labels (str): The labels of the options to add.
			poll_id (int): The id of the poll that this option belongs to.
			author_id (Optional[int], optional): The ID of the person who added this option, or None if the options were created at the time of creation.

		Returns:
			List[Option]: The new Option objects.
		"""
		records = await sql.insert.many(
			conn,
			"options",
			("label", "poll_id", "author"),
			[(label, poll_id, author_id) for label in labels],
			returning="id, label",
		)
		return [Option(r["id"], r["label"], (), author_id) for r in records]

	@classmethod
	async def get_options_of_poll(
		cls, conn: asyncpg.Connection, poll_id: int
	) -> List["Option"]:
		"""Get the options of a poll given its ID.

		Returns:
			List[Option]: A list of Option objects belonging to the given poll.
		"""
		records = await sql.select.many(
			conn, "options", ("id", "label", "author"), poll_id=poll_id
		)
		return [
			cls(r["id"], r["label"], await cls.get_voters(conn, r["id"]), r["author"])
			for r in records
		]
