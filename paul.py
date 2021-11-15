from typing import Dict, Optional
import disnake
from disnake.enums import ActivityType
from disnake.errors import Forbidden
from disnake.ext.commands.bot import Bot
import asyncpg
import logging
from disnake.message import Message
from poll import Poll
from poll.command_params import PollCommandParams
from poll.ui.poll_view import PollView
from readable_mapping import ReadableDict, ReadableMapping


class Paul(Bot):
	def __init__(self, pool: asyncpg.Pool, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.pool = pool
		self.__polls: Dict[int, Poll] = {}
		self.__polls_readonly = ReadableDict(self.__polls)
		self.__closed_poll_count = 0
		self.__activity_name = ""

	async def load_polls(self):
		"""Fetch the polls from the database and set up the bot to react to poll interactions."""
		self.__polls.update(
			{poll.poll_id: poll for poll in await Poll.fetch_polls(self.pool)}
		)
		for poll in self.__polls.values():
			if poll.is_expired:
				self.__closed_poll_count += 1
				if poll.is_opened:
					await poll.close(self)
			else:
				poll.close_when_expired(self)
			self.add_view(PollView(self, poll))
		logging.info(f"Finished loading {len(self.__polls)} polls.")

	async def set_presence(self):
		total_polls = len(self.__polls)
		active_polls = total_polls - self.__closed_poll_count
		activity_name = f"/poll. {active_polls} active, {total_polls} total."
		if activity_name != self.__activity_name:
			activity = disnake.Activity(name=activity_name, type=ActivityType.listening)
			await self.change_presence(activity=activity)

	async def create_poll(
		self, params: PollCommandParams, author_id: int, message: Message
	):
		poll = await Poll.create_poll(params, author_id, message, self.pool)
		self.__add_polls(poll)
		await self.update_poll_message(poll, message)

	async def update_poll_message(self, poll: Poll, message: Optional[Message] = None):
		"""Update the poll's message. This should be called after a poll changes.

		Args:
			poll (Poll): The poll whose message should be updated.
			message (Optional[Message], optional): The message containing the poll. If omitted, it will be fetched asynchronously.
		"""
		try:
			message = message or await self.get_poll_message(poll)
			await message.edit(embed=poll.embed(), view=PollView(self, poll))
		except Forbidden:
			pass
		if poll.is_expired:
			self.__closed_poll_count += 1
		await self.set_presence()

	def __add_polls(self, *polls: Poll):
		self.__polls.update((poll.poll_id, poll) for poll in polls)

	async def get_poll_message(self, poll: Poll) -> Message:
		return await self.get_partial_messageable(poll.channel_id).fetch_message(
			poll.message_id
		)

	@property
	def polls(self) -> ReadableMapping[int, Poll]:
		return self.__polls_readonly