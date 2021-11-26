import disnake
from application.poll import Poll
from . import colours


class QuestionResultsEmbed(disnake.Embed):
	def __init__(self, poll: Poll):
		super().__init__(colour=colours.blurple, title=poll.question)