from __future__ import annotations

from asyncio import CancelledError, Event, Task, create_task, sleep
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from ..application import Poll

if TYPE_CHECKING:
    from .paul import Paul


class CloseLoop:
    """A background task that closes polls when they expire."""

    def __init__(self, paul: Paul) -> None:
        self.__paul = paul
        self.__next_expire: datetime = datetime.max.replace(tzinfo=UTC)
        self.__wait_task: Task[None] | None = None
        self.__poll_added = Event()
        self.__closing: set[int] = set()

    def register(self, poll: Poll) -> None:
        """Check if the newly added poll is scheduled to expire sooner than the current next expiration."""
        if poll.closed or not poll.expires:
            return
        if self.__next_expire is None or poll.expires < self.__next_expire:
            if self.__wait_task is not None:
                self.__wait_task.cancel()
            self.__poll_added.set()

    def start(self) -> None:
        """Start the loop."""
        create_task(self.__loop())

    async def __loop(self) -> None:
        while True:
            poll = await Poll.next_to_expire()
            if poll is None or poll.expires is None:
                self.__poll_added.clear()
                await self.__poll_added.wait()
                continue
            self.__next_expire = poll.expires
            try:
                await self.__wait()
            except CancelledError:
                continue
            if poll.closed:
                continue
            create_task(self.__close_poll(poll))

    async def __wait(self) -> None:
        """Wait for the next poll to expire, updating the wait task. If the wait task is cancelled while waiting, CancelledError will be raised."""
        self.__wait_task = create_task(self.__wait_for_expire())
        try:
            await self.__wait_task
        finally:
            self.__wait_task = None

    async def __wait_for_expire(self) -> None:
        await sleep((self.__next_expire - datetime.now(UTC)).total_seconds())

    async def __close_poll(self, poll: Poll) -> None:
        if poll.poll_id in self.__closing:
            return
        self.__closing.add(poll.poll_id)
        await self.__paul.close_poll_now(poll)
        self.__closing.remove(poll.poll_id)
