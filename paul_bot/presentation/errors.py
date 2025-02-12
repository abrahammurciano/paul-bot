import logging

from disnake.interactions import Interaction

logger = logging.getLogger(__name__)


async def handle_error(error: Exception) -> None:
    error = getattr(error, "original", error)
    if isinstance(error, FriendlyError):
        logger.debug(f"Handling FriendlyError: {error.message}")
        await error.send()
    else:
        logger.exception(str(error) if error else "Something went wrong...")


class FriendlyError(Exception):
    def __init__(
        self,
        message: str,
        inter: Interaction,
        inner: Exception | None = None,
    ):
        super().__init__(message, inner)
        self.message = message
        self.inter = inter

    async def send(self) -> None:
        message = f"{self.message}\n\n*If you need help, join my server and ask! <https://discord.com/invite/mzhSRnnY78>.*"
        send = (
            self.inter.response.send_message
            if not self.inter.response.is_done()
            else self.inter.followup.send
        )
        await send(message, ephemeral=True)
