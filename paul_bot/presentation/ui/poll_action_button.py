from typing import Callable, Coroutine, Iterable

import disnake
from disnake.emoji import Emoji
from disnake.enums import ButtonStyle
from disnake.interactions import MessageInteraction
from disnake.partial_emoji import PartialEmoji

from ...application.mention import Mention, mentions_str
from ..errors import FriendlyError


class PollActionButton(disnake.ui.Button):
    def __init__(
        self,
        action: Callable[[MessageInteraction], Coroutine],
        allowed_clickers: Iterable[Mention],
        style: ButtonStyle,
        label: str,
        custom_id: str,
        emoji: str | Emoji | PartialEmoji | None = None,
        row: int | None = None,
        no_permission_message: str | None = None,
    ):
        super().__init__(
            style=style, label=label, custom_id=custom_id, emoji=emoji, row=row
        )
        self.__allowed_clickers = allowed_clickers
        self.__no_permission_message = (
            no_permission_message
            or f"You do not have permission to perform this action.\nTo perform this action you must be one of {mentions_str(self.__allowed_clickers)}"
        )
        self.__action = action

    async def callback(self, inter: MessageInteraction) -> None:
        if any(
            mention.includes_member(inter.author) for mention in self.__allowed_clickers
        ):
            await self.__action(inter)
        else:
            raise FriendlyError(self.__no_permission_message, inter)
