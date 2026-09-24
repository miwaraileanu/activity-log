import threading
from collections import deque
from agent.config import settings


class Buffer:
    def __init__(self):
        self._lock = threading.Lock()
        self._queue: deque = deque()
        self._on_flush_callback = None  # optional, for auto-flush

    def add(self, event: dict) -> None:
        with self._lock:
            self._queue.append(event)

    def flush(self) -> list[dict]:
        with self._lock:
            items = list(self._queue)
            self._queue.clear()
            return items

    def size(self) -> int:
        with self._lock:
            return len(self._queue)


buffer = Buffer()
