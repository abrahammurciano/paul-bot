from collections.abc import Generator, Iterable
from datetime import datetime
from typing import TYPE_CHECKING, override

import disnake

from paul_bot.application.mention import Mention, mentions_str
from paul_bot.presentation.embeds.poll_embed import PollEmbed

if TYPE_CHECKING:
    from paul_bot.application.poll import Poll


class PollClosedEmbed(PollEmbed):
    def __init__(self, poll: Poll) -> None:
        super().__init__(poll)

    @override
    def option_prefixes(self) -> Generator[str]:
        most_votes = sorted(
            {option.vote_count for option in self.poll.options}, reverse=True
        )[:3]
        return (
            (
                "🥇🥈🥉"[most_votes.index(option.vote_count)]
                if option.vote_count in most_votes
                else "🥔"
            )
            for option in self.poll.options
        )

    @override
    def closing_text(self, expires: datetime | None) -> str:
        assert expires is not None, (
            "Attempting to create an expired embed for a poll that doesn't expire"
        )
        timestamp = disnake.utils.format_dt(expires, style="R")
        return f"⌛Poll closed {timestamp}."

    @override
    def voters_text(self, voters: Iterable[Mention]) -> str:
        return f"🗳️ {mentions_str(voters)} was allowed to vote."

    @override
    def multiple_votes_text(self, allow_multiple_votes: bool) -> str | None:
        return (
            "🔢 Multiple options were allowed to be chosen."
            if self.poll.allow_multiple_votes
            else None
        )
