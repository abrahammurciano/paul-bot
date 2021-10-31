import asyncpg
import disnake
from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction
from errors import FriendlyError
from mention import mentions_str
from poll.poll import Poll
from poll.embeds import PollEmbed


class VoteButton(disnake.ui.Button):
	def __init__(self, poll: Poll, index: int, conn: asyncpg.Connection):
		"""Construct a Button used to vote for an option.

		Args:
			poll (Poll): The poll that this button belongs to.
			index (int): The index (starting from 0) of the option this button is for.
			conn (asyncpg.Connection): The database connection to register the vote with.
		"""
		self.poll = poll
		self.option = poll.options[index]
		self.conn = conn
		super().__init__(
			style=ButtonStyle.blurple,
			label=(
				f"{str(index + 1)}."
				f" {self.option.label[:30]}{'...' if len(self.option.label) > 30 else ''}"
			),
			custom_id=str(self.option.option_id),
		)

	async def callback(self, interaction: MessageInteraction):
		if any(
			mention.includes_member(interaction.author)
			for mention in self.poll.allowed_voters
		):
			await self.option.toggle_vote(self.conn, interaction.author.id)
			await interaction.response.edit_message(embed=PollEmbed(self.poll))
		else:
			raise FriendlyError(
				"You do not have permission to vote for this poll.\nThe allowed voters"
				f" are: {mentions_str(self.poll.allowed_voters)}",
				interaction.response,
			)
