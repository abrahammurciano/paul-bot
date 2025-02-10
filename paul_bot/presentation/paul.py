import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Iterable, override

import disnake
import psutil
from disnake.enums import ActivityType
from disnake.errors import Forbidden
from disnake.ext.commands.bot import InteractionBot
from disnake.ext.commands.params import Param
from disnake.guild import Guild
from disnake.interactions.application_command import GuildCommandInteraction
from disnake.interactions.base import Interaction
from disnake.interactions.modal import ModalInteraction
from disnake.message import Message

from ..application import Mention, Poll
from ..application.option import Option
from .close_queue import CloseQueue
from .command_params import PollCommandParams
from .converters import length_bound_str, parse_expires, parse_mentions, parse_options
from .embeds.poll_closed_embed import PollClosedEmbed
from .embeds.poll_embed import PollEmbed
from .embeds.poll_embed_base import PollEmbedBase
from .errors import FriendlyError, handle_error
from .ui.poll_view import PollView

logger = logging.getLogger(__name__)


class Paul(InteractionBot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__total_poll_count = 0
        self.__closed_poll_count = 0
        self.__activity_name = ""
        self.__on_ready_triggered = False
        self.__close_queue = CloseQueue()

        @self.event
        async def on_ready() -> None:
            if not self.__on_ready_triggered:
                logger.info(f"\n{self.user.name} has connected to Discord!\n")
                asyncio.create_task(self.__poll_close_task())
                await self.__set_loading_presence()
                await self.__load_polls()
                await self.__set_presence()
                self.__on_ready_triggered = True

        @self.event
        async def on_guild_join(guild: Guild) -> None:
            logger.info(f"Joined guild {guild.name}.")
            await self.__set_presence()

        @self.slash_command(desc="Create a poll")
        async def poll(
            inter: GuildCommandInteraction,
            question: str = Param(
                desc="Ask a question...", converter=length_bound_str(254)
            ),
            options: Iterable[str] = Param(
                desc="Separate each option with a pipe (|). By default the options are yes or no.",
                converter=parse_options(sep="|"),
                default=("Yes", "No"),
            ),
            expires: datetime | None = Param(
                desc="When to stop accepting votes, e.g. 1h20m or 1pm UTC+2. Default timezone is UTC. Default is 30 days.",
                converter=parse_expires,
                default=lambda _: datetime.now(UTC) + timedelta(days=30),
            ),
            allow_multiple_votes: bool = Param(
                desc="Can a user choose multiple options?", default=False
            ),
            allowed_vote_viewers: list[Mention] = Param(
                desc="Mention members or roles who can view the votes. Default is no one.",
                default=[],
                converter=parse_mentions,
            ),
            allowed_editors: list[Mention] = Param(
                desc="Mention members or roles who may add options to the poll. Default is only you.",
                default=lambda inter: [Mention("@", inter.author.id)],
                converter=parse_mentions,
            ),
            allowed_voters: list[Mention] = Param(
                desc="Mention members or roles who may vote. Default is @everyone.",
                default=lambda inter: [
                    (
                        Mention("@&", inter.guild.default_role.id)
                        if inter.guild
                        else Mention("@", inter.user.id)
                    )
                ],
                converter=parse_mentions,
            ),
        ):
            params = PollCommandParams(
                question,
                options,
                expires,
                allow_multiple_votes,
                allowed_vote_viewers,
                allowed_editors,
                allowed_voters,
            )
            logger.debug(f"{inter.author.name} wants to create a poll: {params}.")
            await inter.response.send_message(
                embed=PollEmbedBase(
                    question, "<a:loading:904120454975991828> Loading poll..."
                )
            )
            message = await inter.original_message()
            await self.new_poll(params, inter.author.id, message)
            logger.debug(f"{inter.author.name} successfully created a poll {question}.")

    async def close_poll_now(self, poll: Poll) -> None:
        """Close a poll immediately."""
        logger.debug(f"Closing poll {poll.question}.")
        poll.close()
        await self.__update_poll_message(poll)
        self.__closed_poll_count += 1
        await self.__set_presence()

    async def new_poll(
        self, params: PollCommandParams, author_id: int, message: Message
    ):
        try:
            poll = await Poll.create_poll(params, author_id, message)
            self.__total_poll_count += 1
            await self.__update_poll_message(poll, message)
            await self.__set_presence()
            self.__close_queue.add(poll)
        except RuntimeError as e:
            await message.edit(
                embed=PollEmbedBase(
                    f'Something went wrong... "{params.question}" could not be created. Please try again.\n\n**Reason:** {e}\n\nIf the problem persists, please open an issue on [GitHub](https://github.com/abrahammurciano/paul-bot) or ask for help on the [Discord Server](https://discord.com/invite/mzhSRnnY78).',
                )
            )

    async def add_poll_option(
        self, poll: Poll, label: str, author_id: int, inter: ModalInteraction
    ):
        """Add a new option to the given poll.

        Args:
            poll: The poll to add the option to.
            label: The label of the option.
            author_id: The ID of the user who added the option.
            message: The message containing the poll. If omitted, it will be fetched asynchronously.
        """
        if len(poll.options) == Poll.MAX_OPTIONS:
            raise FriendlyError("You can't add more options to this poll.", inter)
        await poll.new_option(label, author_id)
        await self.__update_poll_message(poll, inter.message)
        logger.debug(f"Added option {label} to poll {poll.question}")

    async def toggle_vote(self, option: Option, voter_id: int) -> None:
        """Toggle a voter's vote for an option, removing the voter's vote from another option if necessary.

        Args:
            option: The option to vote for.
            voter_id: The ID of the user who voted.
        """
        option.toggle_vote(voter_id)
        await self.__update_poll_message(option.poll)

    async def __load_polls(self) -> None:
        """Fetch the polls from the database and set up the bot to react to poll interactions."""
        start = datetime.now()
        async for poll in Poll.fetch_polls():
            self.__total_poll_count += 1
            if poll.closed:
                self.__closed_poll_count += 1
            self.__close_queue.add(poll)
            self.add_view(PollView(self, poll))
        logger.info(
            f"Finished loading {self.__total_poll_count} polls. ({(datetime.now() - start).seconds}s, {psutil.virtual_memory().percent}% memory used, {psutil.Process().memory_info().rss / 1024 ** 2:.2f} MB by Paul)"
        )

    async def __poll_close_task(self) -> None:
        """Iterate over the polls in expiration order closing them as they expire."""
        while True:
            asyncio.create_task(self.close_poll_now(await self.__close_queue.wait()))

    async def __update_poll_message(self, poll: Poll, message: Message | None = None):
        """Update the poll's message. This should be called after a poll changes.

        Args:
            poll: The poll whose message should be updated.
            message: The message containing the poll. If omitted, it will be fetched asynchronously.
        """
        try:
            message = message or await self.__get_poll_message(poll)
            await message.edit(
                embed=PollClosedEmbed(poll) if poll.is_expired else PollEmbed(poll),
                view=PollView(self, poll),
            )
        except Forbidden:
            pass

    async def __get_poll_message(self, poll: Poll) -> Message:
        return await self.get_partial_messageable(poll.channel_id).fetch_message(
            poll.message_id
        )

    async def __set_presence(self) -> None:
        active_polls = self.__total_poll_count - self.__closed_poll_count
        activity_name = f"/poll. {active_polls} active, {self.__total_poll_count} total. ({len(self.guilds)} servers)"
        if activity_name != self.__activity_name:
            activity = disnake.Activity(name=activity_name, type=ActivityType.listening)
            await self.change_presence(activity=activity)
            self.__activity_name = activity_name

    async def __set_loading_presence(self) -> None:
        activity = disnake.CustomActivity(name="Loading...", type=ActivityType.watching)
        await self.change_presence(activity=activity, status=disnake.Status.dnd)

    @override
    async def on_error(self, event_name: str, *args, **kwargs) -> None:
        logger.exception(f"Error in {event_name} event: {args=} {kwargs=}")

    @override
    async def on_slash_command_error(
        self, inter: Interaction, error: Exception
    ) -> None:
        await handle_error(error)
