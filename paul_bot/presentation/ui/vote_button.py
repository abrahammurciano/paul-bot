from typing import TYPE_CHECKING
from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction
from .poll_action_button import PollActionButton
from ...application.mention import mentions_str
from ...application.option import Option

if TYPE_CHECKING:
	from paul_bot import Paul


class VoteButton(PollActionButton):
	def __init__(self, bot: "Paul", option: Option):
		"""Construct a Button used to vote for an option.

		Args:
			bot (Paul): The bot instance.
			option (Option): The option to vote for when this button is pressed.
		"""

		async def vote(inter: MessageInteraction):
			await bot.toggle_vote(option, inter.author.id)

		super().__init__(
			action=vote,
			allowed_clickers=option.poll.allowed_voters,
			style=ButtonStyle.blurple,
			label=(
				f"{str(option.index + 1)}."
				f" {option.label[:30]}{'...' if len(option.label) > 30 else ''}"
			),
			custom_id=str(option.option_id),
			emoji="🗳️",
			no_permission_message=(
				"You do not have permission to vote for this poll.\nThe allowed voters"
				f" are: {mentions_str(option.poll.allowed_voters)}"
			),
		)
