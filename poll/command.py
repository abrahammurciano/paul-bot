from typing import Iterable, Optional
from disnake.interactions.base import Interaction
from mention import Mention
from paul import Paul
from datetime import datetime
from typing import Iterable
from paul import Paul
from poll import Poll
from dataclasses import dataclass
from poll.embeds.poll_embed import PollEmbed

from poll.embeds.poll_embed_base import PollEmbedBase


@dataclass
class PollCommandParams:
	question: str
	options: Iterable[str]
	expires: Optional[datetime]
	allow_multiple_votes: bool
	allowed_vote_viewers: Iterable[Mention]
	allowed_editors: Iterable[Mention]
	allowed_voters: Iterable[Mention]


async def poll_command(bot: Paul, inter: Interaction, params: PollCommandParams):
	await create_poll(bot, inter, params)


async def create_poll(bot: Paul, inter: Interaction, params: PollCommandParams):
	await inter.response.send_message(
		embed=PollEmbedBase(params.question, "⚙️ Loading poll...")
	)
	message = await inter.original_message()
	poll = await Poll.create_poll(bot.conn, params, message, inter.author)
	await message.edit(embed=PollEmbed(poll))