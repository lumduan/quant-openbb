# openbb_quant — examples

Runnable Python scripts that exercise the typed command layer
(`openbb_quant.commands`) against a live `quant-api-gateway`. They are the
canonical demos of "how to consume gateway data from Python without parsing
raw JSON by hand."

## Prerequisites

All three scripts hit the gateway on every run. Bring up the stack first:

```bash
cd ../quant-infra-db        && docker compose up -d   # creates quant-network + DBs
cd ../quant-api-gateway     && docker compose up -d
```

The scripts read their configuration from `QUANT_OPENBB_*` env vars via
`openbb_quant.config.get_settings()`. At minimum set:

| Variable | Required | Default |
|---|---|---|
| `QUANT_OPENBB_GATEWAY_BASE_URL` | yes (in dev) | `http://quant-api-gateway:8000/api/v2` (works from inside the container; from the host use `http://localhost:8080/api/v2`) |
| `QUANT_OPENBB_INTERNAL_API_KEY` | yes | _empty_ — must match the gateway's `INTERNAL_API_KEY` |

A working host invocation looks like:

```bash
export QUANT_OPENBB_GATEWAY_BASE_URL=http://localhost:8080/api/v2
export QUANT_OPENBB_INTERNAL_API_KEY=<your-internal-api-key>
```

## Run

```bash
# Portfolio-wide overview (overall performance + latest snapshot + equity curve)
uv run python examples/portfolio_overview.py

# Per-strategy detail (config, latest report headline, equity curve)
STRATEGY_ID=csm-set uv run python examples/strategy_detail.py

# Most recent 20 trades for a strategy
STRATEGY_ID=csm-set uv run python examples/trade_log.py
```

Each script exits 0 on success, 1 on `httpx.HTTPError` (network or HTTP-status
failures), and 1 when `STRATEGY_ID` is required but missing.

## Expected output shape

### `portfolio_overview.py`

```
─── Overall performance ───────────────────────────
  Total value      : 10000.00
  Daily return     : 0.0050
  Max drawdown     : -0.0125
  Active strategies: 2

  Allocation:
    csm-set              0.6
    tfex                 0.4

─── Latest snapshot ───────────────────────────────
  Snapshot date    : 2026-05-22
  Total value      : 10000.00
  Combined drawdown: -0.0125

─── Portfolio equity curve (N points) ──
  2025-01-02  1.0000
  …
  2026-05-22  1.0237
```

### `strategy_detail.py`

```
─── Strategy ──────────────────────────────────────
  ID           : csm-set
  Name         : CSM-SET
  Type         : momentum
  Active       : True
  Capital weight: 1.0

─── Report as of 2026-05-22 ──────────────
  net_profit               1234.56
  sharpe                   1.42
  …

─── Equity curve (N points) ────────────
  2025-01-02  1.0000
  …
```

### `trade_log.py`

```
─── Trades for csm-set (showing 20 of N, offset=0) ──
  Date         Side        Entry       Exit        PnL
  ------------ ------ ---------- ---------- ----------
  2026-05-22   long        10.00      11.00       1.00
  …
```

If the strategy has no trades:

```
No trades found for strategy <strategy_id>
```

## Notes

- The scripts close `openbb_quant.commands._client` via `async with` so the
  underlying `httpx.AsyncClient` is cleanly shut down before the event loop
  tears down. This is a best practice for short-lived scripts; long-running
  consumers (notebooks, OpenBB Platform, services) should rely on the
  module-level singleton lifecycle instead.
- For trade rows, fields are read defensively (`direction` falls back to
  `side`, `entry` to `entry_price`, etc.) because each strategy adapter is
  free to choose its own key names within the `extended_data` contract.
- The verify script `scripts/verify_openbb_integration.sh` exercises the
  same gateway endpoints over HTTP rather than via the Python layer.
