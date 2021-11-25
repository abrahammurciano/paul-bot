import asyncio
from typing import Optional
from disnake import Client, Message
from disnake.interactions.message import MessageInteraction
from disnake.webhook.async_ import WebhookMessage


async def get_text_input(
	prompt: str, inter: MessageInteraction, client: Client, timeout: float = 60.0
) -> Optional[Message]:
	prompt = f"{inter.author.mention} {prompt}"
	prompt_msg = await inter.followup.send(prompt, wait=True)
	try:
		message = await client.wait_for(
			"message",
			check=lambda m: m.author == inter.author and m.channel == inter.channel,
			timeout=timeout,
		)
		return message
	except asyncio.TimeoutError:
		await prompt_msg.edit(content=f"~~{prompt}~~ *(Timed out)*")
		return None