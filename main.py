import asyncio
import os
import application
from presentation.paul import Paul
from discord_lumberjack.handlers import DiscordChannelHandler
from discord_lumberjack.message_creators import EmbedMessageCreator
import logging
from dotenv import load_dotenv

load_dotenv()
token = os.environ["BOT_TOKEN"]

logger = logging.getLogger("paul")
logger.setLevel(logging.DEBUG)
stderr_handler = logging.StreamHandler()
stderr_handler.setLevel(logging.INFO)
logger.addHandler(stderr_handler)
file_handler = logging.FileHandler("output.log")
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(
	DiscordChannelHandler(
		token, int(os.environ["ERR_CHANNEL"]), logging.ERROR, EmbedMessageCreator()
	)
)
logger.addHandler(
	DiscordChannelHandler(
		token, int(os.environ["DBG_CHANNEL"]), logging.DEBUG, EmbedMessageCreator()
	)
)


async def main():
	logger.info("Starting Paul...")

	# Connect to the database
	await application.init()

	# empty space effectively disables prefix since discord strips trailing spaces
	bot = Paul(" ")

	# Run Discord bot
	await bot.start(token)


if __name__ == "__main__":
	asyncio.run(main())
