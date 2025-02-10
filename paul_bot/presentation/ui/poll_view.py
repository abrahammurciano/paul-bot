from typing import TYPE_CHECKING

from ...application.poll import Poll
from ..errors import ErrorHandlingView
from .add_option_button import AddOptionButton
from .close_poll_button import ClosePollButton
from .see_votes_button import SeeVotesButton
from .vote_button import VoteButton

if TYPE_CHECKING:
    from paul_bot import Paul


class PollView(ErrorHandlingView):
    def __init__(self, bot: "Paul", poll: Poll) -> None:
        super().__init__(timeout=None)
        self.__add_vote_buttons(poll, bot)
        self.__add_add_option_button(poll, bot)
        self.__add_see_vote_button(poll)
        self.__add_close_poll_button(poll, bot)

    def __add_vote_buttons(self, poll: Poll, bot: "Paul") -> None:
        if not poll.is_expired:
            for option in poll.options:
                self.add_item(VoteButton(bot, option))

    def __add_add_option_button(self, poll: Poll, bot: "Paul") -> None:
        if (
            not poll.is_expired
            and poll.allowed_editors
            and len(poll.options) < Poll.MAX_OPTIONS
        ):
            self.add_item(AddOptionButton(bot, poll))

    def __add_see_vote_button(self, poll: Poll) -> None:
        if poll.allowed_vote_viewers:
            self.add_item(SeeVotesButton(poll))

    def __add_close_poll_button(self, poll: Poll, bot: "Paul") -> None:
        if not poll.is_expired:
            self.add_item(ClosePollButton(bot, poll))
