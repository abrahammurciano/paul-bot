from __future__ import annotations

from typing import TYPE_CHECKING, override

from disnake.enums import ButtonStyle
from disnake.ext.commands import InteractionBot
from disnake.interactions.message import MessageInteraction

from paul_bot.application.mention import Mention
from paul_bot.application.poll import Poll
from paul_bot.presentation.errors import FriendlyError

from .base_button import BaseButton

if TYPE_CHECKING:
    from paul_bot.presentation.paul import Paul


class ClosePollButton(BaseButton):
    _CUSTOM_ID_SUFFIX: str = " close"

    def __init__(self, paul: Paul, poll: Poll) -> None:
        self.__paul = paul
        self.__poll = poll
        self.__author_mention = Mention.member(poll.author_id)
        super().__init__(
            allowed_clickers=(self.__author_mention,),
            style=ButtonStyle.red,
            label="Close Poll",
            custom_id=str(poll.poll_id),
            row=4,
        )

    @override
    @classmethod
    async def from_interaction(
        cls, paul: Paul, inter: MessageInteraction
    ) -> ClosePollButton:
        poll = await Poll.fetch_by_id(cls._parse_custom_id(inter))
        if poll is None:
            raise FriendlyError(
                "I'm sorry, I could not find this poll in the database.", inter
            )
        return cls(paul, poll)

    @override
    async def _on_click(self, inter: MessageInteraction[InteractionBot]) -> None:
        await inter.response.defer()
        await self.__paul.close_poll_now(self.__poll)

    @property
    def _no_permission_message(self) -> str:
        return f"You do not have permission to close the poll. Only {self.__author_mention} may do that."
