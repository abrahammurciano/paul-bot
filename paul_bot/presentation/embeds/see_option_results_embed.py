from disnake import Embed
from .colours import get_colour
from ...application.option import Option


class SeeOptionResultsEmbed(Embed):
    def __init__(self, option: Option, index: int):
        mentions = " ".join(f"<@{member_id}>" for member_id in option.votes)
        super().__init__(
            colour=get_colour(index).colour,
            title=f"{index}. {option.label}",
            description=f"*{option.vote_count} votes*\n{mentions}",
        )

    def split(self) -> list[Embed]:
        LIMIT = 5700  # 6000 actually, but just to be safe and accounting for the title and vote count
        if len(self) < LIMIT:
            return [self]
        desc = str(self.description)
        embeds = []
        start = end = 0
        while end < len(desc):
            try:
                end = next(
                    (i for i in range(start + LIMIT - 1, -1, -1) if desc[i] == " "),
                    start + LIMIT,
                )
            except IndexError:
                end = len(desc)
            embeds.append(
                Embed(color=self.colour, title=self.title, description=desc[start:end])
            )
            start = end + 1
        return embeds
