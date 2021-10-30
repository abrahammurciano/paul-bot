from disnake.interactions.base import Interaction
from paul import Paul
from poll import Poll
from poll.command_params import PollCommandParams
from poll.embeds.poll_embed import PollEmbed
from poll.embeds.poll_embed_base import PollEmbedBase
from poll.ui import VoteView


async def poll_command(bot: Paul, inter: Interaction, params: PollCommandParams):
	await create_poll(bot, inter, params)


async def create_poll(bot: Paul, inter: Interaction, params: PollCommandParams):
	await inter.response.send_message(
		embed=PollEmbedBase(
			params.question, "<:loading:904120454975991828> Loading poll..."
		)
	)
	message = await inter.original_message()
	poll = await Poll.create_poll(bot.conn, params, message, inter.author)
	await message.edit(embed=PollEmbed(poll), view=VoteView(poll))