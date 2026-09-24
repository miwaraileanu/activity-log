from __future__ import annotations

import json

from redis.asyncio import Redis

STREAM_KEY = "stream:events"
PUBSUB_CHANNEL = "events:live"
CONSUMER_GROUP = "workers"


async def create_consumer_group(redis: Redis) -> None:
    """Create the consumer group for the events stream.

    Swallows BUSYGROUP error if the group already exists.
    """
    try:
        await redis.xgroup_create(STREAM_KEY, CONSUMER_GROUP, id="0", mkstream=True)
    except Exception as e:
        if "BUSYGROUP" not in str(e):
            raise


async def publish(redis: Redis, event_dict: dict) -> None:
    """Publish an event to the Redis stream and pub/sub channel."""
    payload = json.dumps(event_dict, default=str)
    fields = {"data": payload}
    await redis.xadd(STREAM_KEY, fields)
    await redis.publish(PUBSUB_CHANNEL, payload)
