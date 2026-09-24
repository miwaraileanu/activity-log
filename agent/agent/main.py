import asyncio
import logging
import sys
from agent.config import settings
from agent.buffer import buffer
from agent.client import register_device, send_batch, close_client
from agent.collectors.processes import ProcessCollector
from agent.collectors.active_window import ActiveWindowCollector
from agent.collectors.files import FileCollector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def run() -> None:
    logger.info(f"Registering device: {settings.DEVICE_NAME}")
    try:
        device_id = await register_device(settings.DEVICE_NAME)
        logger.info(f"Device ID: {device_id}")
    except Exception as e:
        logger.warning(f"Could not reach API ({e}), running in offline/console mode")
        device_id = "offline"

    collectors = [
        ProcessCollector(device_id),
        ActiveWindowCollector(device_id),
        FileCollector(device_id),
    ]
    for c in collectors:
        c.start()
        logger.info(f"Started {c.__class__.__name__}")

    logger.info(f"Polling every {settings.POLL_INTERVAL}s — Ctrl+C to stop")
    try:
        while True:
            await asyncio.sleep(settings.POLL_INTERVAL)
            events = buffer.flush()
            if not events:
                continue
            if device_id == "offline":
                for e in events:
                    print(f"[{e['event_type']}] {e['text']}")
            else:
                try:
                    await send_batch(events)
                except Exception as e:
                    logger.error(f"Send failed, events lost: {e}")
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Shutting down...")
    finally:
        for c in collectors:
            c.stop()
        # Flush remaining
        remaining = buffer.flush()
        if remaining and device_id != "offline":
            try:
                await send_batch(remaining)
            except Exception:
                pass
        await close_client()
        logger.info("Agent stopped")


if __name__ == "__main__":
    asyncio.run(run())
