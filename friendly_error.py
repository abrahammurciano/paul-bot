import logging
from typing import Optional
from disnake.interactions.base import InteractionResponse


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
		if not self.response.is_done:
			await self.response.send_message(self.message, ephemeral=True)
		logging.error(self)