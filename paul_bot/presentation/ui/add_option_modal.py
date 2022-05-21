import logging
from typing import TYPE_CHECKING
from disnake.interactions import ModalInteraction
from disnake.ui import TextInput
from ..errors import ErrorHandlingModal
from ...application.poll import Poll

if TYPE_CHECKING:
    from paul_bot import Paul

logger = logging.getLogger(__name__)


class AddOptionModal(ErrorHandlingModal):
    def __init__(self, bot: "Paul", poll: Poll):
        self.__bot = bot
        self.__poll = poll
        super().__init__(
            title="What option do you want to add?",
            custom_id=f"{poll.poll_id} add_option_form",
            components=TextInput(
                label="Enter a new option",
                custom_id=f"{poll.poll_id} add_option_input",
                placeholder="Maybe",
                max_length=254,
            ),
        )

    async def callback(self, interaction: ModalInteraction) -> None:
        new_option = interaction.text_values[f"{self.__poll.poll_id} add_option_input"]
        await self.__bot.add_poll_option(
            self.__poll, new_option, interaction.author.id, interaction.message
        )
        await interaction.response.send_message(
            f"Successfully added option '{new_option}'", ephemeral=True
        )
