from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from ..application.mention import Mention


@dataclass(slots=True)
class PollCommandParams:
    question: str
    options: Iterable[str]
    expires: datetime | None
    allow_multiple_votes: bool
    allowed_vote_viewers: Iterable[Mention]
    allowed_editors: Iterable[Mention]
    allowed_voters: Iterable[Mention]
