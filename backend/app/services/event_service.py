from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.schemas.event import EventCreate
from app.services import stream


async def ingest_batch(
    events: list[EventCreate],
    db: AsyncSession,
    redis: Redis,
) -> None:
    """Insert a batch of events into Postgres and publish each to Redis."""
    orm_events = [
        Event(
            id=e.id,
            device_id=e.device_id,
            event_type=e.event_type.value,
            text=e.text,
            timestamp=e.timestamp,
            prev_hash=e.prev_hash,
            hash=e.hash,
        )
        for e in events
    ]
    db.add_all(orm_events)
    await db.commit()

    for e in events:
        await stream.publish(redis, e.model_dump(mode="json"))


async def list_events(
    db: AsyncSession,
    device_id: Optional[uuid.UUID] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    limit: int = 100,
) -> list[Event]:
    """Query events with optional filters, ordered by timestamp ASC."""
    stmt = select(Event)

    if device_id is not None:
        stmt = stmt.where(Event.device_id == device_id)
    if since is not None:
        stmt = stmt.where(Event.timestamp >= since)
    if until is not None:
        stmt = stmt.where(Event.timestamp <= until)

    stmt = stmt.order_by(Event.timestamp.asc()).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())
