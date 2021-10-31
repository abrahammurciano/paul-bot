from typing import Iterable, List, Literal, Optional, Set, Tuple, Union, TYPE_CHECKING
import asyncpg
from mention import Mention
from poll.command_params import PollCommandParams
import sql
import disnake
from .option import Option
from datetime import datetime


class Poll:
	def __init__(
		self,
		poll_id: int,
		question: str,
		options: Iterable[Option],
		expires: Optional[datetime],
		author_id: int,
		allow_multiple_votes: bool,
		allowed_vote_viewers: Iterable[Mention],
		allowed_editors: Iterable[Mention],
		allowed_voters: Iterable[Mention],
	):
		self.__poll_id = poll_id
		self.__question = question
		self.__options = tuple(options)
		self.__expires = expires
		self.__author_id = author_id
		self.__allow_multiple_votes = allow_multiple_votes
		self.__allowed_vote_viewers = tuple(allowed_vote_viewers)
		self.__allowed_editors = tuple(allowed_editors)
		self.__allowed_voters = tuple(allowed_voters)

	@property
	def poll_id(self) -> int:
		"""The id of the poll."""
		return self.__poll_id

	@property
	def question(self) -> str:
		"""The question of the poll."""
		return self.__question

	@property
	def options(self) -> Tuple[Option, ...]:
		"""The options of the poll that users can choose from."""
		return self.__options

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
	def is_active(self) -> bool:
		"""True if the poll hasn't expired, False otherwise."""
		return self.expires is None or self.expires > datetime.now()

	@property
	def vote_count(self) -> int:
		"""Get the sum of the number of votes cast for each option."""
		return sum(option.vote_count for option in self.options)

	@classmethod
	async def create_poll(
		cls, conn: asyncpg.Connection, params: PollCommandParams, author_id: int
	) -> "Poll":
		poll_id: int = await sql.insert.one(
			conn,
			"polls",
			returning="id",
			question=params.question,
			author=author_id,
			expires=params.expires,
			allow_multiple_votes=params.allow_multiple_votes,
		)
		await cls.__insert_permissions(
			conn, "allowed_vote_viewers", params.allowed_vote_viewers, poll_id
		)
		await cls.__insert_permissions(
			conn, "allowed_editors", params.allowed_editors, poll_id
		)
		await cls.__insert_permissions(
			conn, "allowed_voters", params.allowed_voters, poll_id
		)
		options = await Option.create_options(conn, params.options, poll_id)
		return Poll(
			poll_id,
			params.question,
			options,
			params.expires,
			author_id,
			params.allow_multiple_votes,
			params.allowed_vote_viewers,
			params.allowed_editors,
			params.allowed_voters,
		)

	@classmethod
	async def get_active_polls(cls, conn: asyncpg.Connection) -> Set["Poll"]:
		"""Get the polls which have not yet expired.

		Args:
			conn (asyncpg.Connection): The database connection to get the active polls from.

		Returns:
			Set[Poll]:	A set of Poll objects whose expiry date is in the future.
		"""
		records = await sql.select.many(
			conn,
			"active_polls_view",
			("id", "question", "expires", "author", "allow_multiple_votes",),
		)
		return {
			cls(
				r["id"],
				r["question"],
				await Option.get_options_of_poll(conn, r["id"]),
				r["expires"],
				r["author"],
				r["allow_multiple_votes"],
				await cls.__get_permissions(conn, "allowed_vote_viewers", r["id"]),
				await cls.__get_permissions(conn, "allowed_editors", r["id"]),
				await cls.__get_permissions(conn, "allowed_voters", r["id"]),
			)
			for r in records
		}

	@staticmethod
	async def __insert_permissions(
		conn: asyncpg.Connection, table: str, mentions: Iterable[Mention], poll_id: int
	):
		await sql.insert.many(
			conn,
			table,
			("poll_id", "mention_prefix", "mention_id"),
			[(poll_id, mention.prefix, mention.mentioned_id) for mention in mentions],
			on_conflict="DO NOTHING",
		)

	@staticmethod
	async def __get_permissions(
		conn: asyncpg.Connection,
		table: Literal["allowed_vote_viewers", "allowed_editors", "allowed_voters"],
		poll_id: int,
	) -> List[Mention]:
		return [
			Mention(r["mention_prefix"], r["mention_id"])
			for r in await sql.select.many(
				conn, table, ("mention_prefix", "mention_id"), poll_id=poll_id
			)
		]
