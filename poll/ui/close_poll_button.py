from typing import TYPE_CHECKING
from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction
from mention import Mention
from .poll_action_button import PollActionButton

if TYPE_CHECKING:
	from poll.poll import Poll
	from paul import Paul


class ClosePollButton(PollActionButton):
	def __init__(self, bot: "Paul", poll: "Poll"):
		async def close_poll(_: MessageInteraction):
			await poll.close(bot)

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
