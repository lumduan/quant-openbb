"""Documentation-level Pydantic models for the most-used gateway responses.

The proxy router returns raw JSON dicts (gateway responses verbatim) — these
models exist only for IDE assistance, mypy narrowing, and future type-safe
client code. They mirror the canonical shapes defined in
``quant-api-gateway/src/api/v2/schemas``.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class EquityPoint(BaseModel):
    """A single (date, value) point on an equity curve."""

    model_config = ConfigDict(extra="allow")

    date: str
    value: Decimal


class StrategyPerformance(BaseModel):
    """Daily performance row for a single strategy."""

    model_config = ConfigDict(extra="allow")

    strategy_id: str
    daily_pnl: Decimal
    total_value: Decimal
    max_drawdown: Decimal
    sharpe_ratio: Decimal
    last_updated: datetime


class StrategyConfig(BaseModel):
    """Persistent configuration for a strategy registered in the gateway."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    type: str
    service_url: str
    capital_weight: Decimal
    active: bool


class PortfolioSnapshot(BaseModel):
    """Capital-weighted portfolio snapshot for a single date."""

    model_config = ConfigDict(extra="allow")

    snapshot_date: date
    total_portfolio_value: Decimal
    weighted_daily_return: Decimal
    combined_drawdown: Decimal | None
    active_strategies: int
    allocation: dict[str, Decimal]
    computed_at: datetime


class OverallPerformance(BaseModel):
    """Aggregate portfolio performance across all active strategies."""

    model_config = ConfigDict(extra="allow")

    total_portfolio_value: Decimal
    weighted_daily_return: Decimal
    combined_max_drawdown: Decimal
    active_strategies: int
    allocation: dict[str, Decimal]
    strategies: list[StrategyPerformance]
    computed_at: datetime


class EngineEntry(BaseModel):
    """One row of the ``/engines/catalog`` response."""

    model_config = ConfigDict(extra="allow")

    slug: str
    type: str
    status: str
    description: str


class StrategyReportResponse(BaseModel):
    """Wrapper around the gateway strategy-report payload.

    The ``report`` field carries the strategy-specific KPIs, profit
    structure, and returns table as raw JSON — kept as ``dict[str, Any]``
    so downstream consumers can navigate strategy-specific shapes without
    breaking when extra keys are added gateway-side.
    """

    model_config = ConfigDict(extra="allow")

    strategy_id: str
    as_of: str
    report: dict[str, Any]


class TradeLogResponse(BaseModel):
    """Paginated trades for a single strategy.

    Individual trade rows vary in shape across strategy types (CSM-SET vs.
    TFEX vs. future engines), so ``items`` is intentionally typed as
    ``list[dict[str, Any]]`` rather than a concrete row model. Pagination
    metadata is the same across strategies.
    """

    model_config = ConfigDict(extra="allow")

    items: list[dict[str, Any]]
    total: int
    limit: int
    offset: int
