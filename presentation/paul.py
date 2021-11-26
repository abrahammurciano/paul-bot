import asyncio
from typing import Iterable, List, Optional
import disnake
from disnake.enums import ActivityType
from disnake.errors import Forbidden
from disnake.ext.commands.bot import Bot
import logging
from disnake.ext.commands.params import Param
from disnake.interactions.application_command import GuildCommandInteraction
from disnake.interactions.message import MessageInteraction
from disnake.message import Message
from application import Poll
from application.option import Option
from presentation.command_params import PollCommandParams
from presentation.ui.poll_view import PollView
from presentation.embeds.poll_closed_embed import PollClosedEmbed
from presentation.embeds.poll_embed import PollEmbed
from presentation.embeds.poll_embed_base import PollEmbedBase
from presentation.converters import parse_expires, parse_mentions, parse_options
from datetime import datetime
from application import Mention
from disnake.interactions.base import Interaction
from presentation.errors import handle_error
import pytz


class Paul(Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__total_poll_count = 0
		self.__closed_poll_count = 0
		self.__activity_name = ""
		self.__on_ready_triggered = False

		@self.event
		async def on_ready():
			if not self.__on_ready_triggered:
				logging.info(f"\n{self.user.name} has connected to Discord!\n")
				await self.__load_polls()
				await self.__set_presence()
				self.__on_ready_triggered = True

		@self.event
		async def on_slash_command_error(inter: Interaction, error: Exception):
			await handle_error(error)

		@self.slash_command(desc="Create a poll")
		async def poll(
			inter: GuildCommandInteraction,
			question: str = Param(desc="Ask a question..."),
			options: Iterable[str] = Param(
				desc=(
					"Separate each option with a pipe (|). By default the options are"
					" yes or no."
				),
				converter=parse_options(sep="|"),
				default=("Yes", "No"),
			),
			expires: Optional[datetime] = Param(
				desc=(
					"When to stop accepting votes, e.g. 1h20m or 1pm UTC+2. Default"
					" timezone is UTC. Default is never."
				),
				converter=parse_expires,
				default=None,
			),
			allow_multiple_votes: bool = Param(
				desc="Can a user choose multiple options?", default=False
			),
			allowed_vote_viewers: List[Mention] = Param(
				desc=(
					"Mention members or roles who can view the votes. Default is no"
					" one."
				),
				default=[],
				converter=parse_mentions,
			),
			allowed_editors: List[Mention] = Param(
				desc=(
					"Mention members or roles who may add options to the poll. Default"
					" is only you."
				),
				default=lambda inter: [Mention("@", inter.author.id)],
				converter=parse_mentions,
			),
			allowed_voters: List[Mention] = Param(
				desc="Mention members or roles who may vote. Default is @everyone.",
				default=lambda inter: [Mention("@&", inter.guild.default_role.id)],
				converter=parse_mentions,
			),
		):
			await inter.response.send_message(
				embed=PollEmbedBase(
					question, "<a:loading:904120454975991828> Loading poll..."
				)
			)
			message = await inter.original_message()
			await self.new_poll(
				PollCommandParams(
					question,
					options,
					expires,
					allow_multiple_votes,
					allowed_vote_viewers,
					allowed_editors,
					allowed_voters,
				),
				inter.author.id,
				message,
			)

	async def close_poll_now(self, poll: Poll, message: Optional[Message] = None):
		"""Close a poll immediately.

		Args:
			poll (Poll): The poll to close.
			message (Optional[Message]): The message that triggered the poll to close. If omitted, it will be fetched from Discord's API.
		"""
		await poll.close()
		await self.__update_poll_message(poll, message)
		self.__closed_poll_count += 1
		await self.__set_presence()

	async def new_poll(
		self, params: PollCommandParams, author_id: int, message: Message
	):
		poll = await Poll.create_poll(params, author_id, message)
		self.__total_poll_count += 1
		await self.__update_poll_message(poll, message)
		await self.__set_presence()
		asyncio.create_task(self.__poll_close_task(poll))

	async def add_poll_option(
		self, poll: Poll, label: str, author_id: int, message: Optional[Message] = None
	):
		"""Add a new option to the given poll.

		Args:
			poll (Poll): The poll to add the option to.
			label (str): The label of the option.
			author_id (int): The ID of the user who added the option.
			message (Optional[Message], optional): The message containing the poll. If omitted, it will be fetched asynchronously.
		"""
		await poll.new_option(label, author_id)
		await self.__update_poll_message(poll, message)

	async def toggle_vote(self, option: Option, voter_id: int):
		"""Toggle a voter's vote for an option, removing the voter's vote from another option if necessary.

		Args:
			option (Option): The option to vote for.
			voter_id (int): The ID of the user who voted.
		"""
		await option.toggle_vote(voter_id)
		await self.__update_poll_message(option.poll)

	async def __load_polls(self):
		"""Fetch the polls from the database and set up the bot to react to poll interactions."""
		for poll in await Poll.fetch_polls():
			self.__total_poll_count += 1
			if poll.is_opened:
				asyncio.create_task(self.__poll_close_task(poll))
			else:
				self.__closed_poll_count += 1
			self.add_view(PollView(self, poll))
		logging.info(f"Finished loading {len(self.__polls)} polls.")

	async def __poll_close_task(self, poll: Poll, message: Optional[Message] = None):
		"""Close a poll at a specific time.

		This function blocks until the poll is closed if awaited, so you probably want to make it run in the background instead.

		Args:
			poll (Poll): The poll to close.
			message (Optional[Message]): The message that triggered the poll to close. If omitted, it will be fetched from Discord's API.
		"""
		if poll.expires is None:
			return
		await asyncio.sleep((self.expires - datetime.now(pytz.utc)).total_seconds())
		await self.close_poll_now(poll, message)

	async def __update_poll_message(
		self, poll: Poll, message: Optional[Message] = None
	):
		"""Update the poll's message. This should be called after a poll changes.

		Args:
			poll (Poll): The poll whose message should be updated.
			message (Optional[Message], optional): The message containing the poll. If omitted, it will be fetched asynchronously.
		"""
		try:
			message = message or await self.__get_poll_message(poll)
			await message.edit(
				embed=PollClosedEmbed(poll) if poll.is_expired else PollEmbed(poll),
				view=PollView(self, poll),
			)
		except Forbidden:
			pass

	async def __get_poll_message(self, poll: Poll) -> Message:
		return await self.get_partial_messageable(poll.channel_id).fetch_message(
			poll.message_id
		)

	async def __set_presence(self):
		active_polls = self.__total_poll_count - self.__closed_poll_count
		activity_name = (
			f"/poll. {active_polls} active, {self.__total_poll_count} total."
			f" ({len(self.guilds)} servers)"
		)
		if activity_name != self.__activity_name:
			activity = disnake.Activity(name=activity_name, type=ActivityType.listening)
			await self.change_presence(activity=activity)
			self.__activity_name = activity_name