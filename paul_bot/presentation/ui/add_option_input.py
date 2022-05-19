import logging
from typing import TYPE_CHECKING, Set
from disnake.ui import TextInput
from disnake.enums import TextInputStyle
from disnake.interactions.message import MessageInteraction
from disnake.errors import Forbidden
from .poll_action_button import PollActionButton
from .util import get_text_input
from ...application.mention import mentions_str
from ...application.poll import Poll

if TYPE_CHECKING:
	from paul_bot import Paul

logger = logging.getLogger(__name__)


class AddOptionInput(TextInput):
	def __init__(self, bot: "Paul", poll: Poll):
		# await bot.add_poll_option(
		# 			poll, reply.content, inter.author.id, inter.message
		# 		)

		super().__init__(
			action=add_option,
			allowed_clickers=poll.allowed_editors,
			style=TextInputStyle.,
			label="Add option",
			custom_id=f"{poll.poll_id} add_option",
			emoji="📝",
			row=4,
			no_permission_message=(
				"You do not have permission to add options to this poll.\nThe allowed"
				f" editors are: {mentions_str(poll.allowed_editors)}"
			),
		)
