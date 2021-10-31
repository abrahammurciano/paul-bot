from typing import Set
from disnake.ext.commands.bot import Bot
import asyncpg
from poll import Poll
from poll.ui.poll_view import PollView


class Paul(Bot):
	def __init__(self, pool: asyncpg.Pool, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.pool = pool
		self.__polls: Set[Poll] = set()

	async def load_polls(self):
		"""Fetch the polls from the database."""
		self.__polls = await Poll.get_active_polls(self.pool)
		for poll in self.__polls:
			self.add_view(PollView(poll, self))

	@property
	def polls(self) -> Set[Poll]:
		return self.__polls.copy()