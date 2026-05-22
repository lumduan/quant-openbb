#!/usr/bin/env python3
"""Print a paginated trade log for a strategy using the typed commands.

Reads ``STRATEGY_ID`` from the environment, then calls
``trade_log(id, limit=20)`` from :mod:`openbb_quant.commands`.

Run with: ``STRATEGY_ID=csm-set uv run python examples/trade_log.py``
"""

from __future__ import annotations

import asyncio
import os
import sys

import httpx

from openbb_quant import commands


def _usage_and_exit() -> int:
    print(
        "STRATEGY_ID env var is required.\n"
        "Usage: STRATEGY_ID=<id> uv run python examples/trade_log.py",
        file=sys.stderr,
    )
    return 1


async def main() -> int:
    strategy_id = os.environ.get("STRATEGY_ID")
    if not strategy_id:
        return _usage_and_exit()

    try:
        async with commands._client:
            page = await commands.trade_log(strategy_id, limit=20)
    except httpx.HTTPError as exc:
        print(f"gateway request failed: {exc}", file=sys.stderr)
        return 1

    if not page.items:
        print(f"No trades found for strategy {strategy_id}")
        return 0

    print(
        f"─── Trades for {strategy_id} "
        f"(showing {len(page.items)} of {page.total}, offset={page.offset}) ──"
    )
    print(f"  {'Date':<12} {'Side':<6} {'Entry':>10} {'Exit':>10} {'PnL':>10}")
    print(f"  {'-' * 12} {'-' * 6} {'-' * 10} {'-' * 10} {'-' * 10}")
    for trade in page.items:
        date_str = str(trade.get("date", ""))[:12]
        side = str(trade.get("direction", trade.get("side", "")))[:6]
        entry = str(trade.get("entry", trade.get("entry_price", "")))[:10]
        exit_ = str(trade.get("exit", trade.get("exit_price", "")))[:10]
        pnl = str(trade.get("pnl", trade.get("realized_pnl", "")))[:10]
        print(f"  {date_str:<12} {side:<6} {entry:>10} {exit_:>10} {pnl:>10}")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
