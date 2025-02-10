from asyncio import CancelledError, Event, Task, create_task, sleep
from datetime import UTC, datetime

from typed_data_structures import Heap

from ..application import Poll


class CloseQueue:
    """A queue for polls that are scheduled to be closed."""

    def __init__(self) -> None:
        self.__queue = Heap[Poll]((), key=lambda poll: poll.expires or datetime.max)
        self.__wait_for_expire: Task[None] | None = None
        self.__poll_added = Event()

    def add(self, poll: Poll) -> None:
        """Add a poll to the queue if it is scheduled to be closed."""
        if poll.closed or not poll.expires:
            return
        self.__queue.push(poll)
        if self.__wait_for_expire is not None:
            self.__wait_for_expire.cancel()
        self.__poll_added.set()

    async def wait(self) -> Poll:
        """Get the next poll to be closed when it expires."""
        while True:
            if not self.__queue:
                self.__poll_added.clear()
                await self.__poll_added.wait()
            poll = self.__queue.pop()
            if poll.expires is None:
                continue
            if poll.expires < datetime.now(UTC):
                return poll
            try:
                self.__wait_for_expire = create_task(
                    sleep((poll.expires - datetime.now(UTC)).total_seconds())
                )
                await self.__wait_for_expire
                self.__wait_for_expire = None
                return poll
            except CancelledError:
                self.__queue.push(poll)
                self.__wait_for_expire = None
