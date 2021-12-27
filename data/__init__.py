import os
from data import cruds
import asyncpg
from data.polls_crud import PollsCrud
from data.options_crud import OptionsCrud
from data.votes_crud import VotesCrud


async def init():
	pool = await asyncpg.create_pool(
		os.getenv("DATABASE_URL", ""), ssl="require", min_size=3, max_size=5
	)
	cruds.polls_crud = PollsCrud(pool)
	cruds.options_crud = OptionsCrud(pool)
	cruds.votes_crud = VotesCrud(pool)
