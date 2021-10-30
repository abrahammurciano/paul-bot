from datetime import datetime, timedelta
import disnake
from disnake.enums import ButtonStyle
from disnake.ui.button import Button
from poll import Poll


class VoteView(disnake.ui.View):
	def __init__(self, poll: Poll):
		super().__init__(
			timeout=(poll.expires - datetime.now()).total_seconds()
			if poll.expires
			else None
		)
		for index, option in enumerate(poll.options, start=1):
			self.add_item(Button(style=ButtonStyle.blurple, label=str(index)))
