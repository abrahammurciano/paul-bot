from disnake import Client
from errors import ErrorHandlingView
from poll import Poll
from poll.ui.add_option_button import AddOptionButton
from poll.ui.vote_button import VoteButton


class PollView(ErrorHandlingView):
	def __init__(self, poll: Poll, client: Client):
		super().__init__(timeout=None)
		for index in range(len(poll.options)):
			self.add_item(VoteButton(poll, index))
		self.add_item(AddOptionButton(poll, client, PollView))