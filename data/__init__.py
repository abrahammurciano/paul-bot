import os
import cruds
import asyncpg
from polls_crud import PollsCrud
from options_crud import OptionsCrud
from votes_crud import VotesCrud


async def init():
	pool = await asyncpg.create_pool(
		os.getenv("HEROKU_POSTGRESQL_AQUA_URL", ""), ssl="require", min_size=5
	)
	cruds.polls_crud = PollsCrud(pool)
	cruds.options_crud = OptionsCrud(pool)
	cruds.votes_crud = VotesCrud(pool)