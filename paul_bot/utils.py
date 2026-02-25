import asyncio
from asyncio import Task
from collections.abc import Coroutine, Iterable
from itertools import zip_longest
from logging import LogRecord
from typing import Any, override

from discord_lumberjack.message_creators import EmbedMessageCreator


def chunks[T](
    iterable: Iterable[T], chunk_size: int, fill_value: T | None = None
) -> Iterable[tuple[T | None, ...]]:
    """Given an iterable, splits it into chunks of up to the given size.

    Args:
        iterable: The iterable to split into chunks.
        chunk_size: The size of each chunk.
        fill_value: The value to fill the remaining space (if any) in the last chunk with. If the value is None, the last chunk will be shorter than the chunk size.
    """
    args = [iter(iterable)] * chunk_size
    return zip_longest(*args, fillvalue=fill_value)


class EmbedLongMessageCreator(EmbedMessageCreator):
    @override
    def get_description(self, record: LogRecord) -> str:
        return f"**{super().get_title(record)}**"

    @override
    def get_title(self, record: LogRecord) -> str:
        return ""


_tasks = set[Task[Any]]()


def background[T](coro: Coroutine[Any, Any, T]) -> Task[T]:
    task = asyncio.create_task(coro)
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    return task
