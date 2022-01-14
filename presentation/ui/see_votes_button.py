from typing import List
import disnake
from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction
from presentation.embeds.question_results_embed import QuestionResultsEmbed
from presentation.embeds.see_option_results_embed import SeeOptionResultsEmbed
from application.poll import Poll
from .poll_action_button import PollActionButton
from utils import chunks


class SeeVotesButton(PollActionButton):
	def __init__(self, poll: Poll):
		async def show_votes(inter: MessageInteraction):
			raise RuntimeError("Test Error")
			embeds: List[disnake.Embed] = [QuestionResultsEmbed(poll)]
			embeds.extend(
				SeeOptionResultsEmbed(option, index)
				for index, option in enumerate(poll.options)
			)
			for ten_embeds in chunks(embeds, 10):
				await inter.followup.send(
					embeds=[embed for embed in ten_embeds if embed is not None],
					ephemeral=True,
				)

		super().__init__(
			action=show_votes,
			allowed_clickers=poll.allowed_vote_viewers,
			style=ButtonStyle.grey,
			label="See Votes",
			custom_id=f"{poll.poll_id} see_votes",
			emoji="👀",
			row=4,
			no_permission_message="You do not have permission to view the votes.",
		)