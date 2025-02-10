import os

import asyncpg

from . import cruds
from .options_crud import OptionsCrud
from .polls_crud import PollsCrud
from .votes_crud import VotesCrud


async def init() -> None:
    pool = await asyncpg.create_pool(
        os.environ["DATABASE_URL"],
        min_size=1,
        max_size=int(os.getenv("MAX_DB_CONNECTIONS", "5")),
    )
    cruds.polls_crud = PollsCrud(pool)
    cruds.options_crud = OptionsCrud(pool)
    cruds.votes_crud = VotesCrud(pool)
