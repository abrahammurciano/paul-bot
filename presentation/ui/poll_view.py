from typing import TYPE_CHECKING
from application.poll import Poll
from presentation.errors import ErrorHandlingView
from presentation.ui.add_option_button import AddOptionButton
from presentation.ui.close_poll_button import ClosePollButton
from presentation.ui.see_votes_button import SeeVotesButton
from presentation.ui.vote_button import VoteButton

if TYPE_CHECKING:
	from paul import Paul


class PollView(ErrorHandlingView):
	def __init__(self, bot: "Paul", poll: Poll):
		super().__init__(timeout=None)
		self.__bot = bot
		self.__poll = poll
		self.__add_vote_buttons()
		self.__add_add_option_button()
		self.__add_see_vote_button()
		self.__add_close_poll_button()

	def __add_vote_buttons(self):
		if not self.__poll.is_expired:
			for option in self.__poll.options:
				self.add_item(VoteButton(self.__bot, option))

	def __add_add_option_button(self):
		if (
			not self.__poll.is_expired
			and self.__poll.allowed_editors
			and len(self.__poll.options) < 23
		):
			self.add_item(AddOptionButton(self.__bot, self.__poll))

	def __add_see_vote_button(self):
		if self.__poll.allowed_vote_viewers:
			self.add_item(SeeVotesButton(self.__poll))

	def __add_close_poll_button(self):
		if not self.__poll.is_expired:
			self.add_item(ClosePollButton(self.__bot, self.__poll))
