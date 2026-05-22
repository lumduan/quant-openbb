"""Tests for the 16 proxy endpoints defined in ``openbb_quant.router``.

Each test patches ``openbb_quant.router._client`` and asserts that the
endpoint:

1. Returns HTTP 200 with the mocked payload.
2. Delegates to ``_client.get`` with the correct gateway path.
3. Passes path and query parameters through unchanged (where applicable).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

API_PREFIX = "/api/v2"


async def _call(http_client: AsyncClient, path: str, **params: Any) -> Any:
    response = await http_client.get(f"{API_PREFIX}{path}", params=params or None)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.asyncio
async def test_get_engine_catalog(http_client: AsyncClient, mock_client: AsyncMock) -> None:
    payload = [{"slug": "portfolio", "type": "INTERNAL"}]
    mock_client.get.return_value = payload
    body = await _call(http_client, "/engines/catalog")
    assert body == payload
    mock_client.get.assert_awaited_once_with("engines/catalog")


@pytest.mark.asyncio
async def test_get_portfolio_snapshot(http_client: AsyncClient, mock_client: AsyncMock) -> None:
    payload = {"total_portfolio_value": "1000.00"}
    mock_client.get.return_value = payload
    body = await _call(http_client, "/engines/portfolio/snapshot")
    assert body == payload
    mock_client.get.assert_awaited_once_with("engines/portfolio/snapshot")


@pytest.mark.asyncio
async def test_get_portfolio_snapshot_by_date(
    http_client: AsyncClient, mock_client: AsyncMock
) -> None:
    payload = {"snapshot_date": "2026-05-22"}
    mock_client.get.return_value = payload
    body = await _call(http_client, "/engines/portfolio/snapshot/2026-05-22")
    assert body == payload
    mock_client.get.assert_awaited_once_with("engines/portfolio/snapshot/2026-05-22")


@pytest.mark.asyncio
async def test_get_portfolio_equity_curve_default_normalize(
    http_client: AsyncClient, mock_client: AsyncMock
) -> None:
    payload = [{"date": "2026-05-22", "value": "1.00"}]
    mock_client.get.return_value = payload
    body = await _call(http_client, "/engines/portfolio/equity-curve")
    assert body == payload
    mock_client.get.assert_awaited_once_with("engines/portfolio/equity-curve", normalize=True)


@pytest.mark.asyncio
async def test_get_portfolio_equity_curve_normalize_false(
    http_client: AsyncClient, mock_client: AsyncMock
) -> None:
    mock_client.get.return_value = []
    await _call(http_client, "/engines/portfolio/equity-curve", normalize="false")
    mock_client.get.assert_awaited_once_with("engines/portfolio/equity-curve", normalize=False)


@pytest.mark.asyncio
async def test_get_portfolio_overall_performance(
    http_client: AsyncClient, mock_client: AsyncMock
) -> None:
    payload = {"total_portfolio_value": "1000.00", "strategies": []}
    mock_client.get.return_value = payload
    body = await _call(http_client, "/engines/portfolio/overall-performance")
    assert body == payload
    mock_client.get.assert_awaited_once_with("engines/portfolio/overall-performance")


@pytest.mark.asyncio
async def test_list_portfolio_strategies(http_client: AsyncClient, mock_client: AsyncMock) -> None:
    payload = [{"id": "csm-set", "name": "CSM-SET"}]
    mock_client.get.return_value = payload
    body = await _call(http_client, "/engines/portfolio/strategies")
    assert body == payload
    mock_client.get.assert_awaited_once_with("engines/portfolio/strategies")


@pytest.mark.asyncio
async def test_get_portfolio_strategy(http_client: AsyncClient, mock_client: AsyncMock) -> None:
    payload = {"id": "csm-set"}
    mock_client.get.return_value = payload
    body = await _call(http_client, "/engines/portfolio/strategies/csm-set")
    assert body == payload
    mock_client.get.assert_awaited_once_with("engines/portfolio/strategies/csm-set")


@pytest.mark.asyncio
async def test_get_portfolio_strategy_performance_no_dates(
    http_client: AsyncClient, mock_client: AsyncMock
) -> None:
    payload = {"strategy_id": "csm-set"}
    mock_client.get.return_value = payload
    body = await _call(
        http_client,
        "/engines/portfolio/strategies/csm-set/performance",
    )
    assert body == payload
    mock_client.get.assert_awaited_once_with(
        "engines/portfolio/strategies/csm-set/performance",
        from_date=None,
        to_date=None,
    )


@pytest.mark.asyncio
async def test_get_portfolio_strategy_performance_with_dates(
    http_client: AsyncClient, mock_client: AsyncMock
) -> None:
    mock_client.get.return_value = []
    await _call(
        http_client,
        "/engines/portfolio/strategies/csm-set/performance",
        from_date="2026-05-01",
        to_date="2026-05-22",
    )
    mock_client.get.assert_awaited_once_with(
        "engines/portfolio/strategies/csm-set/performance",
        from_date="2026-05-01",
        to_date="2026-05-22",
    )


@pytest.mark.asyncio
async def test_get_portfolio_strategy_equity_curve(
    http_client: AsyncClient, mock_client: AsyncMock
) -> None:
    payload = [{"date": "2026-05-22", "value": "1.0"}]
    mock_client.get.return_value = payload
    body = await _call(http_client, "/engines/portfolio/strategies/csm-set/equity-curve")
    assert body == payload
    mock_client.get.assert_awaited_once_with("engines/portfolio/strategies/csm-set/equity-curve")


@pytest.mark.asyncio
async def test_get_backtest_strategy_report(
    http_client: AsyncClient, mock_client: AsyncMock
) -> None:
    payload = {"strategy_id": "csm-set"}
    mock_client.get.return_value = payload
    body = await _call(
        http_client,
        "/engines/backtest/strategies/csm-set/report",
        date="2026-05-22",
    )
    assert body == payload
    mock_client.get.assert_awaited_once_with(
        "engines/backtest/strategies/csm-set/report",
        date="2026-05-22",
    )


@pytest.mark.asyncio
async def test_get_backtest_strategy_report_no_date(
    http_client: AsyncClient, mock_client: AsyncMock
) -> None:
    mock_client.get.return_value = {}
    await _call(http_client, "/engines/backtest/strategies/csm-set/report")
    mock_client.get.assert_awaited_once_with(
        "engines/backtest/strategies/csm-set/report",
        date=None,
    )


@pytest.mark.asyncio
async def test_get_backtest_strategy_trades(
    http_client: AsyncClient, mock_client: AsyncMock
) -> None:
    payload = {"items": [], "total": 0, "limit": 50, "offset": 10}
    mock_client.get.return_value = payload
    body = await _call(
        http_client,
        "/engines/backtest/strategies/csm-set/trades",
        from_date="2026-01-01",
        to_date="2026-05-22",
        limit=50,
        offset=10,
    )
    assert body == payload
    mock_client.get.assert_awaited_once_with(
        "engines/backtest/strategies/csm-set/trades",
        from_date="2026-01-01",
        to_date="2026-05-22",
        limit=50,
        offset=10,
    )


@pytest.mark.asyncio
async def test_get_backtest_strategy_trades_defaults(
    http_client: AsyncClient, mock_client: AsyncMock
) -> None:
    mock_client.get.return_value = {"items": []}
    await _call(http_client, "/engines/backtest/strategies/csm-set/trades")
    mock_client.get.assert_awaited_once_with(
        "engines/backtest/strategies/csm-set/trades",
        from_date=None,
        to_date=None,
        limit=100,
        offset=0,
    )


@pytest.mark.asyncio
async def test_get_backtest_strategy_benchmark_curve(
    http_client: AsyncClient, mock_client: AsyncMock
) -> None:
    payload = [{"date": "2026-05-22T00:00:00Z", "value": "100.0"}]
    mock_client.get.return_value = payload
    body = await _call(
        http_client,
        "/engines/backtest/strategies/csm-set/benchmark-curve",
        normalize="true",
    )
    assert body == payload
    mock_client.get.assert_awaited_once_with(
        "engines/backtest/strategies/csm-set/benchmark-curve",
        from_date=None,
        to_date=None,
        normalize=True,
    )


@pytest.mark.asyncio
async def test_get_market_data_health(http_client: AsyncClient, mock_client: AsyncMock) -> None:
    payload = {"status": "stub", "engine": "market-data"}
    mock_client.get.return_value = payload
    body = await _call(http_client, "/engines/market-data/health")
    assert body == payload
    mock_client.get.assert_awaited_once_with("engines/market-data/health")


@pytest.mark.asyncio
async def test_get_market_data_providers(http_client: AsyncClient, mock_client: AsyncMock) -> None:
    payload = {"providers": ["settfex", "tvkit"], "status": "ok"}
    mock_client.get.return_value = payload
    body = await _call(http_client, "/engines/market-data/providers")
    assert body == payload
    mock_client.get.assert_awaited_once_with("engines/market-data/providers")


@pytest.mark.asyncio
async def test_get_signals_health(http_client: AsyncClient, mock_client: AsyncMock) -> None:
    payload = {"status": "stub", "engine": "signals"}
    mock_client.get.return_value = payload
    body = await _call(http_client, "/engines/signals/health")
    assert body == payload
    mock_client.get.assert_awaited_once_with("engines/signals/health")


@pytest.mark.asyncio
async def test_get_signals_status(http_client: AsyncClient, mock_client: AsyncMock) -> None:
    payload = {"status": "dormant", "message": "engine offline"}
    mock_client.get.return_value = payload
    body = await _call(http_client, "/engines/signals/status")
    assert body == payload
    mock_client.get.assert_awaited_once_with("engines/signals/status")


@pytest.mark.asyncio
async def test_health_endpoint(full_http_client: AsyncClient) -> None:
    """The standalone /health endpoint serves the Docker HEALTHCHECK."""
    response = await full_http_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
