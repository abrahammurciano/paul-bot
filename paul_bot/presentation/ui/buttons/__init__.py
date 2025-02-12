from __future__ import annotations

from typing import TYPE_CHECKING

from disnake import MessageInteraction
from disnake.ext.commands import InteractionBot

from .add_option_button import AddOptionButton
from .base_button import BaseButton, InteractionMismatchError
from .close_poll_button import ClosePollButton
from .see_votes_button import SeeVotesButton
from .vote_button import VoteButton

if TYPE_CHECKING:
    from paul_bot.presentation.paul import Paul

__all__ = (
    "BaseButton",
    "AddOptionButton",
    "ClosePollButton",
    "VoteButton",
    "SeeVotesButton",
)


async def factory(paul: Paul, inter: MessageInteraction[InteractionBot]) -> BaseButton:
    for cls in (AddOptionButton, VoteButton, SeeVotesButton, ClosePollButton):
        try:
            return await cls.from_interaction(paul, inter)
        except InteractionMismatchError:
            pass
    raise ValueError("No button class matched the interaction.")
