import disnake

from ...application.poll import Poll
from .colours import BLURPLE


class QuestionResultsEmbed(disnake.Embed):
    def __init__(self, poll: Poll) -> None:
        super().__init__(colour=BLURPLE, title=poll.question)
