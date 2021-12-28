import logging
import asyncio
from disnake.client import Client


class DiscordChannelHandler(logging.Handler):
    def __init__(self, client: Client, channel_id: int) -> None:
        super().__init__()
        self.__client = client
        self.__channel_id = channel_id

    def emit(self, record: logging.LogRecord) -> None:
        async def send_message(message: str) -> None:
            channel = self.__client.get_channel(self.__channel_id)
            if hasattr(channel, "send"):
                await channel.send(message)  # type: ignore
            else:
                raise ValueError(
                    f"Cannot send messages to channel {channel}."
                )  # TODO: ensure this doesn't cause a recursive loop

        asyncio.create_task(send_message(self.format(record)))
