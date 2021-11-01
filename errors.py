import logging
from typing import Optional
import disnake
from disnake.interactions.base import InteractionResponse
from disnake.interactions.message import MessageInteraction
from disnake.ui.item import Item


async def handle_error(error: Exception):
	error = getattr(error, "original", error)
	if isinstance(error, FriendlyError):
		await error.send()
	logging.error(error, stack_info=True)


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
			await self.response.send_message(self.message, ephemeral=True)


class ErrorHandlingView(disnake.ui.View):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_error(
		self, error: Exception, item: Item, interaction: MessageInteraction
	) -> None:
		await handle_error(error)