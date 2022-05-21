import disnake
from .colours import BLURPLE
from ...application.poll import Poll


class QuestionResultsEmbed(disnake.Embed):
    def __init__(self, poll: Poll):
        super().__init__(colour=BLURPLE, title=poll.question)
