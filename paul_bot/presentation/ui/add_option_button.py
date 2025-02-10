import logging
from typing import TYPE_CHECKING

from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction

from ...application.mention import mentions_str
from ...application.poll import Poll
from .add_option_modal import AddOptionModal
from .poll_action_button import PollActionButton

if TYPE_CHECKING:
    from paul_bot import Paul

logger = logging.getLogger(__name__)


class AddOptionButton(PollActionButton):
    def __init__(self, bot: "Paul", poll: Poll) -> None:
        """Construct a Button used to vote for an option.

        Args:
            bot: The bot instance.
            poll: The poll to add options to when this button gets clicked.
        """

        async def add_option(inter: MessageInteraction) -> None:
            logger.debug(
                f"{inter.author.display_name} wants to add an option to poll"
                f" {poll.question}."
            )
            await inter.response.send_modal(AddOptionModal(bot, poll))

        super().__init__(
            action=add_option,
            allowed_clickers=poll.allowed_editors,
            style=ButtonStyle.grey,
            label="Add Option",
            custom_id=f"{poll.poll_id} add_option",
            emoji="📝",
            row=4,
            no_permission_message=(
                "You do not have permission to add options to this poll.\nThe allowed"
                f" editors are: {mentions_str(poll.allowed_editors)}"
            ),
        )
