from typing import Set
from disnake.ext.commands.bot import Bot
import asyncpg
from poll import Poll


class Paul(Bot):
	def __init__(self, conn: asyncpg.Connection, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.conn = conn
		self.__polls: Set[Poll] = set()

	async def load_polls(self):
		"""Fetch the polls from the database."""
		self.__polls = await Poll.get_active_polls()

	@property
	def polls(self) -> Set[Poll]:
		return self.__polls.copy()