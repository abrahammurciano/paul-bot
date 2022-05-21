from dataclasses import dataclass
from typing import Iterable, Union
import disnake


@dataclass
class Mention:
    prefix: str
    mentioned_id: int

    def includes_member(self, member: Union[disnake.User, disnake.Member]) -> bool:
        """Check if this mention mentions the given member or any of their roles.

        Args:
                member (Union[disnake.User, disnake.Member]): The member to check.

        Returns:
                bool: Whether this mention includes the given member.
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
