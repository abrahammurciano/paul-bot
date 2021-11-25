import asyncio
from datetime import datetime
import os
from typing import Iterable, List, Optional
import asyncpg
import disnake
from disnake.ext.commands.params import Param
from disnake.enums import ActivityType
from disnake.interactions.application_command import GuildCommandInteraction
from disnake.interactions.base import Interaction
from errors import handle_error
from paul import Paul
from poll.command_params import PollCommandParams
from poll.converters import Mention, parse_expires, parse_mentions, parse_options
from poll.embeds import PollEmbedBase
import logging
import tracemalloc

import sql

logging.basicConfig(
	format="%(asctime)s %(levelname)-8s %(message)s",
	level=logging.INFO,
	datefmt="%Y-%m-%d %H:%M:%S",
)
tracemalloc.start()

bot_ready_triggered = False


async def main():
	# Connect to the database
	pool: asyncpg.Pool = await asyncpg.create_pool(
		os.getenv("HEROKU_POSTGRESQL_AQUA_URL", ""), ssl="require", min_size=5
	)

	# empty space effectively disables prefix since discord strips trailing spaces
	bot = Paul(pool, " ")

	@bot.event
	async def on_ready():
		global bot_ready_triggered
		if not bot_ready_triggered:
			print(f"\n{bot.user.name} has connected to Discord!\n")
			await bot.load_polls()
			await bot.set_presence()
			bot_ready_triggered = True

	@bot.slash_command(desc="Create a poll")
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
			desc="Mention members or roles who can view the votes. Default is no one.",
			default=[],
			converter=parse_mentions,
		),
		allowed_editors: List[Mention] = Param(
			desc=(
				"Mention members or roles who may add options to the poll. Default is"
				" only you."
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
		await bot.create_poll(
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

	@bot.event
	async def on_slash_command_error(inter: Interaction, error: Exception):
		await handle_error(error)

	# Run Discord bot
	await bot.start(os.getenv("BOT_TOKEN", ""))


if __name__ == "__main__":
	asyncio.run(main())
