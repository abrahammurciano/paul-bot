from datetime import datetime
import disnake
from disnake import utils
from poll import Poll
from poll.option import Option


def initial_embed(question: str) -> disnake.Embed:
	return __embed_template(question, "Loading options...")


def embed(poll: Poll) -> disnake.Embed:
	embed = __embed_template(poll.question)
	for i, option in enumerate(poll.options, start=1):
		embed.add_field(
			name=f"{i}. {option.label}",
			value=__option_body(i - 1, option, poll.vote_count),
			inline=False,
		)
	embed.add_field(name="---", value=__closing_text(poll.expires), inline=False)
	return embed


def __embed_template(question: str, description: str = None) -> disnake.Embed:
	return disnake.Embed(title=f"📊 {question}", color=0x6F85D5, description=description)


def __closing_text(expiry: datetime) -> str:
	return (
		f"Poll close{'d' if expiry < datetime.now() else 's'}"
		f" {utils.format_dt(expiry, style='R')}."
	)


__bar_emojis = "🟨🟩🟥🟦🟪🟧"
__background = "⬛"
__bar_length = 12


def __option_body(index: int, option: Option, total_votes: int) -> str:
	added_by = f"*Added by <@{option.author}>*>\n" if option.author else ""
	proportion = option.vote_count / total_votes if total_votes > 0 else 0
	squares = round(__bar_length * proportion)
	bar = __bar_emojis[index % len(__bar_emojis)] * squares + __background * (
		__bar_length - squares
	)
	return f"{added_by}{bar}`{round(proportion*100)}% ({option.vote_count})`"