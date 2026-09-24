import asyncio
import logging
import httpx
from agent.config import settings

logger = logging.getLogger(__name__)

_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(base_url=settings.API_URL, timeout=10.0)
    return _client


async def close_client() -> None:
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()


async def register_device(name: str) -> str:
    client = await get_client()
    resp = await client.post("/devices", json={"name": name})
    resp.raise_for_status()
    return resp.json()["id"]


async def send_batch(events: list[dict]) -> None:
    if not events:
        return
    client = await get_client()
    for attempt in range(3):
        try:
            resp = await client.post("/events", json={"events": events})
            resp.raise_for_status()
            logger.info(f"Sent {len(events)} events")
            return
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == 2:
                logger.error(f"Failed to send batch after 3 attempts: {e}")
                raise
            wait = 2 ** attempt
            logger.warning(f"Batch send failed (attempt {attempt+1}), retrying in {wait}s: {e}")
            await asyncio.sleep(wait)
