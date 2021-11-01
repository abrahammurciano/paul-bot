from typing import TYPE_CHECKING
from errors import ErrorHandlingView
from poll.ui.add_option_button import AddOptionButton
from poll.ui.close_poll_button import ClosePollButton
from poll.ui.vote_button import VoteButton

if TYPE_CHECKING:
	from poll.poll import Poll
	from paul import Paul


class PollView(ErrorHandlingView):
	def __init__(self, bot: "Paul", poll: "Poll"):
		super().__init__(timeout=None)
		if poll.is_active:
			for index in range(len(poll.options)):
				self.add_item(VoteButton(bot, poll, index))
			self.add_item(AddOptionButton(bot, poll))
			self.add_item(ClosePollButton(bot, poll))