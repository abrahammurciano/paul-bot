from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Self, override

from disnake.enums import ButtonStyle
from disnake.ext.commands import InteractionBot
from disnake.interactions.message import MessageInteraction

from paul_bot.application.mention import mentions_str
from paul_bot.application.poll import Poll
from paul_bot.presentation.errors import FriendlyError

from ..add_option_modal import AddOptionModal
from .base_button import BaseButton

if TYPE_CHECKING:
    from paul_bot.presentation.paul import Paul

logger = logging.getLogger(__name__)


class AddOptionButton(BaseButton):
    _CUSTOM_ID_SUFFIX: str = " add_option"

    def __init__(self, paul: Paul, poll: Poll) -> None:
        """Construct a Button used to vote for an option.

        Args:
            paul: The Paul instance.
            poll: The poll to add options to when this button gets clicked.
        """
        self.__paul = paul
        self.__poll = poll

        super().__init__(
            allowed_clickers=poll.allowed_editors,
            style=ButtonStyle.grey,
            label="Add Option",
            custom_id=str(poll.poll_id),
            emoji="📝",
            row=4,
        )

    @override
    @classmethod
    async def from_interaction(
        cls, paul: Paul, inter: MessageInteraction[InteractionBot]
    ) -> Self:
        poll = await Poll.fetch_by_id(cls._parse_custom_id(inter))
        if poll is None:
            raise FriendlyError(
                "I'm sorry, I could not find this poll in the database.", inter
            )
        return cls(paul, poll)

    @override
    async def _on_click(self, inter: MessageInteraction[InteractionBot]) -> None:
        logger.debug(
            f"{inter.author.display_name} wants to add an option to poll {self.__poll.question}."
        )
        await inter.response.send_modal(AddOptionModal(self.__paul, self.__poll))

    @property
    @override
    def _no_permission_message(self) -> str:
        return f"You do not have permission to add options to this poll.\nThe allowed editors are: {mentions_str(self.allowed_clickers)}"
