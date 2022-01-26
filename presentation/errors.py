import logging
from typing import Optional
import disnake
from disnake.interactions.base import InteractionResponse
from disnake.interactions.message import MessageInteraction
from disnake.ui.item import Item

logger = logging.getLogger(f"paul.{__name__}")


async def handle_error(error: Exception):
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
		response: InteractionResponse,
		inner: Optional[Exception] = None,
	):
		super().__init__(message, inner)
		self.message = message
		self.response = response

	async def send(self):
		if not self.response.is_done():
			await self.response.send_message(
				f"{self.message}\n\n*If you need help, join my server and ask!"
				" <https://discord.com/invite/mzhSRnnY78>.*",
				ephemeral=True,
			)


class ErrorHandlingView(disnake.ui.View):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_error(
		self, error: Exception, item: Item, interaction: MessageInteraction
	) -> None:
		await handle_error(error)
