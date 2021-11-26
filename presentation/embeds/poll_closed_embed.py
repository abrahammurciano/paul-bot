from datetime import datetime
from typing import TYPE_CHECKING, Generator, Iterable, Optional
import disnake
from application.mention import Mention, mentions_str
from presentation.embeds.poll_embed import PollEmbed

if TYPE_CHECKING:
	from application.poll import Poll


class PollClosedEmbed(PollEmbed):
	def __init__(self, poll: "Poll"):
		super().__init__(poll)

	def option_prefixes(self) -> Generator[str, None, None]:
		most_votes = sorted(
			{option.vote_count for option in self.poll.options}, reverse=True
		)[:3]
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
		return f"🗳️ {mentions_str(voters)} was allowed to vote."

	def multiple_votes_text(self, allow_multiple_votes: bool) -> Optional[str]:
		return (
			"🔢 Multiple options were allowed to be chosen."
			if self.poll.allow_multiple_votes
			else None
		)
