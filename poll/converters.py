from typing import Callable, List
from disnake.interactions.base import Interaction
from errors import FriendlyError
from datetime import datetime
import dateparser
import re
from mention import Mention


def parse_options(sep: str = "|") -> Callable[[Interaction, str], List[str]]:
	def converter(inter: Interaction, options: str) -> List[str]:
		return [option.strip() for option in options.split(sep)]

	return converter


RELATIVE_DATE_PARSE_FIX = re.compile(r"([dhms])(\d)")


def parse_expires(inter: Interaction, expires: str) -> datetime:
	# Workaround for https://github.com/scrapinghub/dateparser/issues/1012
	expires = RELATIVE_DATE_PARSE_FIX.sub(r"\1 \2", expires)
	result = dateparser.parse(expires, settings={"PREFER_DATES_FROM": "future"})
	if result is None:
		raise FriendlyError(
			f'Could not parse "{expires}" as a date/time.', inter.response
		)
	return result


MENTION_REGEX = re.compile(r"<(@[!&])?(\d+)>")


def parse_mentions(inter: Interaction, string: str) -> List[Mention]:
	return [Mention(tup[0], int(tup[1])) for tup in MENTION_REGEX.findall(string)]