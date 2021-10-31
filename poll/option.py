from typing import Iterable, List, Optional, Set, Tuple, TYPE_CHECKING
import asyncpg
import sql

if TYPE_CHECKING:
	from poll.poll import Poll


class Option:
	"""Represents an option that a user can choose in a poll."""

	def __init__(
		self,
		option_id: int,
		label: str,
		votes: Iterable[int],
		poll: "Poll",
		author_id: Optional[int] = None,
	):
		"""Construct a Option object.

		Args:
			option_id (int): The unique identifier for the option.
			label (str): The label for the option.
			votes (Iterable[int]): The disnake IDs of the members who voted for this option.
			poll (Poll): The Poll that the option belongs to.
			author_id (Optional[int], optional): The ID of the member who added the option. If the option existed from poll creation, this should be None. Default is None.
		"""
		self.__option_id = option_id
		self.__label = label
		self.__votes = set(votes)
		self.__poll = poll
		self.__author_id = author_id

	@property
	def option_id(self) -> int:
		"""The id of the option."""
		return self.__option_id

	@property
	def label(self) -> str:
		"""The label of the option."""
		return self.__label

	@property
	def votes(self) -> Set[int]:
		"""The set of IDs of members who voted on this option."""
		return self.__votes.copy()

	@property
	def poll(self) -> "Poll":
		"""The Poll that the option belongs to."""
		return self.__poll

	@property
	def author_id(self) -> Optional[int]:
		"""The ID of the member who added the option, or None if the option existed from poll creation."""
		return self.__author_id

	@property
	def vote_count(self) -> int:
		"""Get the number of votes for this option."""
		return len(self.__votes)

	async def remove_vote(self, conn: asyncpg.Connection, voter_id: int):
		"""Remove a vote from the given user on this option. If no such vote exists, nothing happens.

		Args:
			conn (asyncpg.Connection): A connection to the database.
			voter_id (int): The ID of the user whose vote is to be removed.
		"""
		await sql.delete(conn, "votes", option_id=self.option_id, voter_id=voter_id)
		self.__votes.discard(voter_id)

	async def add_vote(self, conn: asyncpg.Connection, voter_id: int):
		"""Add a vote from the given user on this option. If such a vote already exists, nothing happens. If the poll cannot have more than one vote per user, all other votes from this user are removed.

		Args:
			conn (asyncpg.Connection): A connection to the database.
			voter_id (int): The ID of the user whose vote is to be added.
		"""
		if not self.poll.allow_multiple_votes:
			await self.poll.remove_votes_from(conn, voter_id)
		await sql.insert.one(
			conn,
			"votes",
			on_conflict="DO NOTHING",
			option_id=self.option_id,
			voter_id=voter_id,
		)
		self.__votes.add(voter_id)

	async def toggle_vote(self, conn: asyncpg.Connection, voter_id: int):
		"""Toggle a user's vote on this option. If adding their vote would cause too many votes from the same user, the rest of their votes are removed.

		Args:
			conn (asyncpg.Connection): The database connection.
			voter_id (int): The ID of the user to toggle the vote of.
		"""
		if voter_id in self.votes:
			await self.remove_vote(conn, voter_id)
		else:
			await self.add_vote(conn, voter_id)

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
		poll: "Poll",
		author_id: Optional[int] = None,
	) -> Tuple["Option", ...]:
		"""Create new Option objects for the given poll and add them to the database.

		Args:
			labels (str): The labels of the options to add.
			poll (Poll): The poll that this option belongs to.
			author_id (Optional[int], optional): The ID of the person who added this option, or None if the options were created at the time of creation.

		Returns:
			Tuple[Option, ...]: The new Option objects.
		"""
		records = await sql.insert.many(
			conn,
			"options",
			("label", "poll_id", "author"),
			[(label, poll.poll_id, author_id) for label in labels],
			returning="id, label",
		)
		return tuple(Option(r["id"], r["label"], (), poll, author_id) for r in records)

	@classmethod
	async def get_options_of_poll(
		cls, conn: asyncpg.Connection, poll: "Poll"
	) -> List["Option"]:
		"""Get the options of a poll given its ID.

		Args:
			conn (asyncpg.Connection): A connection to the database.
			poll (Poll): The poll to get the options of.

		Returns:
			List[Option]: A list of Option objects belonging to the given poll.
		"""
		records = await sql.select.many(
			conn, "options", ("id", "label", "author"), poll_id=poll.poll_id
		)
		return [
			cls(
				r["id"],
				r["label"],
				await cls.get_voters(conn, r["id"]),
				poll,
				r["author"],
			)
			for r in records
		]
