import asyncio
from datetime import datetime
import os
from typing import Iterable, Optional
import asyncpg
import disnake
from disnake.ext.commands.params import Param
from disnake.enums import ActivityType
from disnake.interactions.application_command import GuildCommandInteraction
from disnake.interactions.base import Interaction
from friendly_error import FriendlyError
from paul import Paul
from poll.command import CommandParams, parse_expires, parse_options, poll_command
import logging

logging.basicConfig(level=logging.INFO)


async def main():
	# Connect to the database
	conn = await asyncpg.connect(os.getenv("DATABASE_URL", ""), ssl="require")

	activity = disnake.Activity(name="/poll", type=ActivityType.listening)

	# empty space effectively disables prefix since discord strips trailing spaces
	bot = Paul(conn, " ", activity=activity)

	@bot.event
	async def on_ready():
		print(f"{bot.user.name} has connected to Discord!")

	@bot.slash_command(desc="Create a poll", guild_ids=[805193644571099187])
	async def poll(
		inter: GuildCommandInteraction,
		question: str = Param(desc="Ask a question..."),
		options: Iterable[str] = Param(
			desc=(
				"Separate each option with a pipe (|). By default the options are yes"
				" or no."
			),
			converter=parse_options(sep="|"),
			default=("Yes", "No"),
		),
		expires: Optional[datetime] = Param(
			desc="When to stop accepting votes, e.g. 1h20m. Default is never.",
			converter=parse_expires,
			default=None,
		),
		allow_multiple_votes: bool = Param(
			desc="Can a user choose multiple options?", default=False
		),
	):
		await poll_command(
			bot, inter, CommandParams(question, options, expires, allow_multiple_votes)
		)

	@bot.event
	async def on_slash_command_error(inter: Interaction, error: Exception):
		if (original := getattr(error, "original", None)) and isinstance(
			original, FriendlyError
		):
			await original.send()
		else:
			logging.error(error)

	# Run Discord bot
	await bot.start(os.getenv("BOT_TOKEN", ""))


if __name__ == "__main__":
	asyncio.run(main())
