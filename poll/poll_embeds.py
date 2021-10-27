from datetime import datetime
import disnake
from disnake import utils
from disnake.colour import Colour
from disnake.embeds import Embed

from poll import Poll


def initial_embed(question: str) -> disnake.Embed:
	return disnake.Embed(title=" ", color=0x6F85D5).set_author(name=f"📊 {question}")


def embed(poll: Poll) -> disnake.Embed:
	embed = initial_embed(poll.question)
	embed.set_footer(text=f"")
	for i, option in enumerate(poll.options):
		embed.add_field(name=f"{i}. {option.label}", value=f"TODO:", inline=False)
	return embed


def __closing_text(expiry: datetime) -> str:
	return (
		f"Poll close{'d' if expiry < datetime.now() else 's in'}"
		f" {utils.format_dt(expiry, style='R')}."
	)
