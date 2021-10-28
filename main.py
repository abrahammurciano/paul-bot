import asyncio
from datetime import datetime, timedelta
import os
from typing import Iterable, List
import asyncpg
import disnake
from disnake.ext.commands.params import Param
from disnake.enums import ActivityType
from disnake.interactions.application_command import (
	ApplicationCommandInteraction,
	GuildCommandInteraction,
)
from paul import Paul
from poll import Poll, poll_embeds


async def main():
	# Connect to the database
	conn = await asyncpg.connect(os.getenv("DATABASE_URL", ""), ssl="require")

	activity = disnake.Activity(name="/poll", type=ActivityType.listening)

	# empty space effectively disables prefix since discord strips trailing spaces
	bot = Paul(conn, " ", activity=activity)

	@bot.event
	async def on_ready():
		print(f"{bot.user.name} has connected to Discord!")

	def parse_options(inter: ApplicationCommandInteraction, options: str) -> List[str]:
		return [option.strip() for option in options.split("|")]

	@bot.slash_command(description="Create a poll", guild_ids=[805193644571099187])
	async def poll(
		inter: GuildCommandInteraction,
		question: str = Param(description="Ask a question..."),
		options: Iterable[str] = Param(
			description=(
				"Separate each option with a pipe (|). By default the options are yes"
				" or no."
			),
			converter=parse_options,
		),
	):
		await inter.response.send_message(embed=poll_embeds.initial_embed(question))
		message = await inter.original_message()
		poll = await Poll.create_poll(
			bot.conn,
			question,
			options,
			message,
			inter.author,
			expires=datetime.now() + timedelta(minutes=2),
		)
		await message.edit(embed=poll_embeds.embed(poll))

	# Run Discord bot
	await bot.start(os.getenv("BOT_TOKEN", ""))


if __name__ == "__main__":
	asyncio.run(main())
