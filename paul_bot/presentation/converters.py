from typing import Callable, List
from disnake.interactions import ApplicationCommandInteraction as Interaction
import pytz
from datetime import datetime
import dateparser
import re
import logging
from .errors import FriendlyError
from ..application.mention import Mention

logger = logging.getLogger(__name__)


def parse_options(sep: str = "|") -> Callable[[Interaction, str], List[str]]:
	def converter(inter: Interaction, options: str) -> List[str]:
		result = [option.strip() for option in options.split(sep) if option]
		if len(result) > 23:
			raise FriendlyError(
				f'Too many options. Maximum is 23.\nOptions: "{result}"',
				inter.response,
			)
		for option in result:
			if len(option) > 254:
				raise FriendlyError(
					f'Option "{option}" is too long. Maximum is 254 characters.',
					inter.response,
				)
		if not result:
			logger.warning(
				f'Unable to parse any options out of the input string "{options}".'
				"Using default Yes/No options instead."
			)
			return ["Yes", "No"]
		return result

	return converter


RELATIVE_DATE_PARSE_FIX = re.compile(r"([dhms])(\d)")


def parse_expires(inter: Interaction, expires: str) -> datetime:
	# Workaround for https://github.com/scrapinghub/dateparser/issues/1012
	expires = RELATIVE_DATE_PARSE_FIX.sub(r"\1 \2", expires)
	result = dateparser.parse(
		expires,
		settings={
			"PREFER_DATES_FROM": "future",
			"RETURN_AS_TIMEZONE_AWARE": True,
			"TO_TIMEZONE": "UTC",
			"TIMEZONE": "UTC",
		},
	)
	if result is None:
		raise FriendlyError(
			f'Could not parse "{expires}" as a date/time.', inter.response
		)
	return (
		result.replace(tzinfo=pytz.utc)
		if result.tzinfo is None or result.tzinfo.utcoffset(result) is None
		else result
	)


MENTION_REGEX = re.compile(r"<(@[!&])?(\d+)>")


def parse_mentions(inter: Interaction, string: str) -> List[Mention]:
	string = (
		string.replace("@everyone", f"<@&{inter.guild.default_role.id}>")
		if inter.guild
		else string
	)
	return [Mention(tup[0], int(tup[1])) for tup in MENTION_REGEX.findall(string)]


def length_bound_str(max: int, min: int = 0):
	def converter(inter: Interaction, string: str) -> str:
		if len(string) > max or len(string) < min:
			raise FriendlyError(
				f"Expected a string of length between {min} and {max}"
				f' characters.\nInstead got "{string}" which is {len(string)}'
				" characters.",
				inter.response,
			)
		return string

	return converter
