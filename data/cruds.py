from abc import ABC
import asyncpg
from options_crud import OptionsCrud
from polls_crud import PollsCrud
from votes_crud import VotesCrud


polls_crud: PollsCrud
options_crud: OptionsCrud
votes_crud: VotesCrud


class Crud(ABC):
	def __init__(self, pool: asyncpg.Pool):
		self.pool = pool