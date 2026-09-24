from __future__ import annotations

import asyncio
import logging

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import AsyncSessionLocal, engine
from app.services.stream import create_consumer_group
from app.worker.consumer import consume_loop


async def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=False)
    try:
        await create_consumer_group(redis)
        logger.info("Starting consumer loop")
        await consume_loop(AsyncSessionLocal, redis)
    finally:
        await redis.aclose()
        await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
