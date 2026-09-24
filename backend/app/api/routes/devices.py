from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceResponse

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    body: DeviceCreate,
    db: AsyncSession = Depends(get_db),
) -> DeviceResponse:
    stmt = (
        insert(Device)
        .values(name=body.name)
        .on_conflict_do_nothing(index_elements=["name"])
    )
    await db.execute(stmt)
    await db.commit()

    result = await db.execute(select(Device).where(Device.name == body.name))
    device = result.scalar_one()
    return DeviceResponse.model_validate(device)


@router.get("/", response_model=list[DeviceResponse])
async def list_devices(
    db: AsyncSession = Depends(get_db),
) -> list[DeviceResponse]:
    result = await db.execute(select(Device).order_by(Device.registered_at.asc()))
    devices = result.scalars().all()
    return [DeviceResponse.model_validate(d) for d in devices]
