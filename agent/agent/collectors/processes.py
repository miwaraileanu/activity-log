import time
import threading
import logging
import psutil
from agent.collectors.base import BaseCollector

logger = logging.getLogger(__name__)


class ProcessCollector(BaseCollector):
    def __init__(self, device_id: str, buf=None, poll_interval: float = 1.0):
        super().__init__(device_id, buf)
        self._poll_interval = poll_interval
        self._snapshot: dict[int, str] = {}  # pid -> name
        self._thread: threading.Thread | None = None

    def _get_procs(self) -> dict[int, str]:
        procs = {}
        for p in psutil.process_iter(['pid', 'name']):
            try:
                procs[p.info['pid']] = p.info['name'] or ''
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return procs

    def start(self) -> None:
        self._snapshot = self._get_procs()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="ProcessCollector")
        self._thread.start()

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            time.sleep(self._poll_interval)
            try:
                current = self._get_procs()
                new_pids = set(current) - set(self._snapshot)
                gone_pids = set(self._snapshot) - set(current)
                for pid in new_pids:
                    self._emit("process_start", f"{current[pid]} started (pid {pid})")
                for pid in gone_pids:
                    self._emit("process_stop", f"{self._snapshot[pid]} stopped (pid {pid})")
                self._snapshot = current
            except Exception as e:
                logger.warning(f"ProcessCollector error: {e}")

    def stop(self) -> None:
        super().stop()
        if self._thread:
            self._thread.join(timeout=3)
