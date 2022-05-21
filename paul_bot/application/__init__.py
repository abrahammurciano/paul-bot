from .poll import Poll
from .mention import Mention
from .option import Option
from .. import data


async def init():
    await data.init()
