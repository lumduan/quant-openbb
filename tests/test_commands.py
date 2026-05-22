"""Tests for the typed command layer in ``openbb_quant.commands``.

Each test patches ``openbb_quant.commands._client`` (NOT
``router._client``) via the local ``commands_mock_client`` fixture, then
asserts that the command:

1. Returns the declared Pydantic model (or list thereof).
2. Parses at least one representative field correctly.
3. Calls ``_client.get`` with the expected gateway path and kwargs.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from openbb_quant import commands
from openbb_quant.models import (
    EquityPoint,
    OverallPerformance,
    PortfolioSnapshot,
    StrategyConfig,
    StrategyReportResponse,
    TradeLogResponse,
)


@pytest.fixture
def commands_mock_client() -> Iterator[AsyncMock]:
    """Patch ``openbb_quant.commands._client`` with a fresh AsyncMock per test."""
    with patch("openbb_quant.commands._client") as mock:
        mock.get = AsyncMock()
        yield mock


# ─── Happy paths ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_equity_curve_returns_typed_points(commands_mock_client: AsyncMock) -> None:
    commands_mock_client.get.return_value = [
        {"date": "2026-05-20", "value": "1.00"},
        {"date": "2026-05-21", "value": "1.05"},
    ]
    result = await commands.equity_curve("csm-set")
    assert isinstance(result, list)
    assert all(isinstance(p, EquityPoint) for p in result)
    assert result[1].value == Decimal("1.05")
    commands_mock_client.get.assert_awaited_once_with(
        "engines/portfolio/strategies/csm-set/equity-curve"
    )


@pytest.mark.asyncio
async def test_portfolio_snapshot_default(commands_mock_client: AsyncMock) -> None:
    commands_mock_client.get.return_value = {
        "snapshot_date": "2026-05-22",
        "total_portfolio_value": "10000.00",
        "weighted_daily_return": "0.0050",
        "combined_drawdown": "-0.0125",
        "active_strategies": 2,
        "allocation": {"csm-set": "0.6", "tfex": "0.4"},
        "computed_at": "2026-05-22T03:00:00Z",
    }
    result = await commands.portfolio_snapshot()
    assert isinstance(result, PortfolioSnapshot)
    assert result.total_portfolio_value == Decimal("10000.00")
    assert result.active_strategies == 2
    commands_mock_client.get.assert_awaited_once_with("engines/portfolio/snapshot")


@pytest.mark.asyncio
async def test_overall_performance(commands_mock_client: AsyncMock) -> None:
    commands_mock_client.get.return_value = {
        "total_portfolio_value": "10000.00",
        "weighted_daily_return": "0.0030",
        "combined_max_drawdown": "-0.0250",
        "active_strategies": 1,
        "allocation": {"csm-set": "1.0"},
        "strategies": [
            {
                "strategy_id": "csm-set",
                "daily_pnl": "30.00",
                "total_value": "10000.00",
                "max_drawdown": "-0.0250",
                "sharpe_ratio": "1.42",
                "last_updated": "2026-05-22T03:00:00Z",
            }
        ],
        "computed_at": "2026-05-22T03:00:00Z",
    }
    result = await commands.overall_performance()
    assert isinstance(result, OverallPerformance)
    assert result.total_portfolio_value == Decimal("10000.00")
    assert result.strategies[0].strategy_id == "csm-set"
    commands_mock_client.get.assert_awaited_once_with("engines/portfolio/overall-performance")


@pytest.mark.asyncio
async def test_strategy_report_default(commands_mock_client: AsyncMock) -> None:
    commands_mock_client.get.return_value = {
        "strategy_id": "csm-set",
        "as_of": "2026-05-22",
        "report": {
            "headline": {"net_profit": "1234.56", "sharpe": "1.42"},
            "profit_structure": [],
            "returns": {"monthly": []},
        },
    }
    result = await commands.strategy_report("csm-set")
    assert isinstance(result, StrategyReportResponse)
    assert result.strategy_id == "csm-set"
    assert result.report["headline"]["net_profit"] == "1234.56"
    commands_mock_client.get.assert_awaited_once_with(
        "engines/backtest/strategies/csm-set/report",
        date=None,
    )


@pytest.mark.asyncio
async def test_trade_log_defaults(commands_mock_client: AsyncMock) -> None:
    commands_mock_client.get.return_value = {
        "items": [
            {
                "date": "2026-05-22",
                "direction": "long",
                "entry": "10.0",
                "exit": "11.0",
                "pnl": "1.0",
            }
        ],
        "total": 1,
        "limit": 100,
        "offset": 0,
    }
    result = await commands.trade_log("csm-set")
    assert isinstance(result, TradeLogResponse)
    assert result.total == 1
    assert result.items[0]["direction"] == "long"
    commands_mock_client.get.assert_awaited_once_with(
        "engines/backtest/strategies/csm-set/trades",
        from_date=None,
        to_date=None,
        limit=100,
        offset=0,
    )


@pytest.mark.asyncio
async def test_portfolio_equity_curve_default_normalize(
    commands_mock_client: AsyncMock,
) -> None:
    commands_mock_client.get.return_value = [{"date": "2026-05-22", "value": "1.00"}]
    result = await commands.portfolio_equity_curve()
    assert isinstance(result, list)
    assert isinstance(result[0], EquityPoint)
    assert result[0].value == Decimal("1.00")
    commands_mock_client.get.assert_awaited_once_with(
        "engines/portfolio/equity-curve",
        normalize=True,
    )


@pytest.mark.asyncio
async def test_list_strategies(commands_mock_client: AsyncMock) -> None:
    commands_mock_client.get.return_value = [
        {
            "id": "csm-set",
            "name": "CSM-SET",
            "type": "momentum",
            "service_url": "http://quant-csm-set:8000",
            "capital_weight": "1.0",
            "active": True,
        }
    ]
    result = await commands.list_strategies()
    assert isinstance(result, list)
    assert isinstance(result[0], StrategyConfig)
    assert result[0].id == "csm-set"
    assert result[0].active is True
    commands_mock_client.get.assert_awaited_once_with("engines/portfolio/strategies")


# ─── Parameter variants ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_portfolio_snapshot_with_date(commands_mock_client: AsyncMock) -> None:
    from datetime import date

    commands_mock_client.get.return_value = {
        "snapshot_date": "2026-05-20",
        "total_portfolio_value": "9500.00",
        "weighted_daily_return": "-0.0010",
        "combined_drawdown": None,
        "active_strategies": 1,
        "allocation": {"csm-set": "1.0"},
        "computed_at": "2026-05-20T03:00:00Z",
    }
    result = await commands.portfolio_snapshot(date(2026, 5, 20))
    assert result.combined_drawdown is None
    commands_mock_client.get.assert_awaited_once_with("engines/portfolio/snapshot/2026-05-20")


@pytest.mark.asyncio
async def test_trade_log_custom_pagination(commands_mock_client: AsyncMock) -> None:
    from datetime import date

    commands_mock_client.get.return_value = {
        "items": [],
        "total": 0,
        "limit": 25,
        "offset": 50,
    }
    result = await commands.trade_log(
        "csm-set",
        limit=25,
        offset=50,
        from_date=date(2026, 1, 1),
        to_date=date(2026, 5, 22),
    )
    assert result.limit == 25
    assert result.offset == 50
    commands_mock_client.get.assert_awaited_once_with(
        "engines/backtest/strategies/csm-set/trades",
        from_date="2026-01-01",
        to_date="2026-05-22",
        limit=25,
        offset=50,
    )


@pytest.mark.asyncio
async def test_equity_curve_named_id(commands_mock_client: AsyncMock) -> None:
    commands_mock_client.get.return_value = []
    await commands.equity_curve("tfex-vol")
    commands_mock_client.get.assert_awaited_once_with(
        "engines/portfolio/strategies/tfex-vol/equity-curve"
    )


@pytest.mark.asyncio
async def test_strategy_report_with_target_date(commands_mock_client: AsyncMock) -> None:
    from datetime import date

    commands_mock_client.get.return_value = {
        "strategy_id": "csm-set",
        "as_of": "2026-04-30",
        "report": {"headline": {}},
    }
    result = await commands.strategy_report("csm-set", target_date=date(2026, 4, 30))
    assert str(result.as_of) == "2026-04-30"
    commands_mock_client.get.assert_awaited_once_with(
        "engines/backtest/strategies/csm-set/report",
        date="2026-04-30",
    )


@pytest.mark.asyncio
async def test_portfolio_equity_curve_normalize_false(
    commands_mock_client: AsyncMock,
) -> None:
    commands_mock_client.get.return_value = []
    await commands.portfolio_equity_curve(normalize=False)
    commands_mock_client.get.assert_awaited_once_with(
        "engines/portfolio/equity-curve",
        normalize=False,
    )


# ─── Extra-field tolerance ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_strategy_report_tolerates_extra_keys(
    commands_mock_client: AsyncMock,
) -> None:
    """Gateway may add keys not enumerated in StrategyReportResponse — they survive."""
    commands_mock_client.get.return_value = {
        "strategy_id": "csm-set",
        "as_of": "2026-05-22",
        "report": {"headline": {}},
        "future_field_unknown_today": {"new": "shape"},
    }
    result = await commands.strategy_report("csm-set")
    assert result.strategy_id == "csm-set"
    assert result.model_dump()["future_field_unknown_today"] == {"new": "shape"}


# ─── Error propagation ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_http_status_error_propagates(commands_mock_client: AsyncMock) -> None:
    """Commands must not swallow HTTPStatusError from the underlying client."""
    request = httpx.Request("GET", "http://gateway/engines/portfolio/snapshot")
    response = httpx.Response(503, request=request)
    commands_mock_client.get.side_effect = httpx.HTTPStatusError(
        "Server error 503", request=request, response=response
    )
    with pytest.raises(httpx.HTTPStatusError):
        await commands.portfolio_snapshot()
