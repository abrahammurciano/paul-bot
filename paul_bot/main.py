import asyncio
import os
import logging
from discord_lumberjack.handlers import DiscordChannelHandler
from dotenv import load_dotenv
from . import application
from .presentation.paul import Paul
from .utils import EmbedLongMessageCreator

load_dotenv()
token = os.environ["BOT_TOKEN"]

logger = logging.getLogger("paul_bot")
logger.setLevel(logging.DEBUG)
stderr_handler = logging.StreamHandler()
stderr_handler.setLevel(logging.INFO)
logger.addHandler(stderr_handler)
file_handler = logging.FileHandler("output.log")
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
if err_channel := os.environ.get("ERR_CHANNEL"):
    logger.addHandler(
        DiscordChannelHandler(
            token, int(err_channel), logging.ERROR, EmbedLongMessageCreator()
        )
    )
if dbg_channel := os.environ.get("DBG_CHANNEL"):
    logger.addHandler(
        DiscordChannelHandler(
            token, int(dbg_channel), logging.DEBUG, EmbedLongMessageCreator()
        )
    )


async def main():
    logger.info("Starting Paul...")

    # Connect to the database
    await application.init()

    # empty space effectively disables prefix since discord strips trailing spaces
    bot = Paul()

    # Run Discord bot
    await bot.start(token)


def _main():
    asyncio.run(main())


if __name__ == "__main__":
    _main()
