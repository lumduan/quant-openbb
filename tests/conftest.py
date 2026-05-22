"""Shared fixtures for the openbb_quant test suite."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from openbb_quant.main import app as application
from openbb_quant.router import router


@pytest.fixture
def app() -> FastAPI:
    """FastAPI app with the proxy router mounted (no CORS middleware)."""
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
def full_app() -> FastAPI:
    """The production FastAPI app (used to exercise /health)."""
    return application


@pytest.fixture
def mock_client() -> Iterator[AsyncMock]:
    """Patch ``openbb_quant.router._client`` with an AsyncMock.

    Each test that uses this fixture gets a fresh mock; ``mock_client.get``
    returns ``{"status": "ok"}`` by default. Tests may override the
    ``return_value`` or ``side_effect`` as needed.
    """
    with patch("openbb_quant.router._client") as mock:
        mock.get = AsyncMock(return_value={"status": "ok"})
        yield mock


@pytest_asyncio.fixture
async def http_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """An ``httpx.AsyncClient`` bound to the test app via ASGITransport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def full_http_client(full_app: FastAPI) -> AsyncIterator[AsyncClient]:
    """``AsyncClient`` bound to the full production app (for /health)."""
    transport = ASGITransport(app=full_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


def fixture_response(payload: Any) -> Any:
    """Return a payload suitable for ``AsyncMock.return_value``."""
    return payload
