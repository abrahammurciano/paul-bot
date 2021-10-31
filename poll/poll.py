from typing import Iterable, List, Literal, Optional, Set, Tuple, Union, TYPE_CHECKING
import asyncpg
from disnake.utils import deprecated
from mention import Mention
from poll.command_params import PollCommandParams
import sql
import disnake
from .option import Option
from datetime import datetime

if TYPE_CHECKING:
	from paul import Paul


class Poll:
	def __init__(
		self,
		poll_id: int,
		question: str,
		options: Iterable[Option],
		message: disnake.Message,
		author: Optional[Union[disnake.User, disnake.Member]],
		expires: Optional[datetime],
		allow_multiple_votes: bool,
		allowed_vote_viewers: Iterable[Mention],
		allowed_editors: Iterable[Mention],
		allowed_voters: Iterable[Mention],
	):
		self.__poll_id = poll_id
		self.__question = question
		self.__options = tuple(options)
		self.__message = message
		self.__author = author
		self.__expires = expires
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
	def message(self) -> disnake.Message:
		"""The message containing the poll."""
		return self.__message

	@property
	def author(self) -> Optional[Union[disnake.User, disnake.Member]]:
		"""The member who created the poll, or None if he's no longer in the guild."""
		return self.__author

	@property
	def expires(self) -> Optional[datetime]:
		"""The time when the poll no longer accepts votes, or None if it doesn't expire."""
		return self.__expires

	@property
	def is_active(self) -> bool:
		"""True if the poll hasn't expired, False otherwise."""
		return self.expires is None or self.expires > datetime.now()

	@property
	def vote_count(self) -> int:
		"""Get the sum of the number of votes cast for each option."""
		return sum(option.vote_count for option in self.options)

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

	@classmethod
	async def create_poll(
		cls,
		conn: asyncpg.Connection,
		params: PollCommandParams,
		message: disnake.Message,
		author: Union[disnake.User, disnake.Member],
	) -> "Poll":
		assert message.guild is not None, "The poll's message must be in a guild."
		poll_id = (
			await sql.insert.one(
				conn,
				"polls",
				returning="id",
				question=params.question,
				message=message.id,
				channel=message.channel.id,
				guild=message.guild.id,
				author=author.id,
				expires=params.expires,
				allow_multiple_votes=params.allow_multiple_votes,
			)
		)["id"]
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
			message,
			author,
			params.expires,
			params.allow_multiple_votes,
			params.allowed_vote_viewers,
			params.allowed_editors,
			params.allowed_voters,
		)

	@classmethod
	async def get_active_polls(cls, bot: "Paul") -> Set["Poll"]:
		"""Get the polls which have not yet expired.

		Returns:
			Set[Poll]:	A set of Poll objects whose expiry date is in the future.
		"""
		records = await sql.select.many(
			bot.conn,
			"active_polls_view",
			(
				"id",
				"question",
				"message",
				"channel",
				"guild",
				"expires",
				"allow_multiple_votes",
			),
		)
		polls = set()
		for r in records:
			if message := await cls.__fetch_message(
				bot, r["message"], r["channel"], r["guild"]
			):
				polls.add(
					cls(
						r["id"],
						r["question"],
						await Option.get_options_of_poll(bot.conn, r["id"]),
						message,
						await bot.get_guild(r["guild"]).get_member(r["author"]),
						r["expires"],
						r["allow_multiple_votes"],
						await cls.__get_permissions(
							bot.conn, "allowed_vote_viewers", r["id"]
						),
						await cls.__get_permissions(
							bot.conn, "allowed_editors", r["id"]
						),
						await cls.__get_permissions(
							bot.conn, "allowed_voters", r["id"]
						),
					)
				)
		return polls

	@staticmethod
	async def __fetch_message(
		client: disnake.Client,
		message_id: int,
		channel_or_thread_id: int,
		guild_id: int,
	) -> Optional[disnake.Message]:
		"""Fetch a message given its ID and the ID of the channel or thread that it's in.

		Args:
			client (disnake.Client): Client who will fetch the message.
			message_id (int): The ID of the message to fetch.
			channel_or_thread_id (int): The ID of the channel or thread that the message is in.
			guild_id (int): The ID of the guild that the message is in.

		Returns:
			Optional[disnake.Message]: The message object, or None if it was not found in the given channel.

		Raises:
			ValueError: If the given channel or thread id is not found in the guild.
			disnake.NotFound: If the message was not found in the given channel or thread.
		"""
		guild = client.get_guild(guild_id)
		if guild is None:
			raise ValueError("Could not find a guile with the given ID.")
		channel_or_thread = guild.get_channel_or_thread(channel_or_thread_id)
		if not isinstance(channel_or_thread, disnake.TextChannel) or isinstance(
			channel_or_thread, disnake.Thread
		):
			raise ValueError("There is no text channel or thread with that ID.")
		return await channel_or_thread.fetch_message(message_id)

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
