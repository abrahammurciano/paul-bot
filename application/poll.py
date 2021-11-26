from typing import Iterable, List, Optional, Set, Tuple
from disnake import Message
import pytz
from application.mention import Mention
from presentation.command_params import PollCommandParams
import data
from .option import Option
from datetime import datetime


class Poll:
	def __init__(
		self,
		poll_id: Optional[int],
		question: str,
		expires: Optional[datetime],
		author_id: int,
		allow_multiple_votes: bool,
		allowed_vote_viewers: Iterable[Mention],
		allowed_editors: Iterable[Mention],
		allowed_voters: Iterable[Mention],
		message_id: int,
		channel_id: int,
		closed: bool,
	):
		self.__poll_id = poll_id
		self.__question = question
		self.__expires = expires
		self.__author_id = author_id
		self.__allow_multiple_votes = allow_multiple_votes
		self.__allowed_vote_viewers = tuple(allowed_vote_viewers)
		self.__allowed_editors = tuple(allowed_editors)
		self.__allowed_voters = tuple(allowed_voters)
		self.__message_id = message_id
		self.__channel_id = channel_id
		self.__closed = closed
		self.__options: List[Option] = []

	@property
	def poll_id(self) -> int:
		"""The id of the poll."""
		if self.__poll_id is None:
			raise ValueError(
				"Poll doesn't have an ID yet since it has not been added to the"
				" database."
			)
		return self.__poll_id

	@property
	def question(self) -> str:
		"""The question of the poll."""
		return self.__question

	@property
	def options(self) -> Tuple[Option, ...]:
		"""The options of the poll that users can choose from."""
		return tuple(self.__options)

	@property
	def expires(self) -> Optional[datetime]:
		"""The time when the poll no longer accepts votes, or None if it doesn't expire."""
		return self.__expires

	@property
	def author_id(self) -> int:
		"""The ID of the member who created the poll."""
		return self.__author_id

	@property
	def allow_multiple_votes(self) -> bool:
		"""Whether or not the poll allowes a user to vote on multiple options."""
		return self.__allow_multiple_votes

	@property
	def allowed_vote_viewers(self) -> Tuple[Mention, ...]:
		"""The mentions of the users or roles who are allowed to view people's votes."""
		return self.__allowed_vote_viewers

	@property
	def allowed_editors(self) -> Tuple[Mention, ...]:
		"""The mentions of the users or roles who are allowed to add options to the poll."""
		return self.__allowed_editors

	@property
	def allowed_voters(self) -> Tuple[Mention, ...]:
		"""The mentions of the users or roles who are allowed to vote on the poll."""
		return self.__allowed_voters

	@property
	def is_expired(self) -> bool:
		"""True if the poll has expired, False otherwise."""
		return self.expires is not None and self.expires < datetime.now(pytz.utc)

	@property
	def is_opened(self) -> bool:
		"""True if the poll is still opened (if the vote buttons are showing), False otherwise."""
		return not self.__closed

	@property
	def vote_count(self) -> int:
		"""Get the sum of the number of votes cast for each option."""
		return sum(option.vote_count for option in self.options)

	@property
	def message_id(self) -> int:
		"""The ID of the message containing the poll."""
		return self.__message_id

	@property
	def channel_id(self) -> int:
		"""The ID of the channel containing the poll."""
		return self.__channel_id

	async def new_option(self, label: str, author_id: int) -> Option:
		"""Add an option to the poll.

		Args:
			label (str): The label of the option to add.
			author_id (int): The ID of the user who added the option.

		Returns:
			Option: The created option.
		"""
		option = await Option.create_option(label, self, author_id)
		self.add_option(option)
		return option

	async def close(self):
		"""Close the poll.

		This function will mark it as closed and expired in the database and update the message accordingly.

		Args:
			bot (Paul): The bot to use to update the message.
		"""
		now = datetime.now(pytz.utc)
		if not self.is_expired:
			self.__expires = now
		await data.cruds.polls_crud.update_expiry(self, now, closed=True)

	async def remove_votes_from(self, voter_id: int):
		"""Remove all votes from the given user on this poll.

		Args:
			voter_id (int): The ID of the user whose votes should be removed.
		"""
		await data.cruds.votes_crud.delete_users_votes_from_poll(self.poll_id, voter_id)
		for option in self.options:
			option.remove_vote(voter_id)

	def add_option(self, option: Option):
		"""Add option objects to the poll."""
		self.__options.append(option)

	@classmethod
	async def create_poll(
		cls, params: PollCommandParams, author_id: int, message: Message,
	) -> "Poll":
		poll = Poll(
			None,
			params.question,
			params.expires,
			author_id,
			params.allow_multiple_votes,
			params.allowed_vote_viewers,
			params.allowed_editors,
			params.allowed_voters,
			message.id,
			message.channel.id,
			False,
		)
		poll.__poll_id = await data.cruds.polls_crud.add(poll)
		for option in await Option.create_options(params.options, poll):
			poll.add_option(option)
		return poll

	@classmethod
	async def fetch_polls(cls) -> Set["Poll"]:
		"""Get all the polls from the database.

		Returns:
			Set[Poll]:	A set of Poll objects.
		"""
		return await data.cruds.polls_crud.fetch_all()