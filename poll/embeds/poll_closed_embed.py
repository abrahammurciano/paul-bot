from datetime import datetime
from typing import Generator, Iterable, Optional

import disnake
from mention import Mention, mentions_str
from poll.embeds.poll_embed import PollEmbed
from poll import Poll


class PollClosedEmbed(PollEmbed):
	def __init__(self, poll: Poll):
		super().__init__(poll)

	def option_prefixes(self) -> Generator[str, None, None]:
		most_votes = sorted({option.vote_count for option in self.poll.options})[:3]
		return (
			"🥇🥈🥉"[most_votes.index(option.vote_count)]
			if option.vote_count in most_votes
			else "🥔"
			for option in self.poll.options
		)

	def closing_text(self, expires: Optional[datetime]) -> str:
		assert (
			expires is not None
		), "Attempting to create an expired embed for a poll that doesn't expire"
		timestamp = disnake.utils.format_dt(expires, style="R")
		return f"⌛Poll closed {timestamp}."

	def voters_text(self, voters: Iterable[Mention]) -> str:
		return f"🗳️ {mentions_str(voters)} were allowed to vote."