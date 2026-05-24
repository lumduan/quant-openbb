"""FastAPI router proxying the 16 live ``/api/v2/engines/*`` gateway endpoints.

Each endpoint delegates to ``_client.get`` with the gateway path and any
query parameters received from the caller. Responses are returned verbatim
as JSON.

``verify_api_key`` is applied as a router-level dependency so auth works
regardless of how the router is mounted (standalone main.py or full OpenBB
Platform extension discovery).
"""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query

from openbb_quant.auth import verify_api_key
from openbb_quant.client import GatewayClient
from openbb_quant.config import get_settings

_settings = get_settings()
_client = GatewayClient(
    base_url=_settings.gateway_base_url,
    api_key=_settings.internal_api_key.get_secret_value(),
)

router = APIRouter(
    prefix="/api/v2",
    tags=["quant"],
    dependencies=[Depends(verify_api_key)],
)


# ─── Engine catalog ────────────────────────────────────────────────────────


@router.get("/engines/catalog")
async def get_engine_catalog() -> Any:
    return await _client.get("engines/catalog")


# ─── Portfolio engine ──────────────────────────────────────────────────────


@router.get("/engines/portfolio/snapshot")
async def get_portfolio_snapshot() -> Any:
    return await _client.get("engines/portfolio/snapshot")


@router.get("/engines/portfolio/snapshot/{snapshot_date}")
async def get_portfolio_snapshot_by_date(snapshot_date: date) -> Any:
    return await _client.get(f"engines/portfolio/snapshot/{snapshot_date.isoformat()}")


@router.get("/engines/portfolio/equity-curve")
async def get_portfolio_equity_curve(
    normalize: bool = Query(True, description="Normalize curve to start at 1.0"),
) -> Any:
    return await _client.get("engines/portfolio/equity-curve", normalize=normalize)


@router.get("/engines/portfolio/overall-performance")
async def get_portfolio_overall_performance() -> Any:
    return await _client.get("engines/portfolio/overall-performance")


@router.get("/engines/portfolio/strategies")
async def list_portfolio_strategies() -> Any:
    return await _client.get("engines/portfolio/strategies")


@router.get("/engines/portfolio/strategies/{strategy_id}")
async def get_portfolio_strategy(strategy_id: str) -> Any:
    return await _client.get(f"engines/portfolio/strategies/{strategy_id}")


@router.get("/engines/portfolio/strategies/{strategy_id}/performance")
async def get_portfolio_strategy_performance(
    strategy_id: str,
    from_date: date | None = Query(None, description="Range start (inclusive)"),
    to_date: date | None = Query(None, description="Range end (inclusive)"),
) -> Any:
    return await _client.get(
        f"engines/portfolio/strategies/{strategy_id}/performance",
        from_date=from_date.isoformat() if from_date else None,
        to_date=to_date.isoformat() if to_date else None,
    )


@router.get("/engines/portfolio/strategies/{strategy_id}/equity-curve")
async def get_portfolio_strategy_equity_curve(strategy_id: str) -> Any:
    return await _client.get(f"engines/portfolio/strategies/{strategy_id}/equity-curve")


# ─── Backtest engine ───────────────────────────────────────────────────────


@router.get("/engines/backtest/strategies/{strategy_id}/report")
async def get_backtest_strategy_report(
    strategy_id: str,
    target_date: date | None = Query(
        None,
        alias="date",
        description="Report date (default latest)",
    ),
) -> Any:
    return await _client.get(
        f"engines/backtest/strategies/{strategy_id}/report",
        date=target_date.isoformat() if target_date else None,
    )


@router.get("/engines/backtest/strategies/{strategy_id}/trades")
async def get_backtest_strategy_trades(
    strategy_id: str,
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> Any:
    return await _client.get(
        f"engines/backtest/strategies/{strategy_id}/trades",
        from_date=from_date.isoformat() if from_date else None,
        to_date=to_date.isoformat() if to_date else None,
        limit=limit,
        offset=offset,
    )


@router.get("/engines/backtest/strategies/{strategy_id}/benchmark-curve")
async def get_backtest_strategy_benchmark_curve(
    strategy_id: str,
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    normalize: bool = Query(False),
) -> Any:
    return await _client.get(
        f"engines/backtest/strategies/{strategy_id}/benchmark-curve",
        from_date=from_date.isoformat() if from_date else None,
        to_date=to_date.isoformat() if to_date else None,
        normalize=normalize,
    )


# ─── Market data engine ────────────────────────────────────────────────────


@router.get("/engines/market-data/health")
async def get_market_data_health() -> Any:
    return await _client.get("engines/market-data/health")


@router.get("/engines/market-data/providers")
async def get_market_data_providers() -> Any:
    return await _client.get("engines/market-data/providers")


# ─── Signals engine ────────────────────────────────────────────────────────


@router.get("/engines/signals/health")
async def get_signals_health() -> Any:
    return await _client.get("engines/signals/health")


@router.get("/engines/signals/status")
async def get_signals_status() -> Any:
    return await _client.get("engines/signals/status")
