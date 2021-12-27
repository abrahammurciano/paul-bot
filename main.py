import asyncio
import os
import application
from presentation.paul import Paul
import logging
import tracemalloc

logging.basicConfig(
	format="%(asctime)s %(levelname)-8s %(message)s",
	level=logging.INFO,
	datefmt="%Y-%m-%d %H:%M:%S",
	handlers=[
		logging.FileHandler("ouput.log"),
		logging.StreamHandler()
	]
)
tracemalloc.start()


async def main():
	# Connect to the database
	await application.init()

	# empty space effectively disables prefix since discord strips trailing spaces
	bot = Paul(" ")

	# Run Discord bot
	await bot.start(os.getenv("BOT_TOKEN", ""))


if __name__ == "__main__":
	asyncio.run(main())
