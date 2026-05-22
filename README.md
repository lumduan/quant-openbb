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
| `QUANT_OPENBB_INTERNAL_API_KEY` | _(empty)_ | Shared `X-API-Key` for internal calls (must match the gateway's `INTERNAL_API_KEY`). |
| `QUANT_OPENBB_LOG_LEVEL` | `INFO` | Python logging level. |
| `QUANT_OPENBB_CORS_ALLOW_ORIGINS` | `["*"]` | CORS allow-list (JSON list). |

## Proxied endpoints

All 16 endpoints are GET requests under `/api/v2`. The proxy delegates
to the gateway and returns its JSON verbatim.

| # | Path | Path params | Query params |
|---|---|---|---|
| 1 | `/engines/catalog` | — | — |
| 2 | `/engines/portfolio/snapshot` | — | — |
| 3 | `/engines/portfolio/snapshot/{snapshot_date}` | `snapshot_date` (date) | — |
| 4 | `/engines/portfolio/equity-curve` | — | `normalize` (bool, default `true`) |
| 5 | `/engines/portfolio/overall-performance` | — | — |
| 6 | `/engines/portfolio/strategies` | — | — |
| 7 | `/engines/portfolio/strategies/{strategy_id}` | `strategy_id` (str) | — |
| 8 | `/engines/portfolio/strategies/{strategy_id}/performance` | `strategy_id` | `from_date`, `to_date` |
| 9 | `/engines/portfolio/strategies/{strategy_id}/equity-curve` | `strategy_id` | — |
| 10 | `/engines/backtest/strategies/{strategy_id}/report` | `strategy_id` | `date` |
| 11 | `/engines/backtest/strategies/{strategy_id}/trades` | `strategy_id` | `from_date`, `to_date`, `limit`, `offset` |
| 12 | `/engines/backtest/strategies/{strategy_id}/benchmark-curve` | `strategy_id` | `from_date`, `to_date`, `normalize` |
| 13 | `/engines/market-data/health` | — | — |
| 14 | `/engines/market-data/providers` | — | — |
| 15 | `/engines/signals/health` | — | — |
| 16 | `/engines/signals/status` | — | — |

Local health check: `curl http://localhost:8500/health` → `{"status":"ok"}`.

## Dependencies

This service is downstream of the gateway. Bring-up order from the
umbrella repo:

```
quant-infra-db  →  quant-api-gateway  →  quant-openbb
```

Without `quant-api-gateway` healthy, the proxy returns 502/504 errors.

## Development

See [`CLAUDE.md`](CLAUDE.md) for the full development workflow, quality
gate, and known gotchas.
