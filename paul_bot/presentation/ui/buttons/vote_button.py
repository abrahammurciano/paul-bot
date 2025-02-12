from __future__ import annotations

from typing import TYPE_CHECKING, override

from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction

from paul_bot.application.mention import mentions_str
from paul_bot.application.option import Option
from paul_bot.application.poll import Poll
from paul_bot.presentation.errors import FriendlyError

from .base_button import BaseButton

if TYPE_CHECKING:
    from paul_bot.presentation.paul import Paul


class VoteButton(BaseButton):
    _CUSTOM_ID_SUFFIX: str = ""

    def __init__(self, paul: Paul, option: Option) -> None:
        """Construct a Button used to vote for an option.

        Args:
            paul: The bot instance.
            option: The option to vote for when this button is pressed.
        """
        self.__paul = paul
        self.__option = option
        super().__init__(
            allowed_clickers=option.poll.allowed_voters,
            style=ButtonStyle.blurple,
            label=(
                f"{str(option.index + 1)}. {option.label[:30]}{'...' if len(option.label) > 30 else ''}"
            ),
            custom_id=str(option.option_id),
            emoji="🗳️",
        )

    @override
    @classmethod
    async def from_interaction(
        cls, paul: Paul, inter: MessageInteraction
    ) -> VoteButton:
        option = await Poll.fetch_option(cls._parse_custom_id(inter))
        if option is None:
            raise FriendlyError(
                "I'm sorry, I could not find this option in the database.", inter
            )
        return cls(paul, option)

    @override
    async def _on_click(self, inter: MessageInteraction) -> None:
        await inter.response.defer()
        await self.__paul.toggle_vote(self.__option, inter.author.id)

    @property
    @override
    def _no_permission_message(self) -> str:
        return f"You do not have permission to vote for this poll.\nThe allowed voters are: {mentions_str(self.allowed_clickers)}"
