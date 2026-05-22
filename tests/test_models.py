"""Round-trip tests for the documentation-level Pydantic models.

The proxy returns raw JSON; these models exist for IDE/mypy convenience.
Tests instantiate each model from a sample payload to catch regressions in
field names and types.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from openbb_quant.models import (
    EngineEntry,
    EquityPoint,
    OverallPerformance,
    PortfolioSnapshot,
    StrategyConfig,
    StrategyPerformance,
)


def test_equity_point_roundtrip() -> None:
    point = EquityPoint(date="2026-05-22", value=Decimal("1.0123"))
    assert point.value == Decimal("1.0123")


def test_strategy_performance_roundtrip() -> None:
    perf = StrategyPerformance(
        strategy_id="csm-set",
        daily_pnl=Decimal("123.45"),
        total_value=Decimal("100000.00"),
        max_drawdown=Decimal("-0.05"),
        sharpe_ratio=Decimal("1.42"),
        last_updated=datetime(2026, 5, 22, 12, 0, 0),
    )
    assert perf.strategy_id == "csm-set"
    assert perf.daily_pnl == Decimal("123.45")


def test_strategy_config_roundtrip() -> None:
    config = StrategyConfig(
        id="csm-set",
        name="CSM-SET",
        type="EQUITY",
        service_url="http://quant-csm-set:8000",
        capital_weight=Decimal("0.5"),
        active=True,
    )
    assert config.active is True


def test_portfolio_snapshot_roundtrip() -> None:
    snapshot = PortfolioSnapshot(
        snapshot_date=date(2026, 5, 22),
        total_portfolio_value=Decimal("1000000.00"),
        weighted_daily_return=Decimal("0.0123"),
        combined_drawdown=Decimal("-0.05"),
        active_strategies=2,
        allocation={"csm-set": Decimal("0.5"), "tfex": Decimal("0.5")},
        computed_at=datetime(2026, 5, 22, 16, 0, 0),
    )
    assert snapshot.active_strategies == 2


def test_portfolio_snapshot_allows_null_drawdown() -> None:
    snapshot = PortfolioSnapshot(
        snapshot_date=date(2026, 5, 22),
        total_portfolio_value=Decimal("1000000.00"),
        weighted_daily_return=Decimal("0.0"),
        combined_drawdown=None,
        active_strategies=0,
        allocation={},
        computed_at=datetime(2026, 5, 22, 16, 0, 0),
    )
    assert snapshot.combined_drawdown is None


def test_overall_performance_roundtrip() -> None:
    perf = OverallPerformance(
        total_portfolio_value=Decimal("1000000.00"),
        weighted_daily_return=Decimal("0.005"),
        combined_max_drawdown=Decimal("-0.10"),
        active_strategies=1,
        allocation={"csm-set": Decimal("1.0")},
        strategies=[],
        computed_at=datetime(2026, 5, 22, 16, 0, 0),
    )
    assert perf.active_strategies == 1


def test_engine_entry_roundtrip() -> None:
    entry = EngineEntry(
        slug="portfolio",
        type="INTERNAL",
        status="active",
        description="Portfolio aggregation engine",
    )
    assert entry.slug == "portfolio"
