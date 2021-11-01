import asyncio
from typing import TYPE_CHECKING, Iterable, List, Literal, Optional, Set, Tuple
import asyncpg
from disnake import Message
import disnake
import pytz
from mention import Mention
from poll.command_params import PollCommandParams
from poll.embeds.poll_closed_embed import PollClosedEmbed
from poll.embeds.poll_embed import PollEmbed
from poll.ui.poll_view import PollView
import sql
from .option import Option
from datetime import datetime

if TYPE_CHECKING:
	from paul import Paul


class Poll:
	def __init__(
		self,
		poll_id: int,
		question: str,
		expires: Optional[datetime],
		author_id: int,
		allow_multiple_votes: bool,
		allowed_vote_viewers: Iterable[Mention],
		allowed_editors: Iterable[Mention],
		allowed_voters: Iterable[Mention],
		message_id: int,
		channel_id: int,
		pool: asyncpg.Pool,
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
		self.__pool = pool
		self.__options: List[Option] = []

	@property
	def pool(self) -> asyncpg.Pool:
		"""Get the connection pool to the database which holds this poll."""
		return self.__pool

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
	def is_active(self) -> bool:
		"""True if the poll hasn't expired, False otherwise."""
		return self.expires is None or self.expires > datetime.now(pytz.utc)

	@property
	def vote_count(self) -> int:
		"""Get the sum of the number of votes cast for each option."""
		return sum(option.vote_count for option in self.options)

	def embed(self) -> disnake.Embed:
		"""Get the embed for this poll."""
		return PollEmbed(self) if self.is_active else PollClosedEmbed(self)

	async def new_option(self, label: str, author_id: int) -> Option:
		"""Add an option to the poll.

		Args:
			label (str): The label of the option to add.
			author_id (int): The ID of the user who added the option.

		Returns:
			Option: The created option.
		"""
		option = next(await Option.create_options((label,), self, author_id))
		self.__add_options(option)
		return option

	@property
	def message_id(self) -> int:
		"""The ID of the message containing the poll."""
		return self.__message_id

	@property
	def channel_id(self) -> int:
		"""The ID of the channel containing the poll."""
		return self.__channel_id

	def close_when_expired(self, bot: "Paul"):
		"""Schedule a task to close the poll on its expiration. This operation is not blocking."""

		async def coro():
			if self.expires is None:
				return
			await asyncio.sleep((self.expires - datetime.now(pytz.utc)).total_seconds())
			await self.close(bot)

		asyncio.create_task(coro())

	async def close(self, bot: "Paul"):
		"""Close the poll.

		This function will mark it as closed and expired in the database and update the message accordingly.

		Args:
			bot (Paul): The bot to use to update the message.
		"""
		now = datetime.now(pytz.utc)
		if self.is_active:
			self.__expires = now
		await bot.update_poll_message(self)
		await sql.update(
			self.pool,
			"polls",
			set={"expires": now, "closed": True},
			where={"id": self.poll_id},
		)

	async def remove_votes_from(self, voter_id: int):
		"""Remove all votes from the given user on this poll.

		Args:
			voter_id (int): The ID of the user whose votes should be removed.
		"""
		for option in self.options:
			await option.remove_vote(voter_id)

	async def __add_options(self, *options: Option):
		"""Add option objects to the poll."""
		for option in options:
			self.__options.append(option)

	@classmethod
	async def create_poll(
		cls,
		params: PollCommandParams,
		author_id: int,
		message: Message,
		pool: asyncpg.Pool,
	) -> "Poll":
		poll_id: int = await sql.insert.one(
			pool,
			"polls",
			returning="id",
			question=params.question,
			author=author_id,
			expires=params.expires,
			allow_multiple_votes=params.allow_multiple_votes,
			message=message.id,
			channel=message.channel.id,
		)
		await cls.__insert_permissions(
			pool, "allowed_vote_viewers", params.allowed_vote_viewers, poll_id
		)
		await cls.__insert_permissions(
			pool, "allowed_editors", params.allowed_editors, poll_id
		)
		await cls.__insert_permissions(
			pool, "allowed_voters", params.allowed_voters, poll_id
		)
		poll = cls(
			poll_id,
			params.question,
			params.expires,
			author_id,
			params.allow_multiple_votes,
			params.allowed_vote_viewers,
			params.allowed_editors,
			params.allowed_voters,
			message.id,
			message.channel.id,
			pool,
		)
		await poll.__add_options(*await Option.create_options(params.options, poll))
		return poll

	@classmethod
	async def get_open_polls(cls, pool: asyncpg.Pool) -> Set["Poll"]:
		"""Get the polls which have not yet expired.

		Args:
			pool (Pool): The connection pool to use to fetch the polls.

		Returns:
			Set[Poll]:	A set of Poll objects whose expiry date is in the future.
		"""
		records = await sql.select.many(
			pool,
			"polls",
			(
				"id",
				"question",
				"expires",
				"author",
				"allow_multiple_votes",
				"message",
				"channel",
			),
			closed=False,
		)
		polls = {
			cls(
				r["id"],
				r["question"],
				r["expires"],
				r["author"],
				r["allow_multiple_votes"],
				await cls.__get_permissions(pool, "allowed_vote_viewers", r["id"]),
				await cls.__get_permissions(pool, "allowed_editors", r["id"]),
				await cls.__get_permissions(pool, "allowed_voters", r["id"]),
				r["message"],
				r["channel"],
				pool,
			)
			for r in records
		}
		for poll in polls:
			await poll.__add_options(*await Option.get_options_of_poll(poll))
		return polls

	@staticmethod
	async def __insert_permissions(
		pool: asyncpg.Pool, table: str, mentions: Iterable[Mention], poll_id: int
	):
		await sql.insert.many(
			pool,
			table,
			("poll_id", "mention_prefix", "mention_id"),
			[(poll_id, mention.prefix, mention.mentioned_id) for mention in mentions],
			on_conflict="DO NOTHING",
		)

	@staticmethod
	async def __get_permissions(
		pool: asyncpg.Pool,
		table: Literal["allowed_vote_viewers", "allowed_editors", "allowed_voters"],
		poll_id: int,
	) -> List[Mention]:
		return [
			Mention(r["mention_prefix"], r["mention_id"])
			for r in await sql.select.many(
				pool, table, ("mention_prefix", "mention_id"), poll_id=poll_id
			)
		]