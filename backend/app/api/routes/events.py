from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_redis
from app.schemas.event import EventBatchCreate, EventResponse
from app.services import event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def ingest_events(
    batch: EventBatchCreate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    await event_service.ingest_batch(batch.events, db, redis)
    return {"accepted": len(batch.events)}


@router.get("/", response_model=list[EventResponse])
async def get_events(
    device_id: Optional[uuid.UUID] = Query(default=None),
    since: Optional[datetime] = Query(default=None),
    until: Optional[datetime] = Query(default=None),
    limit: int = Query(default=100, le=1000),
    db: AsyncSession = Depends(get_db),
) -> list[EventResponse]:
    events = await event_service.list_events(
        db,
        device_id=device_id,
        since=since,
        until=until,
        limit=limit,
    )
    return [EventResponse.model_validate(e) for e in events]
