from typing import Iterable, List, Optional, Set
import sql


class Option:
	"""Represents an option that a user can choose in a poll."""

	def __init__(
		self,
		option_id: int,
		label: str,
		votes: Iterable[int],
		author: Optional[int] = None,
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
		self.__author = author
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
	def author(self) -> Optional[int]:
		"""The ID of the member who added the option, or None if the option existed from poll creation."""
		return self.__author

	@property
	def votes(self) -> Set[int]:
		"""The set of IDs of members who voted on this option."""
		return self.__votes.copy()

	async def add_vote(self, voter_id: int):
		await sql.insert("votes", option_id=self.option_id, voter_id=voter_id)

	@classmethod
	async def get_voters(cls, option_id: int) -> Set[int]:
		"""Fetch the IDs of all the voters for a given option from the database.

		Args:
			option_id (int): The ID of the option to fetch the voters for.

		Returns:
			List[int]: A list of the IDs of the members who voted on the option.
		"""
		return {
			r["voter_id"]
			for r in await sql.select.many("votes", ("voter_id",), option_id=option_id)
		}

	@classmethod
	async def create_option(cls, label: str, poll_id: int) -> "Option":
		"""Create a new Option and add it to the database.

		Args:
			label (str): The label of the option.
			poll_id (int): The id of the poll that this option belongs to.

		Returns:
			Option: The new Option object.
		"""
		option_id = await sql.insert(
			"options", returning="id", label=label, poll_id=poll_id
		)
		return Option(option_id, label, ())

	@classmethod
	async def get_options_of_poll(cls, poll_id: int) -> List["Option"]:
		"""Get the options of a poll given its ID.

		Returns:
			List[Option]: A list of Option objects belonging to the given poll.
		"""
		records = await sql.select.many(
			"options", ("id", "label", "author"), poll_id=poll_id
		)
		return [
			cls(r["id"], r["label"], await cls.get_voters(r["id"]), r["author"])
			for r in records
		]
