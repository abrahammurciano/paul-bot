from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction
from poll.poll import Poll
from .poll_action_button import PollActionButton


class SeeVotesButton(PollActionButton):
	def __init__(self, bot, poll: Poll):
		async def show_votes(inter: MessageInteraction):
			await inter.followup.send("response 1", ephemeral=True)
			await inter.followup.send("response 2", ephemeral=True)

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
