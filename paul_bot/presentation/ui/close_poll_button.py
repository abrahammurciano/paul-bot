from typing import TYPE_CHECKING
from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction
from .poll_action_button import PollActionButton
from ...application.poll import Poll
from ...application.mention import Mention

if TYPE_CHECKING:
	from paul_bot import Paul


class ClosePollButton(PollActionButton):
	def __init__(self, bot: "Paul", poll: Poll):
		async def close_poll(inter: MessageInteraction):
			await bot.close_poll_now(poll)
			await inter.response.defer()

		author_mention = Mention("@", poll.author_id)
		super().__init__(
			action=close_poll,
			allowed_clickers=(author_mention,),
			style=ButtonStyle.red,
			label="Close Poll",
			custom_id=f"{poll.poll_id} close",
			row=4,
			no_permission_message=(
				f"You do not have permission to close the poll. Only {author_mention}"
				" may do that."
			),
		)
