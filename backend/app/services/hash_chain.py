from __future__ import annotations

import hashlib
import json
from typing import Any


def compute_hash(prev_hash: str, id: Any, timestamp: str, text: str) -> str:
    """Compute SHA-256 hash of [prev_hash, id, timestamp, text].

    The payload is byte-identical to the frontend JS:
        JSON.stringify([prevHash, id, timestamp, text])
    """
    payload = json.dumps(
        [prev_hash, str(id), timestamp, text],
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_chain(events: list[Any]) -> dict:
    """Verify the hash chain integrity of a list of events.

    Events must be ordered by timestamp ASC (as stored).
    Returns {"valid": True} if all hashes are consistent,
    or {"valid": False, "broken_at": i, "event_id": str(event.id)} on failure.
    """
    if not events:
        return {"valid": True}

    for i, event in enumerate(events):
        # The timestamp stored in the DB is a datetime; convert to ISO string
        # matching what was originally used when computing the hash.
        ts = event.timestamp
        if hasattr(ts, "isoformat"):
            timestamp_str = ts.isoformat()
        else:
            timestamp_str = str(ts)

        expected = compute_hash(event.prev_hash, event.id, timestamp_str, event.text)
        if expected != event.hash:
            return {"valid": False, "broken_at": i, "event_id": str(event.id)}

        # Check prev_hash link: event[i].prev_hash must equal event[i-1].hash
        if i > 0 and event.prev_hash != events[i - 1].hash:
            return {"valid": False, "broken_at": i, "event_id": str(event.id)}

    return {"valid": True}
