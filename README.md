# quant-openbb

OpenBB Platform router extension that proxies the `quant-api-gateway`
`/api/v2/engines/*` surface, exposing the four logical engines
(Market Data, Backtest, Portfolio, Signals) inside an OpenBB-compatible
FastAPI app. Joins the umbrella `quant-network` and listens on host
port `:8500`.

> See the umbrella system map at
> [`../CLAUDE.md`](../CLAUDE.md) for the broader architecture.

## Quick start

### Local (uv)

```bash
uv sync
cp .env.example .env       # fill in QUANT_OPENBB_INTERNAL_API_KEY
uv run uvicorn openbb_quant.main:app --reload --port 8500
curl -sf http://localhost:8500/health
```

### Docker

The default compose file runs the **standalone** proxy (no OpenBB data
providers). To add providers, see [docs/connections.md](docs/connections.md).

```bash
# 1. Bring up quant-network (one-time, from umbrella)
cd ../quant-infra-db && docker compose up -d
cd ../quant-api-gateway && docker compose up -d

# 2. Bring up quant-openbb
cd ../quant-openbb
cp .env.example .env       # fill in QUANT_OPENBB_INTERNAL_API_KEY
docker compose up -d --build
curl -sf http://localhost:8500/health
```

## Environment variables

| Name | Default | Description |
|---|---|---|
| `QUANT_OPENBB_GATEWAY_BASE_URL` | `http://quant-api-gateway:8000/api/v2` | Gateway v2 base URL. Use `localhost` for host-network testing. |
| `QUANT_OPENBB_INTERNAL_API_KEY` | _(empty)_ | Shared `X-API-Key` for outbound gateway calls. Also controls **inbound auth** on `/api/v2/*` when non-empty (see [Authentication](#authentication)). |
| `QUANT_OPENBB_LOG_LEVEL` | `INFO` | Python logging level. |
| `QUANT_OPENBB_CORS_ALLOW_ORIGINS` | `["*"]` | CORS allow-list (JSON list). |

## Proxied endpoints

All 18 endpoints are GET requests under `/api/v2`. The proxy delegates
to the gateway and returns its JSON verbatim.

| # | Path | Path params | Query params |
|---|---|---|---|
| 1 | `/engines/catalog` | — | — |
| 2 | `/engines/portfolio/snapshot` | — | — |
| 3 | `/engines/portfolio/snapshot/{snapshot_date}` | `snapshot_date` (date) | — |
| 4 | `/engines/portfolio/metrics` | — | — |
| 5 | `/engines/portfolio/metrics/{snapshot_date}` | `snapshot_date` (date) | — |
| 6 | `/engines/portfolio/equity-curve` | — | `normalize` (bool, default `true`) |
| 7 | `/engines/portfolio/overall-performance` | — | — |
| 8 | `/engines/portfolio/strategies` | — | — |
| 9 | `/engines/portfolio/strategies/{strategy_id}` | `strategy_id` (str) | — |
| 10 | `/engines/portfolio/strategies/{strategy_id}/performance` | `strategy_id` | `from_date`, `to_date` |
| 11 | `/engines/portfolio/strategies/{strategy_id}/equity-curve` | `strategy_id` | — |
| 12 | `/engines/backtest/strategies/{strategy_id}/report` | `strategy_id` | `date` |
| 13 | `/engines/backtest/strategies/{strategy_id}/trades` | `strategy_id` | `from_date`, `to_date`, `limit`, `offset` |
| 14 | `/engines/backtest/strategies/{strategy_id}/benchmark-curve` | `strategy_id` | `from_date`, `to_date`, `normalize` |
| 15 | `/engines/market-data/health` | — | — |
| 16 | `/engines/market-data/providers` | — | — |
| 17 | `/engines/signals/health` | — | — |
| 18 | `/engines/signals/status` | — | — |

Rows 4 and 5 ship pre-formatted KPI cards for the OpenBB Metric widget —
see [OpenBB Metric Widget Example](#openbb-metric-widget-example) below.

Local health check: `curl http://localhost:8500/health` → `{"status":"ok"}`.

## Dependencies

This service is downstream of the gateway. Bring-up order from the
umbrella repo:

```
quant-infra-db  →  quant-api-gateway  →  quant-openbb
```

Without `quant-api-gateway` healthy, the proxy returns 502/504 errors.

## Authentication

`QUANT_OPENBB_INTERNAL_API_KEY` controls optional inbound auth on the proxy
router. The check uses constant-time comparison (`secrets.compare_digest`)
and failures return HTTP 401.

| Key state | Behavior |
| --- | --- |
| **Empty** (default) | All requests allowed — backward compatible |
| **Non-empty** | `X-API-Key` header required on every `/api/v2/*` request |

`/health` is always open (it runs on the app, not the router).

For the OpenBB Workspace "Connect backend" form, configure Key = `X-API-Key`,
Value = your key, Location = `Header`.

See [`src/openbb_quant/auth.py`](src/openbb_quant/auth.py) for the implementation.

## OpenBB Metric Widget Example

The `/engines/portfolio/metrics` proxy returns an array of `{label, value,
delta}` objects matching the
[OpenBB Metric widget contract](https://docs.openbb.co/workspace/developers/widget-types/metric).
The widget renders the arrow (`↑` / `↓`) and color from the sign of `delta`
— the data carries only pre-formatted strings.

### Example response

```json
[
  {"label": "Daily Return",          "value": "0.63%",       "delta": "-0.12"},
  {"label": "Portfolio Drawdown",    "value": "-4.22%",      "delta": "-0.12"},
  {"label": "Total Portfolio Value", "value": "$998,142.71", "delta": "6234.10"}
]
```

`delta` is the day-over-day change vs the most recent earlier snapshot
(percentage points for percentages, raw dollars for currency, no unit on the
output string). Empty string when no comparable previous snapshot exists. See
the gateway reference: [`quant-api-gateway/docs/reference/portfolio.md`](../quant-api-gateway/docs/reference/portfolio.md).

### `widgets.json` config

Drop this into your OpenBB Workspace `widgets.json` to render the three KPIs:

```json
{
  "name": "Portfolio Metrics",
  "description": "Key portfolio KPIs with day-over-day deltas",
  "category": "Portfolio",
  "type": "metric",
  "endpoint": "engines/portfolio/metrics",
  "gridData": { "w": 15, "h": 8 },
  "params": [
    {
      "paramName": "snapshot_date",
      "type": "date",
      "value": "$currentDate-1d",
      "label": "Select Date"
    }
  ]
}
```

When `snapshot_date` is omitted the proxy hits `/engines/portfolio/metrics`
(latest); when supplied, it hits `/engines/portfolio/metrics/{snapshot_date}`.

## OpenBB data provider connections

To use OpenBB data providers (Yahoo Finance, Polygon, etc.) alongside the
quant proxy, run in **full-platform mode** and configure provider credentials.

See **[docs/connections.md](docs/connections.md)** for the complete guide,
including credential setup, Docker configuration, and provider installation.

## Development

See [`CLAUDE.md`](CLAUDE.md) for the full development workflow, quality
gate, and known gotchas.

## Migration from quant-dashboard

> **quant-dashboard** ([github.com/lumduan/quant-dashboard](https://github.com/lumduan/quant-dashboard))
> is deprecated as of 2026-05-22 and superseded by this service.

### Feature-to-command mapping

Every dashboard data hook has a typed OpenBB command equivalent (confirmed
in Phase 3 of the OpenBB transition). Use this table to migrate your
existing dashboard integration:

| Dashboard Feature | Dashboard Hook | OpenBB Typed Command | Raw Proxy Path |
|---|---|---|---|
| Portfolio Performance | `fetchOverallPerformance` | `overall_performance()` | `GET /engines/portfolio/overall-performance` |
| Portfolio Equity Curve | `fetchPortfolioEquityCurve` | `portfolio_equity_curve(normalize)` | `GET /engines/portfolio/equity-curve` |
| Strategy List | `fetchStrategies` | `list_strategies()` | `GET /engines/portfolio/strategies` |
| Portfolio Snapshot | `fetchPortfolioSnapshot` | `portfolio_snapshot(snapshot_date?)` | `GET /engines/portfolio/snapshot[/{date}]` |
| Strategy Details | `fetchStrategyDetails` | (N/A — use `strategy_report`) | `GET /engines/portfolio/strategies/{id}` |
| Strategy Equity Curve | `fetchStrategyEquityCurve` | `equity_curve(strategy_id)` | `GET /engines/portfolio/strategies/{id}/equity-curve` |
| Strategy Report | `fetchStrategyReport` | `strategy_report(strategy_id, target_date?)` | `GET /engines/backtest/strategies/{id}/report` |
| Trade Log | `fetchStrategyTrades` | `trade_log(strategy_id, ...)` | `GET /engines/backtest/strategies/{id}/trades` |
| Benchmark Curve | `fetchStrategyBenchmarkCurve` | *(raw proxy, no typed command)* | `GET /engines/backtest/strategies/{id}/benchmark-curve` |

### Quick start

```python
from openbb_quant.commands import (
    overall_performance,
    portfolio_equity_curve,
    list_strategies,
    strategy_report,
    trade_log,
)
import asyncio

async def main():
    perf = await overall_performance()
    strategies = await list_strategies()
    # Full examples: see examples/ directory

asyncio.run(main())
```

> **Bring-up reminder:** Ensure the stack is running before calling commands:
> `quant-infra-db` → `quant-api-gateway` → `quant-openbb`
> (see [CLAUDE.md](../CLAUDE.md) for the full bring-up order).
