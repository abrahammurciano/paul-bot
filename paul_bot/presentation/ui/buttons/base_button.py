from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable, Self

from disnake import ButtonStyle, Emoji, MessageInteraction, PartialEmoji
from disnake.ext.commands import InteractionBot
from disnake.ui import Button as DisnakeButton

from paul_bot.application.mention import Mention, mentions_str
from paul_bot.presentation.errors import FriendlyError

if TYPE_CHECKING:
    from paul_bot.presentation.paul import Paul


class BaseButton(ABC):
    """A base class for buttons that can be clicked in a message interaction.

    Subclasses must implement the following methods:
    - `from_interaction` to match an interaction to the correct button class, so that the appropriate callback can be called.
    - `_on_click` to define the action that should be taken when the button is clicked, assuming the clicker has permission.

    Subclasses may implement the following methods:
    - `_no_permission_message` to define a custom message to be sent when the clicker does not have permission to click the button.

    Subclasses must also define the following attributes:
    - `_CUSTOM_ID_SUFFIX`: A suffix to be appended to the custom_id of the button. This suffix should be unique to the button class. It is also used to identify the button class in the `from_interaction` method.
    """

    _CUSTOM_ID_SUFFIX: str = ""

    def __init__(
        self,
        allowed_clickers: Iterable[Mention],
        style: ButtonStyle,
        label: str,
        custom_id: str,
        emoji: str | Emoji | PartialEmoji | None = None,
        row: int | None = None,
    ):
        self._style = style
        self._label = label
        self._custom_id = (
            custom_id
            if custom_id.endswith(self._CUSTOM_ID_SUFFIX)
            else f"{custom_id}{self._CUSTOM_ID_SUFFIX}"
        )
        self._emoji = emoji
        self._row = row
        self.allowed_clickers = allowed_clickers

    @classmethod
    @abstractmethod
    async def from_interaction(
        cls, paul: Paul, inter: MessageInteraction[InteractionBot]
    ) -> Self:
        """Create an instance of the button from an interaction. If the interaction does not match this kind of button, raise an InteractionMismatchError."""

    @property
    def button(self) -> DisnakeButton:
        return DisnakeButton(
            style=self._style,
            label=self._label,
            custom_id=self._custom_id,
            emoji=self._emoji,
            row=self._row,
        )

    async def callback(self, inter: MessageInteraction[InteractionBot]) -> None:
        if any(
            mention.includes_member(inter.author) for mention in self.allowed_clickers
        ):
            await self._on_click(inter)
        else:
            raise FriendlyError(self._no_permission_message, inter)

    @abstractmethod
    async def _on_click(self, inter: MessageInteraction[InteractionBot]) -> None: ...

    @property
    def _no_permission_message(self) -> str:
        return f"You do not have permission to perform this action.\nTo perform this action you must be one of {mentions_str(self.allowed_clickers)}"

    @classmethod
    def _parse_custom_id(cls, inter: MessageInteraction[InteractionBot]) -> int:
        """Try to parse the numerical ID from the button's custom ID. If the custom ID does not match the expected format, raise an InteractionMismatchError."""
        custom_id = inter.component.custom_id or ""
        if not custom_id.endswith(cls._CUSTOM_ID_SUFFIX):
            raise InteractionMismatchError(cls, inter)
        try:
            return int(custom_id.removesuffix(cls._CUSTOM_ID_SUFFIX))
        except ValueError:
            raise InteractionMismatchError(cls, inter)


class InteractionMismatchError(ValueError):
    def __init__(
        self, cls: type[BaseButton], inter: MessageInteraction[InteractionBot]
    ) -> None:
        component_description = f"{type(inter.component).__name__}(custom_id={inter.component.custom_id!r}, label={inter.component.label if isinstance(inter.component, DisnakeButton) else None})"
        super().__init__(
            f"The interaction does not match the class {cls.__name__}. The interacted component is: {component_description}"
        )
