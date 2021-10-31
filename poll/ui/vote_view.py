import asyncpg
from errors import ErrorHandlingView
from poll import Poll
from poll.ui.vote_button import VoteButton


class VoteView(ErrorHandlingView):
	def __init__(self, poll: Poll, conn: asyncpg.Connection):
		super().__init__(timeout=None)
		for index in range(len(poll.options)):
			self.add_item(VoteButton(poll, index, conn))