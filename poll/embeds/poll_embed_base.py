from typing import Optional
import disnake


class PollEmbedBase(disnake.Embed):
	"""A base class for poll embeds. This only sets the colour, title question, and optionally a description."""

	def __init__(self, question: str, description: Optional[str] = None):
		super().__init__(
			title=f"📊 {question}", colour=0x6F85D5, description=description or "",
		)
