from typing import Iterable, Optional
from datetime import datetime
from typing import Iterable
from dataclasses import dataclass
from ..application.mention import Mention


@dataclass
class PollCommandParams:
    question: str
    options: Iterable[str]
    expires: Optional[datetime]
    allow_multiple_votes: bool
    allowed_vote_viewers: Iterable[Mention]
    allowed_editors: Iterable[Mention]
    allowed_voters: Iterable[Mention]
