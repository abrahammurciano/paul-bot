from __future__ import annotations

from typing import TYPE_CHECKING, Self, override

import disnake
from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction

from paul_bot.application.poll import Poll
from paul_bot.presentation.errors import FriendlyError
from paul_bot.utils import chunks

from ...embeds.question_results_embed import QuestionResultsEmbed
from ...embeds.see_option_results_embed import SeeOptionResultsEmbed
from .base_button import BaseButton

if TYPE_CHECKING:
    from paul_bot.presentation.paul import Paul


class SeeVotesButton(BaseButton):
    _CUSTOM_ID_SUFFIX: str = " see_votes"

    def __init__(self, poll: Poll) -> None:
        self.__poll = poll
        super().__init__(
            allowed_clickers=poll.allowed_vote_viewers,
            style=ButtonStyle.grey,
            label="See Votes",
            custom_id=str(poll.poll_id),
            emoji="👀",
            row=4,
        )

    @override
    @classmethod
    async def from_interaction(cls, paul: Paul, inter: MessageInteraction) -> Self:
        poll = await Poll.fetch_by_id(cls._parse_custom_id(inter))
        if poll is None:
            raise FriendlyError(
                "I'm sorry, I could not find this poll in the database.", inter
            )
        return cls(poll)

    @override
    async def _on_click(self, inter: MessageInteraction) -> None:
        await inter.response.defer(with_message=True, ephemeral=True)
        embeds: list[disnake.Embed] = [QuestionResultsEmbed(self.__poll)]
        embeds.extend(
            embed
            for index, option in enumerate(self.__poll.options)
            for embed in SeeOptionResultsEmbed(option, index).split()
        )
        for ten_embeds in chunks(embeds, 10):
            await inter.followup.send(
                embeds=[embed for embed in ten_embeds if embed is not None],
                ephemeral=True,
            )

    @property
    @override
    def _no_permission_message(self) -> str:
        return "You do not have permission to view the votes."
