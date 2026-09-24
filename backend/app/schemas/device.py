from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DeviceCreate(BaseModel):
    name: str


class DeviceResponse(BaseModel):
    id: uuid.UUID
    name: str
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)
