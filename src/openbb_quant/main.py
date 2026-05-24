"""Standalone FastAPI app for ``openbb_quant``.

Used by the container CMD (``uvicorn openbb_quant.main:app``) to expose
the proxy router without depending on OpenBB Platform's full app bootstrap.
A ``/health`` endpoint is exposed for the Docker HEALTHCHECK and for
container-level liveness probes.

OpenBB Platform's built-in routers (system, commands, coverage) are also
mounted so the OpenBB Dashboard can discover widgets and invoke commands.
Our proxy router is mounted directly (not via extension discovery) to avoid
the Platform's ``build_api_wrapper`` command-wrapping pipeline, which would
replace our proxy endpoint functions.
"""

from __future__ import annotations

import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openbb_core.api.router.commands import router as router_commands
from openbb_core.api.router.coverage import router as router_coverage
from openbb_core.api.router.system import router as router_system

from openbb_quant.auth import verify_api_key
from openbb_quant.config import get_settings
from openbb_quant.router import router

_settings = get_settings()
logging.basicConfig(level=_settings.log_level)

app = FastAPI(
    title="openbb-quant",
    version="0.1.0",
    description="OpenBB router extension proxying quant-api-gateway /api/v2/engines/*",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_allow_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Proxy router — auth dependency lives on the router itself (router.py).
# The duplicate Depends here is belt-and-suspenders in case the router is
# ever mounted without its own dependency.
app.include_router(router, dependencies=[Depends(verify_api_key)])

# OpenBB Platform built-in routers — provide the widget/command surface the
# OpenBB Dashboard needs. Mounted at /api/v1 to match standard Platform layout.
app.include_router(router_system, prefix="/api/v1")
app.include_router(router_coverage, prefix="/api/v1")
app.include_router(router_commands, prefix="/api/v1")


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness probe used by the container HEALTHCHECK."""
    return {"status": "ok"}


@app.get("/widgets.json", tags=["meta"])
async def widgets_manifest() -> dict[str, object]:
    """OpenBB Workspace widget manifest for the 16 quant proxy endpoints."""
    return _build_widgets_manifest()


@app.get("/apps.json", tags=["meta"])
async def apps_manifest() -> list[dict[str, object]]:
    """OpenBB Workspace dashboard app templates.

    Returns a single default app that lays out the core quant widgets.
    Users can export custom layouts from the Workspace UI and save them
    here to share with their team.
    """
    return _build_apps_manifest()


@app.get("/agents.json", tags=["meta"])
async def agents_manifest() -> dict[str, object]:
    """OpenBB Workspace AI agent definitions.

    Returns a minimal quant-aware agent that can query the gateway
    through the widget endpoints.
    """
    return _build_agents_manifest()


@app.get("/templates.json", tags=["meta"])
async def templates_manifest() -> list[dict[str, object]]:
    """Alias for /apps.json — some Workspace versions request templates.json."""
    return _build_apps_manifest()


# ---------------------------------------------------------------------------
# Widget manifest builder
# ---------------------------------------------------------------------------


def _table_with_chart(chart_type: str = "line") -> dict[str, object]:
    """Return a ``data.table`` config enabling chart view for a table widget."""
    return {
        "table": {
            "enableCharts": True,
            "chartView": {"enabled": True, "chartType": chart_type},
        },
    }


_WIDGET_DEFS: list[dict[str, object]] = [
    # ── Engine catalog ──────────────────────────────────────────────────
    {
        "id": "engine_catalog",
        "name": "Engine Catalog",
        "description": (
            "List all registered quant engines "
            "(market-data, backtest, portfolio, signals) with type and status."
        ),
        "endpoint": "/api/v2/engines/catalog",
        "category": "Quant",
        "type": "table",
    },
    # ── Portfolio engine ────────────────────────────────────────────────
    {
        "id": "portfolio_snapshot",
        "name": "Portfolio Snapshot",
        "description": "Latest combined portfolio snapshot across all active strategies.",
        "endpoint": "/api/v2/engines/portfolio/snapshot",
        "category": "Quant",
        "type": "table",
    },
    {
        "id": "portfolio_snapshot_by_date",
        "name": "Portfolio Snapshot by Date",
        "description": "Combined portfolio snapshot for a specific date.",
        "endpoint": "/api/v2/engines/portfolio/snapshot/{snapshot_date}",
        "category": "Quant",
        "type": "table",
        "params": [
            {
                "type": "date",
                "paramName": "snapshot_date",
                "value": "$currentDate-1d",
                "label": "Snapshot Date",
                "description": "Date to retrieve the portfolio snapshot for.",
            },
        ],
    },
    {
        "id": "portfolio_equity_curve",
        "name": "Portfolio Equity Curve",
        "description": "Combined equity curve across all strategies, optionally normalized to 1.0.",
        "endpoint": "/api/v2/engines/portfolio/equity-curve",
        "category": "Quant",
        "type": "table",
        "data": _table_with_chart("line"),
        "params": [
            {
                "type": "boolean",
                "paramName": "normalize",
                "value": True,
                "label": "Normalize",
                "description": "Normalize curve to start at 1.0.",
            },
        ],
    },
    {
        "id": "portfolio_overall_performance",
        "name": "Overall Performance",
        "description": "Capital-weighted aggregate performance metrics across all strategies.",
        "endpoint": "/api/v2/engines/portfolio/overall-performance",
        "category": "Quant",
        "type": "table",
    },
    {
        "id": "portfolio_strategies",
        "name": "Strategy List",
        "description": "List all registered portfolio strategies with their capital weights.",
        "endpoint": "/api/v2/engines/portfolio/strategies",
        "category": "Quant",
        "type": "table",
    },
    {
        "id": "portfolio_strategy_detail",
        "name": "Strategy Detail",
        "description": "Metadata and status for a single strategy by id.",
        "endpoint": "/api/v2/engines/portfolio/strategies/{strategy_id}",
        "category": "Quant",
        "type": "table",
        "params": [
            {
                "type": "text",
                "paramName": "strategy_id",
                "value": "csm-set",
                "label": "Strategy ID",
                "description": "Strategy identifier (e.g. csm-set).",
            },
        ],
    },
    {
        "id": "portfolio_strategy_performance",
        "name": "Strategy Performance",
        "description": "Performance metrics for a single strategy, optionally date-ranged.",
        "endpoint": "/api/v2/engines/portfolio/strategies/{strategy_id}/performance",
        "category": "Quant",
        "type": "table",
        "params": [
            {
                "type": "text",
                "paramName": "strategy_id",
                "value": "csm-set",
                "label": "Strategy ID",
            },
            {
                "type": "date",
                "paramName": "from_date",
                "value": None,
                "label": "From Date",
                "description": "Range start (inclusive).",
            },
            {
                "type": "date",
                "paramName": "to_date",
                "value": None,
                "label": "To Date",
                "description": "Range end (inclusive).",
            },
        ],
    },
    {
        "id": "portfolio_strategy_equity_curve",
        "name": "Strategy Equity Curve",
        "description": "Equity curve for a single strategy.",
        "endpoint": "/api/v2/engines/portfolio/strategies/{strategy_id}/equity-curve",
        "category": "Quant",
        "type": "table",
        "data": _table_with_chart("line"),
        "params": [
            {
                "type": "text",
                "paramName": "strategy_id",
                "value": "csm-set",
                "label": "Strategy ID",
            },
        ],
    },
    # ── Backtest engine ─────────────────────────────────────────────────
    {
        "id": "backtest_strategy_report",
        "name": "Backtest Report",
        "description": "Walk-forward backtest report for a strategy, optionally for a target date.",
        "endpoint": "/api/v2/engines/backtest/strategies/{strategy_id}/report",
        "category": "Quant",
        "type": "table",
        "params": [
            {
                "type": "text",
                "paramName": "strategy_id",
                "value": "csm-set",
                "label": "Strategy ID",
            },
            {
                "type": "date",
                "paramName": "date",
                "value": "$currentDate-1d",
                "label": "Report Date",
                "description": "Report date (defaults to latest).",
            },
        ],
    },
    {
        "id": "backtest_strategy_trades",
        "name": "Trade Log",
        "description": "Paginated trade history for a backtested strategy.",
        "endpoint": "/api/v2/engines/backtest/strategies/{strategy_id}/trades",
        "category": "Quant",
        "type": "table",
        "params": [
            {
                "type": "text",
                "paramName": "strategy_id",
                "value": "csm-set",
                "label": "Strategy ID",
            },
            {
                "type": "date",
                "paramName": "from_date",
                "value": None,
                "label": "From Date",
            },
            {
                "type": "date",
                "paramName": "to_date",
                "value": None,
                "label": "To Date",
            },
            {
                "type": "number",
                "paramName": "limit",
                "value": 100,
                "label": "Limit",
                "description": "Max results (1–1000).",
            },
            {
                "type": "number",
                "paramName": "offset",
                "value": 0,
                "label": "Offset",
            },
        ],
    },
    {
        "id": "backtest_strategy_benchmark",
        "name": "Benchmark Curve",
        "description": "Benchmark comparison curve for a backtested strategy.",
        "endpoint": "/api/v2/engines/backtest/strategies/{strategy_id}/benchmark-curve",
        "category": "Quant",
        "type": "table",
        "data": _table_with_chart("line"),
        "params": [
            {
                "type": "text",
                "paramName": "strategy_id",
                "value": "csm-set",
                "label": "Strategy ID",
            },
            {
                "type": "date",
                "paramName": "from_date",
                "value": None,
                "label": "From Date",
            },
            {
                "type": "date",
                "paramName": "to_date",
                "value": None,
                "label": "To Date",
            },
            {
                "type": "boolean",
                "paramName": "normalize",
                "value": False,
                "label": "Normalize",
            },
        ],
    },
    # ── Market data engine ──────────────────────────────────────────────
    {
        "id": "market_data_health",
        "name": "Market Data Health",
        "description": "Health check for the market data engine (settfex + tvkit).",
        "endpoint": "/api/v2/engines/market-data/health",
        "category": "Quant",
        "type": "table",
    },
    {
        "id": "market_data_providers",
        "name": "Market Data Providers",
        "description": "List available market data providers and their status.",
        "endpoint": "/api/v2/engines/market-data/providers",
        "category": "Quant",
        "type": "table",
    },
    # ── Signals engine ──────────────────────────────────────────────────
    {
        "id": "signals_health",
        "name": "Signals Health",
        "description": "Health check for the signals engine (currently dormant).",
        "endpoint": "/api/v2/engines/signals/health",
        "category": "Quant",
        "type": "table",
    },
    {
        "id": "signals_status",
        "name": "Signals Status",
        "description": "Operational status of the signal generation pipeline.",
        "endpoint": "/api/v2/engines/signals/status",
        "category": "Quant",
        "type": "table",
    },
]


def _build_widgets_manifest() -> dict[str, object]:
    """Build the widgets.json payload from ``_WIDGET_DEFS``."""
    manifest: dict[str, object] = {}
    for w in _WIDGET_DEFS:
        widget_id: str = w["id"]  # type: ignore[assignment]
        manifest[widget_id] = {
            "name": w["name"],
            "description": w["description"],
            "endpoint": w["endpoint"],
            "category": w.get("category", "Quant"),
            "type": w.get("type", "table"),
            "exportable": True,
            "refetchInterval": 900000,
            "staleTime": 300000,
        }
        if "params" in w:
            manifest[widget_id]["params"] = w["params"]  # type: ignore[index]
        if "data" in w:
            manifest[widget_id]["data"] = w["data"]  # type: ignore[index]
    return manifest


def _build_apps_manifest() -> list[dict[str, object]]:
    """Build a default dashboard app template for the quant widgets."""
    return [
        {
            "name": "Quant Trading Dashboard",
            "img": "",
            "description": (
                "Portfolio snapshots, equity curves, strategy performance, "
                "backtest reports, and engine health monitoring."
            ),
            "allowCustomization": True,
            "tabs": {
                "portfolio": {
                    "id": "portfolio",
                    "name": "Portfolio",
                    "layout": [
                        {
                            "i": "portfolio_snapshot",
                            "x": 0,
                            "y": 0,
                            "w": 20,
                            "h": 6,
                        },
                        {
                            "i": "portfolio_equity_curve",
                            "x": 20,
                            "y": 0,
                            "w": 20,
                            "h": 10,
                        },
                        {
                            "i": "portfolio_overall_performance",
                            "x": 0,
                            "y": 6,
                            "w": 20,
                            "h": 8,
                        },
                        {
                            "i": "portfolio_strategies",
                            "x": 0,
                            "y": 14,
                            "w": 20,
                            "h": 6,
                        },
                    ],
                },
                "strategies": {
                    "id": "strategies",
                    "name": "Strategies",
                    "layout": [
                        {
                            "i": "portfolio_strategy_performance",
                            "x": 0,
                            "y": 0,
                            "w": 20,
                            "h": 8,
                        },
                        {
                            "i": "portfolio_strategy_equity_curve",
                            "x": 20,
                            "y": 0,
                            "w": 20,
                            "h": 10,
                        },
                        {
                            "i": "backtest_strategy_report",
                            "x": 0,
                            "y": 8,
                            "w": 20,
                            "h": 8,
                        },
                        {
                            "i": "backtest_strategy_benchmark",
                            "x": 20,
                            "y": 10,
                            "w": 20,
                            "h": 10,
                        },
                        {
                            "i": "backtest_strategy_trades",
                            "x": 0,
                            "y": 16,
                            "w": 40,
                            "h": 10,
                        },
                    ],
                },
                "engines": {
                    "id": "engines",
                    "name": "Engines",
                    "layout": [
                        {
                            "i": "engine_catalog",
                            "x": 0,
                            "y": 0,
                            "w": 20,
                            "h": 6,
                        },
                        {
                            "i": "market_data_health",
                            "x": 20,
                            "y": 0,
                            "w": 10,
                            "h": 4,
                        },
                        {
                            "i": "market_data_providers",
                            "x": 30,
                            "y": 0,
                            "w": 10,
                            "h": 4,
                        },
                        {
                            "i": "signals_health",
                            "x": 20,
                            "y": 4,
                            "w": 10,
                            "h": 3,
                        },
                        {
                            "i": "signals_status",
                            "x": 30,
                            "y": 4,
                            "w": 10,
                            "h": 3,
                        },
                    ],
                },
            },
            "groups": [
                {
                    "name": "Strategy",
                    "type": "param",
                    "paramName": "strategy_id",
                    "defaultValue": "csm-set",
                    "widgetIds": [
                        "portfolio_strategy_detail",
                        "portfolio_strategy_performance",
                        "portfolio_strategy_equity_curve",
                        "backtest_strategy_report",
                        "backtest_strategy_trades",
                        "backtest_strategy_benchmark",
                    ],
                },
            ],
            "prompts": [
                "Show me today's portfolio snapshot",
                "What is the current equity curve?",
                "Compare strategy performance for csm-set",
                "Show recent trades for csm-set",
            ],
        },
    ]


def _build_agents_manifest() -> dict[str, object]:
    """Build a minimal quant-aware AI agent definition."""
    return {
        "quant-agent": {
            "agent_id": "quant-agent",
            "name": "Quant Trading Agent",
            "description": (
                "AI agent with access to the quant trading platform — "
                "portfolio snapshots, equity curves, backtest reports, "
                "strategy performance, and engine health."
            ),
            "endpoints": {
                "query": "/api/v1/agent/query",
            },
            "features": {
                "streaming": True,
                "widget-dashboard-select": True,
                "widget-dashboard-search": True,
            },
        },
    }
