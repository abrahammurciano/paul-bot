from datetime import datetime
from typing import Optional, Union, overload
import disnake
from disnake import utils
from poll import Poll
from poll.option import Option


class PollEmbed(disnake.Embed):
	@overload
	def __init__(self, question: str, /):
		...

	@overload
	def __init__(self, poll: Poll, /):
		...

	def __init__(self, arg: Union[str, Poll], /):
		self.__colour = 0x6F85D5
		self.__bar_emojis = "🟨🟩🟥🟦🟪🟧"
		self.__background = "⬛"
		self.__bar_length = 12

		if isinstance(arg, str):
			super().__init__(
				title=f"📊 {arg}", colour=self.__colour, description="Loading options..."
			)
		else:
			poll = arg
			super().__init__(title=f"📊 {poll.question}", colour=self.__colour)
			self.__add_options(poll)
			self.add_field(
				name="---", value=self.__closing_text(poll.expires), inline=False
			)

	def __add_options(self, poll: Poll):
		for i, option in enumerate(poll.options, start=1):
			self.add_field(
				name=f"{i}. {option.label}",
				value=self.__option_body(i - 1, option, poll.vote_count),
				inline=False,
			)

	def __option_body(self, index: int, option: Option, total_votes: int) -> str:
		added_by = f"*Added by <@{option.author}>*\n" if option.author else ""
		proportion = option.vote_count / total_votes if total_votes > 0 else 0
		squares = round(self.__bar_length * proportion)
		bar = self.__bar_emojis[
			index % len(self.__bar_emojis)
		] * squares + self.__background * (self.__bar_length - squares)
		return f"{added_by}{bar}`{round(proportion*100)}% ({option.vote_count})`"

	def __closing_text(self, expiry: Optional[datetime]) -> str:
		if expiry is None:
			return "This poll does not expire."
		return (
			f"Poll close{'d' if expiry < datetime.now() else 's'}"
			f" {utils.format_dt(expiry, style='R')}."
		)