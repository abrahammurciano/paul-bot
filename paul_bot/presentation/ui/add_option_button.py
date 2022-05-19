import logging
from typing import TYPE_CHECKING, Set
from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction
from disnake.errors import Forbidden
from .poll_action_button import PollActionButton
from .util import get_text_input
from ...application.mention import mentions_str
from ...application.poll import Poll

if TYPE_CHECKING:
	from paul_bot import Paul

logger = logging.getLogger(__name__)


class AddOptionButton(PollActionButton):
	def __init__(self, bot: "Paul", poll: Poll):
		"""Construct a Button used to vote for an option.

		Args:
			bot (Paul): The bot instance.
			poll (Poll): The poll to add options to when this button gets clicked.
		"""

		users_using_button: Set[int] = set()

		async def add_option(inter: MessageInteraction):
			if inter.author.id in users_using_button:
				return
			users_using_button.add(inter.author.id)

			logger.debug(
				f"{inter.author.display_name} wants to add an option to poll"
				f" {poll.question}."
			)
			if reply := await get_text_input(
				f"**What option do you want to add?** *(You have one minute to reply)*",
				inter,
				bot,
				60.0,
			):
				users_using_button.discard(inter.author.id)
				await bot.add_poll_option(
					poll, reply.content, inter.author.id, inter.message
				)
				try:
					await reply.add_reaction("✅")
				except Forbidden:
					pass

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
