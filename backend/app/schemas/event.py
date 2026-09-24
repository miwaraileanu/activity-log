from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class EventType(str, Enum):
    process_start = "process_start"
    process_stop = "process_stop"
    window_focus = "window_focus"
    file_change = "file_change"


class EventCreate(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    event_type: EventType
    text: str
    timestamp: datetime
    prev_hash: str
    hash: str


class EventBatchCreate(BaseModel):
    events: list[EventCreate]


class EventResponse(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    event_type: EventType
    text: str
    timestamp: datetime
    prev_hash: str
    hash: str

    model_config = ConfigDict(from_attributes=True)
