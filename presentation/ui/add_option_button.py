from typing import TYPE_CHECKING
from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction
from mention import mentions_str
from poll.ui.poll_action_button import PollActionButton
from poll.ui.util import get_text_input

if TYPE_CHECKING:
	from poll.poll import Poll
	from paul import Paul


class AddOptionButton(PollActionButton):
	def __init__(self, bot: "Paul", poll: "Poll"):
		"""Construct a Button used to vote for an option.

		Args:
			bot (Paul): The bot instance.
			poll (Poll): The poll to add options to when this button gets clicked.
		"""

		async def add_option(inter: MessageInteraction):
			if reply := await get_text_input(
				f"**What option do you want to add?** *(You have one minute to reply)*",
				inter,
				bot,
				60.0,
			):
				await poll.new_option(reply.content, inter.author.id)
				await bot.update_poll_message(poll, inter.message)
				await reply.add_reaction("✅")

		super().__init__(
			action=add_option,
			allowed_clickers=poll.allowed_editors,
			style=ButtonStyle.grey,
			label="Add Option",
			custom_id=f"{poll.poll_id} add_option",
			emoji="📝",
			row=4,
			no_permission_message=(
				"You do not have permission to add options to this poll.\nThe allowed"
				f" editors are: {mentions_str(poll.allowed_editors)}"
			),
		)
