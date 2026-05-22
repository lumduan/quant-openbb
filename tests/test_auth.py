"""Tests for the optional inbound API-key auth dependency."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_no_key_configured_allows_all(
    no_auth_http_client: AsyncClient,
    mock_client: AsyncMock,
) -> None:
    """When key is empty, requests without X-API-Key pass through."""
    mock_client.get.return_value = {"ok": True}
    response = await no_auth_http_client.get("/api/v2/engines/catalog")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_auth_key_set_missing_header_returns_401(
    authed_http_client: AsyncClient,
) -> None:
    """When key is configured and request has no X-API-Key, return 401."""
    response = await authed_http_client.get("/api/v2/engines/catalog")
    assert response.status_code == 401
    body = response.json()
    assert "detail" in body


@pytest.mark.asyncio
async def test_auth_key_set_wrong_key_returns_401(
    authed_http_client: AsyncClient,
) -> None:
    """When key is configured and request has wrong X-API-Key, return 401."""
    response = await authed_http_client.get(
        "/api/v2/engines/catalog",
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_key_set_correct_key_passes(
    authed_http_client: AsyncClient,
    mock_client: AsyncMock,
) -> None:
    """Correct X-API-Key passes through and returns the proxied response."""
    mock_client.get.return_value = {"status": "ok"}
    response = await authed_http_client.get(
        "/api/v2/engines/catalog",
        headers={"X-API-Key": "test-api-key-123"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_client.get.assert_awaited_once_with("engines/catalog")


@pytest.mark.asyncio
async def test_auth_health_endpoint_always_open(
    full_http_client: AsyncClient,
) -> None:
    """/health is on the app, not the router, so it never requires auth."""
    response = await full_http_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
