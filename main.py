import asyncio
import os
import application
from presentation.paul import Paul
from presentation.discord_channel_handler import DiscordChannelHandler
import logging
import tracemalloc

# empty space effectively disables prefix since discord strips trailing spaces
bot = Paul(" ")

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("ouput.log"),
        logging.StreamHandler(),
        DiscordChannelHandler(bot, int(os.getenv("LOG_CHANNEL", ""))),
    ],
)
tracemalloc.start()


async def main():
    # Connect to the database
    await application.init()

    # Run Discord bot
    await bot.start(os.getenv("BOT_TOKEN", ""))


if __name__ == "__main__":
    asyncio.run(main())
