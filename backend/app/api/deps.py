from __future__ import annotations

from fastapi import Request
from redis.asyncio import Redis

from app.db.session import get_db


async def get_redis(request: Request) -> Redis:
    return request.app.state.redis


__all__ = ["get_db", "get_redis"]
