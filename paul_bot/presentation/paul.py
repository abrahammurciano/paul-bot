import asyncio
import logging
from datetime import datetime, timedelta
from typing import Iterable, Optional

import disnake
import pytz
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
from .command_params import PollCommandParams
from .converters import length_bound_str, parse_expires, parse_mentions, parse_options
from .embeds.poll_closed_embed import PollClosedEmbed
from .embeds.poll_embed import PollEmbed
from .embeds.poll_embed_base import PollEmbedBase
from .errors import FriendlyError, handle_error
from .ui.poll_view import PollView

logger = logging.getLogger(__name__)


class Paul(InteractionBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__total_poll_count = 0
        self.__closed_poll_count = 0
        self.__activity_name = ""
        self.__on_ready_triggered = False

        @self.event
        async def on_ready():
            if not self.__on_ready_triggered:
                logger.info(f"\n{self.user.name} has connected to Discord!\n")
                await self.__load_polls()
                await self.__set_presence()
                self.__on_ready_triggered = True

        @self.event
        async def on_guild_join(guild: Guild):
            logger.info(f"Joined guild {guild.name}.")
            await self.__set_presence()

        @self.event
        async def on_slash_command_error(inter: Interaction, error: Exception):
            await handle_error(error)

        @self.event
        async def on_error(self, event: str, *args, **kwargs):
            logger.exception(f"Error in {event} event: {args=} {kwargs=}")
            # Just in case i don't know what i'm doing
            await super(Paul, self).on_error(event, *args, **kwargs)

        @self.slash_command(desc="Create a poll")
        async def poll(
            inter: GuildCommandInteraction,
            question: str = Param(
                desc="Ask a question...", converter=length_bound_str(254)
            ),
            options: Iterable[str] = Param(
                desc=(
                    "Separate each option with a pipe (|). By default the options are"
                    " yes or no."
                ),
                converter=parse_options(sep="|"),
                default=("Yes", "No"),
            ),
            expires: Optional[datetime] = Param(
                desc=(
                    "When to stop accepting votes, e.g. 1h20m or 1pm UTC+2. Default"
                    " timezone is UTC. Default is 30 days."
                ),
                converter=parse_expires,
                default=lambda _: datetime.now(pytz.utc) + timedelta(days=30),
            ),
            allow_multiple_votes: bool = Param(
                desc="Can a user choose multiple options?", default=False
            ),
            allowed_vote_viewers: list[Mention] = Param(
                desc=(
                    "Mention members or roles who can view the votes. Default is no"
                    " one."
                ),
                default=[],
                converter=parse_mentions,
            ),
            allowed_editors: list[Mention] = Param(
                desc=(
                    "Mention members or roles who may add options to the poll. Default"
                    " is only you."
                ),
                default=lambda inter: [Mention("@", inter.author.id)],
                converter=parse_mentions,
            ),
            allowed_voters: list[Mention] = Param(
                desc="Mention members or roles who may vote. Default is @everyone.",
                default=lambda inter: [
                    Mention("@&", inter.guild.default_role.id)
                    if inter.guild
                    else Mention("@", inter.user.id)
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

    async def close_poll_now(self, poll: Poll, message: Optional[Message] = None):
        """Close a poll immediately.

        Args:
            poll: The poll to close.
            message: The message that triggered the poll to close. If omitted, it will be fetched from Discord's API.
        """
        logger.debug(f"Closing poll {poll.question}.")
        poll.close()
        await self.__update_poll_message(poll, message)
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
            asyncio.create_task(self.__poll_close_task(poll))
        except RuntimeError as e:
            await message.edit(
                embed=PollEmbedBase(
                    "Something went wrong...",
                    f'"{params.question}" could not be created. Please try'
                    f" again.\n\n**Reason:** {e}\n\nIf the problem persists,"
                    " please open an issue on"
                    " [GitHub](https://github.com/abrahammurciano/paul-bot) or ask for"
                    " help on the [Discord"
                    " Server](https://discord.com/invite/mzhSRnnY78).",
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

    async def toggle_vote(self, option: Option, voter_id: int):
        """Toggle a voter's vote for an option, removing the voter's vote from another option if necessary.

        Args:
            option: The option to vote for.
            voter_id: The ID of the user who voted.
        """
        option.toggle_vote(voter_id)
        await self.__update_poll_message(option.poll)

    async def __load_polls(self):
        """Fetch the polls from the database and set up the bot to react to poll interactions."""
        start = datetime.now()
        for poll in await Poll.fetch_polls():
            self.__total_poll_count += 1
            if poll.is_opened:
                asyncio.create_task(self.__poll_close_task(poll))
            else:
                self.__closed_poll_count += 1
            self.add_view(PollView(self, poll))
        logger.info(
            f"Finished loading {self.__total_poll_count} polls. ({(datetime.now() - start).seconds}s)"
        )

    async def __poll_close_task(self, poll: Poll, message: Optional[Message] = None):
        """Close a poll at a specific time.

        This function blocks until the poll is closed if awaited, so you probably want to make it run in the background instead.

        Args:
            poll: The poll to close.
            message: The message that triggered the poll to close. If omitted, it will be fetched from Discord's API.
        """
        if poll.expires is None:
            return
        await asyncio.sleep((poll.expires - datetime.now(pytz.utc)).total_seconds())
        await self.close_poll_now(poll, message)

    async def __update_poll_message(
        self, poll: Poll, message: Optional[Message] = None
    ):
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

    async def __set_presence(self):
        active_polls = self.__total_poll_count - self.__closed_poll_count
        activity_name = (
            f"/poll. {active_polls} active, {self.__total_poll_count} total."
            f" ({len(self.guilds)} servers)"
        )
        if activity_name != self.__activity_name:
            activity = disnake.Activity(name=activity_name, type=ActivityType.listening)
            await self.change_presence(activity=activity)
            self.__activity_name = activity_name
