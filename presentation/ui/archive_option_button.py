import logging
from typing import TYPE_CHECKING
from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction
from application.mention import mentions_str
from application.poll import Poll
from presentation.ui.poll_action_button import PollActionButton
from presentation.ui.util import get_text_input

if TYPE_CHECKING:
	from paul import Paul

logger = logging.getLogger(f"paul.{__name__}")


class ArchiveOptionButton(PollActionButton):
	def __init__(self, bot: "Paul", poll: Poll):
		"""Construct a Button used to archive an option.

		Args:
			bot (Paul): The bot instance.
			poll (Poll): The poll to archive option in when this button gets clicked.
		"""

		async def archive_option(inter: MessageInteraction):
			logger.debug(
				f"{inter.author.display_name} wants to archive an option, removing it from poll"
				f" {poll.question}."
			)
			if reply := await get_text_input(
				f"**What is the number of the option you want to archive?** *(You have one minute to reply)*",
				inter,
				bot,
				60.0,
			):
				try:
					await bot.archive_poll_option(
						poll, int(reply.content)-1, inter.message
					)
					await reply.add_reaction("✅")
				except ValueError as e:
					await reply.add_reaction("❗")

		super().__init__(
			action=archive_option,
			allowed_clickers=poll.allowed_editors,
			style=ButtonStyle.red,
			label="Archive Option",
			custom_id=f"{poll.poll_id} archive_option",
			emoji="📝",
			row=4,
			no_permission_message=(
				"You do not have permission to archive options in this poll.\nThe allowed"
				f" editors are: {mentions_str(poll.allowed_editors)}"
			),
		)
