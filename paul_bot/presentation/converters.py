import logging
import re
from datetime import UTC, datetime
from typing import Callable

import dateparser
from disnake.interactions import ApplicationCommandInteraction as Interaction

from ..application import Mention, Poll
from .errors import FriendlyError

logger = logging.getLogger(__name__)


def parse_options(sep: str = "|") -> Callable[[Interaction, str], list[str]]:
    def converter(inter: Interaction, options: str) -> list[str]:
        result = [option.strip() for option in options.split(sep) if option]
        if len(result) > Poll.MAX_OPTIONS:
            raise FriendlyError(
                f'Too many options. Maximum is {Poll.MAX_OPTIONS}.\nOptions: "{result}"',
                inter,
            )
        for option in result:
            if len(option) > Poll.MAX_OPTION_LENGTH:
                raise FriendlyError(
                    f'Option "{option}" is too long. Maximum is {Poll.MAX_OPTION_LENGTH} characters.',
                    inter,
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


def parse_expires(inter: Interaction, expires: str) -> datetime | None:
    # Workaround for https://github.com/scrapinghub/dateparser/issues/1012
    if expires.lower() == "never":
        return None
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
        raise FriendlyError(f'Could not parse "{expires}" as a date/time.', inter)
    return (
        result.replace(tzinfo=UTC)
        if result.tzinfo is None or result.tzinfo.utcoffset(result) is None
        else result
    )


_MENTION_REGEX = re.compile(r"<(@[!&])?(\d+)>")
_NAMED_MENTION_REGEX = re.compile(r"@[^!&@,\s][^\s,@<]*")


def parse_mentions(inter: Interaction, string: str) -> list[Mention]:
    result = []
    result.extend(
        Mention(prefix, int(mention_id))
        for prefix, mention_id in _MENTION_REGEX.findall(string)
    )
    if inter.guild:
        result.extend(
            mention
            for name in _NAMED_MENTION_REGEX.findall(string)
            if (mention := Mention.named(name, inter.guild))
        )
    return result


def length_bound_str(max: int, min: int = 0) -> Callable[[Interaction, str], str]:
    def converter(inter: Interaction, string: str) -> str:
        if len(string) > max or len(string) < min:
            raise FriendlyError(
                f"Expected a string of length between {min} and {max}"
                f' characters.\nInstead got "{string}" which is {len(string)}'
                " characters.",
                inter,
            )
        return string

    return converter
