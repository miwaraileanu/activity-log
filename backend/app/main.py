from __future__ import annotations

from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import devices, events, health, verify, ws
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    app.state.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=False)
    yield
    await app.state.redis.aclose()
    await engine.dispose()


app = FastAPI(
    title="Activity Log API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(devices.router)
app.include_router(events.router)
app.include_router(verify.router)
app.include_router(ws.router)
