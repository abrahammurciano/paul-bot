from dataclasses import dataclass
from typing import Iterable, Self, Union

import disnake
import disnake.utils


@dataclass(slots=True, frozen=True)
class Mention:
    """A mention of a member or role in a guild."""

    prefix: str
    """The prefix of the mention, either "@" for a member or "@&" for a role."""

    mentioned_id: int
    """The ID of the member or role mentioned."""

    @classmethod
    def member(cls, member_id: int) -> Self:
        """Create a Mention for a member.

        Args:
            member_id: The ID of the member to mention.

        Returns:
            A Mention for the given member.
        """
        return cls(prefix="@", mentioned_id=member_id)

    @classmethod
    def role(cls, role_id: int) -> Self:
        """Create a Mention for a role.

        Args:
            role_id: The ID of the role to mention.

        Returns:
            A Mention for the given role.
        """
        return cls(prefix="@&", mentioned_id=role_id)

    @classmethod
    def named(cls, name: str, guild: disnake.Guild) -> Self | None:
        """Create a Mention from a string containing the name of a guild's member or role.

        Args:
            name: The name of the member or role to parse. May or may not start with an @.
            guild: The guild to search for the member or role.

        Returns:
            A Mention if the name was found, or None if it was not.
        """
        name = name.removeprefix("@")
        if name == "everyone":
            return cls(prefix="@&", mentioned_id=guild.default_role.id)
        if member := guild.get_member_named(name):
            return cls(prefix="@", mentioned_id=member.id)
        if role := disnake.utils.get(guild.roles, name=name):
            return cls(prefix="@&", mentioned_id=role.id)
        return None

    def includes_member(self, member: Union[disnake.User, disnake.Member]) -> bool:
        """Check if this mention mentions the given member or any of their roles.

        Args:
            member: The member to check.

        Returns:
            Whether this mention includes the given member.
        """
        return self.mentioned_id == member.id or (
            isinstance(member, disnake.Member)
            and self.mentioned_id in (role.id for role in member.roles)
        )

    def __str__(self) -> str:
        return f"<{self.prefix}{self.mentioned_id}>"

    def __repr__(self) -> str:
        return f"<{self.prefix}{str(self.mentioned_id)[:3]}...{str(self.mentioned_id)[-3:]}>"


def mentions_str(mentions: Iterable[Mention]) -> str:
    return ", ".join(str(mention) for mention in mentions)
