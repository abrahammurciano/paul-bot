import disnake
import asyncpg


class DatabaseBot(disnake.Bot):
	def __init__(self, conn: asyncpg.Connection, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.conn = conn