from typing import Callable, Iterable, List, Optional
from disnake.interactions.base import Interaction
from friendly_error import FriendlyError
from paul import Paul
from datetime import datetime
from typing import Iterable, List
from paul import Paul
from poll import Poll, PollEmbed
from dataclasses import dataclass
import dateparser
import re


@dataclass
class CommandParams:
	question: str
	options: Iterable[str]
	expires: Optional[datetime]
	allow_multiple_votes: bool


async def poll_command(bot: Paul, inter: Interaction, params: CommandParams):
	await send_poll_message(bot, inter, params)


async def send_poll_message(bot: Paul, inter: Interaction, params: CommandParams):
	await inter.response.send_message(embed=PollEmbed(params.question))
	message = await inter.original_message()
	poll = await Poll.create_poll(
		bot.conn, params.question, params.options, message, inter.author, params.expires
	)
	await message.edit(embed=PollEmbed(poll))


def parse_options(sep: str = "|") -> Callable[[Interaction, str], List[str]]:
	def converter(inter: Interaction, options: str) -> List[str]:
		return [option.strip() for option in options.split(sep)]

	return converter


REGEX = re.compile(r"([dhms])(\d)")


def parse_expires(inter: Interaction, expires: str) -> datetime:
	# Workaround for https://github.com/scrapinghub/dateparser/issues/1012
	expires = REGEX.sub(r"\1 \2", expires)
	result = dateparser.parse(expires, settings={"PREFER_DATES_FROM": "future"})
	if result is None:
		raise FriendlyError(
			f'Could not parse "{expires}" as a date/time.', inter.response
		)
	return result