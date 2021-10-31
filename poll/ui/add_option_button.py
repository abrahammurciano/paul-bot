from typing import TYPE_CHECKING, Type
import disnake
from disnake import utils
from disnake.emoji import Emoji
from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction
from mention import mentions_str
from poll.embeds.poll_embed import PollEmbed
from poll.poll import Poll
from poll.ui.poll_action_button import PollActionButton
from poll.ui.util import get_text_input

if TYPE_CHECKING:
	from poll.ui.poll_view import PollView


class AddOptionButton(PollActionButton):
	def __init__(self, poll: Poll, client: disnake.Client, view_cls: Type["PollView"]):
		"""Construct a Button used to vote for an option.

		Args:
			poll (Poll): The poll that this button belongs to.
		"""

		async def add_option(inter: MessageInteraction):
			if reply := await get_text_input(
				f"**What option do you want to add?** *(You have one minute to reply)*",
				inter,
				client,
				60.0,
			):
				await poll.add_option(reply.content, inter.author.id)
				await inter.message.edit(
					embed=PollEmbed(poll), view=view_cls(poll, client)
				)
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
