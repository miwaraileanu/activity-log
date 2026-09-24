from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def client():
    app.state.redis = MagicMock()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
