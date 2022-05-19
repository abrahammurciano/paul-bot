import disnake
from .colours import get_colour
from ...application.option import Option


class SeeOptionResultsEmbed(disnake.Embed):
	def __init__(self, option: Option, index: int):
		mentions = " ".join(f"<@{member_id}>" for member_id in option.votes)
		super().__init__(
			colour=get_colour(index).colour,
			title=option.label,
			description=f"*{option.vote_count} votes*\n{mentions}",
		)
