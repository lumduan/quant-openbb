"""Typed OpenBB provider-style commands wrapping the gateway /api/v2 surface.

Each function corresponds to a dashboard data query. All functions are async,
fully typed, and parse gateway JSON into Pydantic models before returning.

Patching for tests: replace ``openbb_quant.commands._client`` (the
module-level :class:`GatewayClient` instance below) — NOT
``openbb_quant.router._client``. Each module instantiates its own client at
import time and they are independent. See ``tests/test_commands.py`` for the
canonical fixture.

HTTP error semantics: this module does not catch :class:`httpx.HTTPStatusError`
or :class:`httpx.HTTPError`. Callers are responsible for handling network and
gateway failures. The ``examples/`` scripts demonstrate the expected pattern.
"""

from __future__ import annotations

from datetime import date

from pydantic import TypeAdapter

from openbb_quant.client import GatewayClient
from openbb_quant.config import get_settings
from openbb_quant.models import (
    EquityPoint,
    OverallPerformance,
    PortfolioSnapshot,
    StrategyConfig,
    StrategyReportResponse,
    TradeLogResponse,
)

_settings = get_settings()
_client = GatewayClient(
    base_url=_settings.gateway_base_url,
    api_key=_settings.internal_api_key.get_secret_value(),
)

_EQUITY_POINT_LIST = TypeAdapter(list[EquityPoint])
_STRATEGY_CONFIG_LIST = TypeAdapter(list[StrategyConfig])


async def equity_curve(strategy_id: str) -> list[EquityPoint]:
    """Return a single strategy's equity curve as a typed list of points."""
    raw = await _client.get(f"engines/portfolio/strategies/{strategy_id}/equity-curve")
    return _EQUITY_POINT_LIST.validate_python(raw)


async def portfolio_snapshot(snapshot_date: date | None = None) -> PortfolioSnapshot:
    """Return the capital-weighted portfolio snapshot for a date.

    With no ``snapshot_date`` the gateway returns the latest snapshot;
    passing a date returns that day's snapshot.
    """
    if snapshot_date is None:
        raw = await _client.get("engines/portfolio/snapshot")
    else:
        raw = await _client.get(f"engines/portfolio/snapshot/{snapshot_date.isoformat()}")
    return PortfolioSnapshot.model_validate(raw)


async def overall_performance() -> OverallPerformance:
    """Aggregate portfolio performance across all active strategies."""
    raw = await _client.get("engines/portfolio/overall-performance")
    return OverallPerformance.model_validate(raw)


async def strategy_report(
    strategy_id: str,
    target_date: date | None = None,
) -> StrategyReportResponse:
    """Return the strategy backtest report for ``strategy_id``.

    With no ``target_date`` the gateway returns the latest report.
    """
    raw = await _client.get(
        f"engines/backtest/strategies/{strategy_id}/report",
        date=target_date.isoformat() if target_date else None,
    )
    return StrategyReportResponse.model_validate(raw)


async def trade_log(
    strategy_id: str,
    *,
    limit: int = 100,
    offset: int = 0,
    from_date: date | None = None,
    to_date: date | None = None,
) -> TradeLogResponse:
    """Return a paginated page of trades for ``strategy_id``.

    ``from_date`` and ``to_date`` are inclusive when present. ``limit`` is
    capped to 1000 by the gateway.
    """
    raw = await _client.get(
        f"engines/backtest/strategies/{strategy_id}/trades",
        from_date=from_date.isoformat() if from_date else None,
        to_date=to_date.isoformat() if to_date else None,
        limit=limit,
        offset=offset,
    )
    return TradeLogResponse.model_validate(raw)


async def portfolio_equity_curve(normalize: bool = True) -> list[EquityPoint]:
    """Return the combined portfolio equity curve."""
    raw = await _client.get("engines/portfolio/equity-curve", normalize=normalize)
    return _EQUITY_POINT_LIST.validate_python(raw)


async def list_strategies() -> list[StrategyConfig]:
    """List the strategies registered with the gateway."""
    raw = await _client.get("engines/portfolio/strategies")
    return _STRATEGY_CONFIG_LIST.validate_python(raw)
