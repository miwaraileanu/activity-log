import uuid
import json
import hashlib
import threading
from datetime import datetime, timezone
from agent.buffer import buffer as _global_buffer

GENESIS_HASH = '0' * 64


def _compute_hash(prev_hash: str, id_: str, timestamp: str, text: str) -> str:
    payload = json.dumps([prev_hash, id_, timestamp, text], separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


class BaseCollector:
    def __init__(self, device_id: str, buf=None):
        self.device_id = device_id
        self.buf = buf or _global_buffer
        self._prev_hash = GENESIS_HASH
        self._hash_lock = threading.Lock()
        self._stop_event = threading.Event()

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        self._stop_event.set()

    def _emit(self, event_type: str, text: str) -> None:
        id_ = str(uuid.uuid4())
        ts = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        with self._hash_lock:
            prev = self._prev_hash
            hash_ = _compute_hash(prev, id_, ts, text)
            self._prev_hash = hash_
        self.buf.add({
            "id": id_,
            "device_id": self.device_id,
            "event_type": event_type,
            "text": text,
            "timestamp": ts,
            "prev_hash": prev,
            "hash": hash_,
        })
