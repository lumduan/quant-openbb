"""Tests for ``openbb_quant.client.GatewayClient``.

Uses ``respx`` to mock httpx at the transport level so we exercise the real
client code path (retry, backoff, header injection, status handling) without
network I/O.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest
import pytest_asyncio
import respx

from openbb_quant.client import GatewayClient

BASE_URL = "http://gateway.test/api/v2"
API_KEY = "test-api-key-123"


@pytest_asyncio.fixture
async def fast_client() -> AsyncIterator[GatewayClient]:
    """A client with zero backoff so retry tests run instantly."""
    client = GatewayClient(
        base_url=BASE_URL,
        api_key=API_KEY,
        backoff_seconds=(0.0, 0.0, 0.0),
    )
    try:
        yield client
    finally:
        await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_get_injects_x_api_key_header(fast_client: GatewayClient) -> None:
    route = respx.get(f"{BASE_URL}/engines/catalog").mock(
        return_value=httpx.Response(200, json=[{"slug": "portfolio"}]),
    )
    body = await fast_client.get("engines/catalog")
    assert body == [{"slug": "portfolio"}]
    assert route.called
    sent_headers = route.calls.last.request.headers
    assert sent_headers["X-API-Key"] == API_KEY


@pytest.mark.asyncio
@respx.mock
async def test_get_strips_none_query_params(fast_client: GatewayClient) -> None:
    route = respx.get(f"{BASE_URL}/engines/portfolio/equity-curve").mock(
        return_value=httpx.Response(200, json=[]),
    )
    await fast_client.get(
        "engines/portfolio/equity-curve",
        normalize=True,
        from_date=None,
    )
    assert route.called
    sent_params = dict(route.calls.last.request.url.params)
    assert sent_params == {"normalize": "true"}


@pytest.mark.asyncio
@respx.mock
async def test_get_passes_query_params(fast_client: GatewayClient) -> None:
    route = respx.get(f"{BASE_URL}/engines/backtest/strategies/csm-set/trades").mock(
        return_value=httpx.Response(200, json={"items": []}),
    )
    await fast_client.get(
        "engines/backtest/strategies/csm-set/trades",
        limit=50,
        offset=10,
    )
    sent_params = dict(route.calls.last.request.url.params)
    assert sent_params == {"limit": "50", "offset": "10"}


@pytest.mark.asyncio
@respx.mock
async def test_get_retries_on_5xx_then_succeeds(fast_client: GatewayClient) -> None:
    route = respx.get(f"{BASE_URL}/engines/catalog").mock(
        side_effect=[
            httpx.Response(503, text="unavailable"),
            httpx.Response(502, text="bad gateway"),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    body = await fast_client.get("engines/catalog")
    assert body == {"ok": True}
    assert route.call_count == 3


@pytest.mark.asyncio
@respx.mock
async def test_get_raises_after_max_attempts_on_5xx(fast_client: GatewayClient) -> None:
    route = respx.get(f"{BASE_URL}/engines/catalog").mock(
        return_value=httpx.Response(500, text="boom"),
    )
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        await fast_client.get("engines/catalog")
    assert excinfo.value.response.status_code == 500
    assert route.call_count == 3


@pytest.mark.asyncio
@respx.mock
async def test_get_raises_immediately_on_4xx(fast_client: GatewayClient) -> None:
    route = respx.get(f"{BASE_URL}/engines/portfolio/snapshot").mock(
        return_value=httpx.Response(404, text="not found"),
    )
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        await fast_client.get("engines/portfolio/snapshot")
    assert excinfo.value.response.status_code == 404
    assert route.call_count == 1


@pytest.mark.asyncio
@respx.mock
async def test_get_path_strips_leading_slash(fast_client: GatewayClient) -> None:
    route = respx.get(f"{BASE_URL}/engines/catalog").mock(
        return_value=httpx.Response(200, json=[]),
    )
    await fast_client.get("/engines/catalog")
    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_get_retries_on_network_error(fast_client: GatewayClient) -> None:
    route = respx.get(f"{BASE_URL}/engines/catalog").mock(
        side_effect=[
            httpx.ConnectError("dns failure"),
            httpx.Response(200, json=[]),
        ]
    )
    body = await fast_client.get("engines/catalog")
    assert body == []
    assert route.call_count == 2


@pytest.mark.asyncio
async def test_client_close_is_idempotent() -> None:
    client = GatewayClient(base_url=BASE_URL, api_key=API_KEY)
    await client.close()
    await client.close()  # second close must not raise


@pytest.mark.asyncio
@respx.mock
async def test_async_context_manager() -> None:
    respx.get(f"{BASE_URL}/engines/catalog").mock(
        return_value=httpx.Response(200, json=[]),
    )
    async with GatewayClient(
        base_url=BASE_URL,
        api_key=API_KEY,
        backoff_seconds=(0.0,),
    ) as client:
        body: Any = await client.get("engines/catalog")
        assert body == []
