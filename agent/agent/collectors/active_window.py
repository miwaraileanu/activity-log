import sys
import time
import threading
import logging
from agent.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

if sys.platform == 'win32':
    from agent.platform.windows import get_active_window_title
else:
    from agent.platform.linux import get_active_window_title


class ActiveWindowCollector(BaseCollector):
    def __init__(self, device_id: str, buf=None, poll_interval: float = 0.5):
        super().__init__(device_id, buf)
        self._poll_interval = poll_interval
        self._last_title: str = ''
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._last_title = get_active_window_title()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="ActiveWindowCollector")
        self._thread.start()

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            time.sleep(self._poll_interval)
            try:
                title = get_active_window_title()
                if title and title != self._last_title:
                    self._emit("window_focus", title)
                    self._last_title = title
            except Exception as e:
                logger.warning(f"ActiveWindowCollector error: {e}")

    def stop(self) -> None:
        super().stop()
        if self._thread:
            self._thread.join(timeout=3)
