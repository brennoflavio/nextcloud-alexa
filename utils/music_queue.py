from typing import Tuple


class MusicQueue:
    def __init__(self):
        self._queue = []
        self._idx = None

    def start_queue(self, playlist: list) -> str:
        self._queue = [*playlist]
        self._idx = 0
        return self._queue[self._idx]

    def next_item(self) -> Tuple[str, None]:
        self._idx += 1
        if len(self._queue) <= self._idx:
            return

        return self._queue[self._idx]

    def clear(self):
        self._queue = []
        self._idx = None

    def previous_item(self) -> Tuple[str, None]:
        self._idx -= 1
        if len(self._queue) <= self._idx or self._idx < 0:
            return

        return self._queue[self._idx]

    def current(self) -> Tuple[str, None]:
        if self._queue:
            return self._queue[self._idx]
        return None
