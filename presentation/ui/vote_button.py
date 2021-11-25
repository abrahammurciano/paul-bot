from typing import TYPE_CHECKING
from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction
from mention import mentions_str
from poll.ui.poll_action_button import PollActionButton

if TYPE_CHECKING:
	from paul import Paul
	from poll.poll import Poll


class VoteButton(PollActionButton):
	def __init__(self, bot: "Paul", poll: "Poll", index: int):
		"""Construct a Button used to vote for an option.

		Args:
			bot (Paul): The bot instance.
			poll (Poll): The poll that this button belongs to.
			index (int): The index (starting from 0) of the option this button is for.
		"""
		option = poll.options[index]

		async def vote(inter: MessageInteraction):
			await option.toggle_vote(inter.author.id)
			await bot.update_poll_message(poll, inter.message)

		super().__init__(
			action=vote,
			allowed_clickers=poll.allowed_voters,
			style=ButtonStyle.blurple,
			label=(
				f"{str(index + 1)}."
				f" {option.label[:30]}{'...' if len(option.label) > 30 else ''}"
			),
			custom_id=str(option.option_id),
			emoji="🗳️",
			no_permission_message=(
				"You do not have permission to vote for this poll.\nThe allowed voters"
				f" are: {mentions_str(poll.allowed_voters)}"
			),
		)
