import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from agent.collectors.base import BaseCollector
from agent.config import settings

logger = logging.getLogger(__name__)


class _Handler(FileSystemEventHandler):
    def __init__(self, collector: 'FileCollector'):
        self._collector = collector

    def _should_skip(self, path: str) -> bool:
        name = os.path.basename(path)
        return name.startswith('.') or '__pycache__' in path

    def on_created(self, event):
        if not event.is_directory and not self._should_skip(event.src_path):
            self._collector._emit("file_change", f"created: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory and not self._should_skip(event.src_path):
            self._collector._emit("file_change", f"modified: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory and not self._should_skip(event.src_path):
            self._collector._emit("file_change", f"deleted: {event.src_path}")


class FileCollector(BaseCollector):
    def __init__(self, device_id: str, buf=None, watched_dirs: list[str] | None = None):
        super().__init__(device_id, buf)
        self._dirs = watched_dirs if watched_dirs is not None else settings.WATCHED_DIRS
        self._observer: Observer | None = None

    def start(self) -> None:
        if not self._dirs:
            logger.info("FileCollector: no watched directories configured, skipping")
            return
        self._observer = Observer()
        handler = _Handler(self)
        for d in self._dirs:
            if os.path.isdir(d):
                self._observer.schedule(handler, d, recursive=True)
                logger.info(f"Watching: {d}")
            else:
                logger.warning(f"Watched dir not found: {d}")
        self._observer.start()

    def stop(self) -> None:
        super().stop()
        if self._observer:
            self._observer.stop()
            self._observer.join()
