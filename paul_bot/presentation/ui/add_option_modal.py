from __future__ import annotations

import logging
from typing import TYPE_CHECKING, override

from disnake.interactions import ModalInteraction
from disnake.ui import Modal, TextInput

from paul_bot.application.poll import Poll

from ..errors import handle_error

if TYPE_CHECKING:
    from paul_bot.presentation.paul import Paul

logger = logging.getLogger(__name__)


class AddOptionModal(Modal):
    def __init__(self, paul: Paul, poll: Poll) -> None:
        self.__paul = paul
        self.__poll = poll
        super().__init__(
            title="What option do you want to add?",
            custom_id=f"{poll.poll_id} add_option_form",
            components=TextInput(
                label="Enter a new option",
                custom_id=f"{poll.poll_id} add_option_input",
                placeholder="Maybe",
                max_length=Poll.MAX_OPTION_LENGTH,
            ),
        )

    @override
    async def callback(self, interaction: ModalInteraction) -> None:
        new_option = interaction.text_values[f"{self.__poll.poll_id} add_option_input"]
        await self.__paul.add_poll_option(
            self.__poll, new_option, interaction.author.id, interaction
        )
        await interaction.response.send_message(
            f"Successfully added option '{new_option}'", ephemeral=True
        )

    @override
    async def on_error(self, error: Exception, interaction: ModalInteraction) -> None:
        await handle_error(error)
