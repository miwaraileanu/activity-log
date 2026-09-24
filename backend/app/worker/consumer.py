from __future__ import annotations

import asyncio
import json
import logging

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.event import Event
from app.services.stream import CONSUMER_GROUP, STREAM_KEY

logger = logging.getLogger(__name__)
CONSUMER_NAME = "worker-1"


async def consume_loop(session_factory: async_sessionmaker, redis: Redis) -> None:
    """Infinite loop that reads events from the Redis stream and writes them to Postgres."""
    logger.info("Worker started, waiting for messages...")
    while True:
        try:
            results = await redis.xreadgroup(
                CONSUMER_GROUP,
                CONSUMER_NAME,
                {STREAM_KEY: ">"},
                count=100,
                block=2000,
            )
            if not results:
                continue

            for _stream, messages in results:
                for msg_id, fields in messages:
                    try:
                        raw = fields[b"data"] if b"data" in fields else fields["data"]
                        data = json.loads(raw)

                        async with session_factory() as db:
                            event = Event(
                                id=data["id"],
                                device_id=data["device_id"],
                                event_type=data["event_type"],
                                text=data["text"],
                                timestamp=data["timestamp"],
                                prev_hash=data["prev_hash"],
                                hash=data["hash"],
                            )
                            db.add(event)
                            await db.commit()

                        await redis.xack(STREAM_KEY, CONSUMER_GROUP, msg_id)
                    except Exception as e:
                        logger.error("Failed to process message %s: %s", msg_id, e)
        except Exception as e:
            logger.error("Consumer loop error: %s", e)
            await asyncio.sleep(1)
