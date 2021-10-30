from datetime import datetime
from typing import Generator, Iterable, Optional, Tuple
import disnake
from itertools import count
from mention import Mention
from poll import Poll
from .poll_embed_base import PollEmbedBase


class PollEmbed(PollEmbedBase):
	"""Base class for poll embeds."""

	def __init__(
		self,
		poll: Poll,
		*,
		vote_bar_background: str = "⬛",
		vote_bar_foregrounds: Tuple[str, ...] = ("🟨", "🟩", "🟥", "🟦", "🟪", "🟧"),
		vote_bar_length: int = 12,
	):
		"""Construct an Embed for the poll.

		Args:
			question (str): The question of the poll.
		"""
		super().__init__(poll.question)
		self.poll = poll
		self.__vote_bar_background = vote_bar_background
		self.__vote_bar_foregrounds = vote_bar_foregrounds
		self.__vote_bar_length = vote_bar_length
		self.add_options()
		self.add_details()

	@property
	def vote_bar_background(self) -> str:
		"""The emoji to use as the vote bar background."""
		return self.__vote_bar_background

	@property
	def vote_bar_foregrounds(self) -> Tuple[str, ...]:
		"""A tuple of emojis which can be used as the vote bar foreground."""
		return self.__vote_bar_foregrounds

	@property
	def vote_bar_length(self) -> int:
		"""The number of emojis to use for the vote bar."""
		return self.__vote_bar_length

	@property
	def details(self) -> Iterable[str]:
		"""A list of lines which will be shown at the bottom of the embed."""
		return (
			self.closing_text(self.poll.expires),
			# self.vote_viewers_text(self.poll.allowed_vote_viewers),
		)

	@property
	def option_prefixes(self) -> Generator[str, None, None]:
		return (f"{i}." for i in count(start=1))

	def add_options(self):
		for i, option in enumerate(self.poll.options):
			self.add_field(
				name=f"{next(self.option_prefixes)} {option.label}",
				value=self.vote_bar(i, option.vote_count, self.poll.vote_count),
				inline=False,
			)

	def vote_bar(
		self,
		index: int,
		option_votes: int,
		total_votes: int,
		author_id: Optional[int] = None,
	) -> str:
		"""Get the string which will show statistics for the votes for one particular option.

		Args:
			index (int): The index of the option starting from 0.
			option_votes (int): The number of votes for the option.
			total_votes (int): The total number of votes for the poll.
			author_id (Optional[int], optional): The ID of the user who added the option, or None if the option existed since the poll's creation. Default is None.

		Returns:
			str: A string showing statistics for the votes for one option.
		"""
		added_by = f"*Added by <@{author_id}>*\n" if author_id is not None else ""
		proportion = option_votes / total_votes if total_votes > 0 else 0
		squares = round(self.vote_bar_length * proportion)
		bar = self.vote_bar_foregrounds[
			index % len(self.vote_bar_foregrounds)
		] * squares + self.vote_bar_background * (self.vote_bar_length - squares)
		return f"{added_by}{bar}`{round(proportion*100)}% ({option_votes})`"

	def add_details(self):
		"""Add poll details to the end of the embed."""
		if self.details:
			self.add_field(name="---", value="\n".join(self.details), inline=False)

	def closing_text(self, expires: Optional[datetime]) -> str:
		"""Some text describing when the poll will expire.

		Args:
			expires (Optional[datetime]): The time when the poll will expire. If None, the poll does not expire.

		Returns:
			str: A string describing when the poll will expire.
		"""
		if expires is None:
			return "♾️This poll will never expire."
		timestamp = disnake.utils.format_dt(expires, style="R")
		return f"⏳Poll closes {timestamp}."

	def vote_viewers_text(self, viewers: Iterable[Mention]) -> str:
		return (
			"Your vote can be seen by"
			f" {', '.join(str(mention) for mention in viewers)}."
			if viewers
			else "No one can see your vote."
		)
