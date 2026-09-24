from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.services.hash_chain import compute_hash, verify_chain

GENESIS = "0" * 64


def test_compute_hash_returns_hex_string():
    h = compute_hash(GENESIS, "abc", "2024-01-01T00:00:00Z", "hello")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_compute_hash_is_deterministic():
    a = compute_hash(GENESIS, "id1", "2024-01-01T00:00:00Z", "text")
    b = compute_hash(GENESIS, "id1", "2024-01-01T00:00:00Z", "text")
    assert a == b


def test_compute_hash_changes_on_text_diff():
    a = compute_hash(GENESIS, "id1", "2024-01-01T00:00:00Z", "text")
    b = compute_hash(GENESIS, "id1", "2024-01-01T00:00:00Z", "textx")
    assert a != b


def test_verify_chain_empty():
    assert verify_chain([]) == {"valid": True}


def _make_chain(texts: list[str]) -> list[SimpleNamespace]:
    """Build a correctly-chained list of fake event objects."""
    events = []
    prev = GENESIS
    for i, text in enumerate(texts):
        id_ = f"id-{i}"
        ts = datetime(2024, 1, 1, 0, 0, i, tzinfo=timezone.utc)
        ts_str = ts.isoformat()
        h = compute_hash(prev, id_, ts_str, text)
        e = SimpleNamespace(id=id_, timestamp=ts, text=text, prev_hash=prev, hash=h)
        events.append(e)
        prev = h
    return events


def test_verify_chain_valid():
    events = _make_chain(["alpha", "beta", "gamma"])
    result = verify_chain(events)
    assert result.get("valid") is True


def test_verify_chain_detects_tampered_text():
    events = _make_chain(["alpha", "beta", "gamma"])
    # Tamper text at index 1 without updating the hash
    events[1] = SimpleNamespace(
        id=events[1].id,
        timestamp=events[1].timestamp,
        text="TAMPERED",
        prev_hash=events[1].prev_hash,
        hash=events[1].hash,
    )
    result = verify_chain(events)
    assert result["valid"] is False
    assert result["broken_at"] == 1


def test_verify_chain_detects_broken_prev_link():
    events = _make_chain(["alpha", "beta"])
    # Break the prev_hash link on event 1
    events[1] = SimpleNamespace(
        id=events[1].id,
        timestamp=events[1].timestamp,
        text=events[1].text,
        prev_hash="wrong" + "0" * 59,
        hash=events[1].hash,
    )
    result = verify_chain(events)
    assert result["valid"] is False
