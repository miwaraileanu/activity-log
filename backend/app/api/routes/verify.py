from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.event import Event
from app.services.hash_chain import verify_chain

router = APIRouter(prefix="/verify", tags=["verify"])


@router.get("/{device_id}")
async def verify_device_chain(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(Event)
        .where(Event.device_id == device_id)
        .order_by(Event.timestamp.asc())
    )
    events = list(result.scalars().all())

    if not events:
        raise HTTPException(status_code=404, detail="No events found for this device.")

    return verify_chain(events)
