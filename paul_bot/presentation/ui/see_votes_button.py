import disnake
from disnake.enums import ButtonStyle
from disnake.interactions.message import MessageInteraction
from .poll_action_button import PollActionButton
from ..embeds.question_results_embed import QuestionResultsEmbed
from ..embeds.see_option_results_embed import SeeOptionResultsEmbed
from ...application.poll import Poll
from ...utils import chunks


class SeeVotesButton(PollActionButton):
    def __init__(self, poll: Poll):
        async def show_votes(inter: MessageInteraction):
            await inter.response.defer(with_message=True, ephemeral=True)
            embeds: list[disnake.Embed] = [QuestionResultsEmbed(poll)]
            embeds.extend(
                embed
                for index, option in enumerate(poll.options)
                for embed in SeeOptionResultsEmbed(option, index).split()
            )
            for ten_embeds in chunks(embeds, 10):
                await inter.followup.send(
                    embeds=[embed for embed in ten_embeds if embed is not None],
                    ephemeral=True,
                )

        super().__init__(
            action=show_votes,
            allowed_clickers=poll.allowed_vote_viewers,
            style=ButtonStyle.grey,
            label="See Votes",
            custom_id=f"{poll.poll_id} see_votes",
            emoji="👀",
            row=4,
            no_permission_message="You do not have permission to view the votes.",
        )
