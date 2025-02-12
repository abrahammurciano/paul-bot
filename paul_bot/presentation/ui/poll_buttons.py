from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Sequence, override

from disnake.ui import Button

from paul_bot.application.poll import Poll

from .buttons.add_option_button import AddOptionButton
from .buttons.close_poll_button import ClosePollButton
from .buttons.see_votes_button import SeeVotesButton
from .buttons.vote_button import VoteButton

if TYPE_CHECKING:
    from paul_bot import Paul


class PollButtons(Sequence[Button]):
    def __init__(self, bot: "Paul", poll: Poll) -> None:
        self.__buttons = []
        self.__add_vote_buttons(poll, bot)
        self.__add_add_option_button(poll, bot)
        self.__add_see_vote_button(poll)
        self.__add_close_poll_button(poll, bot)

    def __add_vote_buttons(self, poll: Poll, paul: Paul) -> None:
        if not poll.is_expired:
            for option in poll.options:
                self.__buttons.append(VoteButton(paul, option).button)

    def __add_add_option_button(self, poll: Poll, bot: "Paul") -> None:
        if (
            not poll.is_expired
            and poll.allowed_editors
            and len(poll.options) < Poll.MAX_OPTIONS
        ):
            self.__buttons.append(AddOptionButton(bot, poll).button)

    def __add_see_vote_button(self, poll: Poll) -> None:
        if poll.allowed_vote_viewers:
            self.__buttons.append(SeeVotesButton(poll).button)

    def __add_close_poll_button(self, poll: Poll, bot: "Paul") -> None:
        if not poll.is_expired:
            self.__buttons.append(ClosePollButton(bot, poll).button)

    @override
    def __getitem__(self, index: int) -> Button:
        return self.__buttons[index]

    @override
    def __len__(self) -> int:
        return len(self.__buttons)

    @override
    def __iter__(self) -> Iterator[Button]:
        return iter(self.__buttons)
