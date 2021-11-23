from typing import Generator, Iterable, List, Optional, Set, TYPE_CHECKING, Tuple
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
		author_id: Optional[int],
	):
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

	async def remove_vote(self, voter_id: int, remove_from_database: bool = True):
		"""Remove a vote from the given user on this option. If no such vote exists, nothing happens.

		Args:
			voter_id (int): The ID of the user whose vote is to be removed.
			remove_from_database (bool): Whether or not to remove the vote from the database. Default is True. Should be False if for example the vote was already removed.
		"""
		if remove_from_database:
			await sql.delete(
				self.poll.pool, "votes", option_id=self.option_id, voter_id=voter_id
			)
		self.__votes.discard(voter_id)

	async def add_vote(self, voter_id: int):
		"""Add a vote from the given user on this option. If such a vote already exists, nothing happens. If the poll cannot have more than one vote per user, all other votes from this user are removed.

		Args:
			voter_id (int): The ID of the user whose vote is to be added.
		"""
		if not self.poll.allow_multiple_votes:
			await self.poll.remove_votes_from(voter_id)
		await sql.insert.one(
			self.poll.pool,
			"votes",
			on_conflict="DO NOTHING",
			option_id=self.option_id,
			voter_id=voter_id,
		)
		self.__votes.add(voter_id)

	async def toggle_vote(self, voter_id: int):
		"""Toggle a user's vote on this option. If adding their vote would cause too many votes from the same user, the rest of their votes are removed.

		Args:
			voter_id (int): The ID of the user to toggle the vote of.
		"""
		if voter_id in self.__votes:
			await self.remove_vote(voter_id)
		else:
			await self.add_vote(voter_id)

	@classmethod
	async def create_options(
		cls, labels: Iterable[str], poll: "Poll", author_id: Optional[int] = None,
	) -> Generator["Option", None, None]:
		"""Create new Option objects for the given poll and add them to the database.

		Args:
			labels (str): The labels of the options to add.
			poll (Poll): The ID of the poll that this option belongs to.
			author_id (Optional[int], optional): The ID of the person who added this option, or None if the options were created at the time of creation.

		Returns:
			Generator[Option, ...]: The new Option objects.
		"""
		records = await sql.insert.many(
			poll.pool,
			"options",
			("label", "poll_id", "author", "index"),
			[
				(label, poll.poll_id, author_id, index)
				for index, label in enumerate(labels, start=len(poll.options))
			],
			returning="id, label",
		)
		return (cls(r["id"], r["label"], (), poll, author_id) for r in records)

	@classmethod
	def construct_options_of_poll(
		cls,
		poll: "Poll",
		options: List[Tuple[int, str, Optional[int], Optional[Iterable[int]]]],
	) -> List["Option"]:
		"""Construct a list of options for a poll given a list of tuples returned from the database.

		The format of these tuples is as follows. The first element is the option' ID. The second element is the option's label. The third is the author's id if the option was added after the poll's creation. The fourth element is a collection of the IDs of the people who voted on the option.

		Args:
			poll (Poll): The polls that these options belong to.
			options (List[Tuple]): The list of options to construct. Each option is a tuple in the format mentioned above.

		Returns:
			List[Option]: A list of the options of the given poll.
		"""
		return [
			cls(
				option_id=option[0],
				label=option[1],
				votes=option[3] or (),
				poll=poll,
				author_id=option[2],
			)
			for option in options
		]