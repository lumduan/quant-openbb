#!/usr/bin/env python3
"""Print a one-shot portfolio overview using the typed commands.

Calls ``overall_performance()``, ``portfolio_snapshot()``, and
``portfolio_equity_curve(normalize=True)`` from :mod:`openbb_quant.commands`.
The gateway must be reachable on ``QUANT_OPENBB_GATEWAY_BASE_URL`` (default
``http://quant-api-gateway:8000/api/v2``) and ``QUANT_OPENBB_INTERNAL_API_KEY``
must match the gateway's key.

Run with: ``uv run python examples/portfolio_overview.py``
"""

from __future__ import annotations

import asyncio
import sys

import httpx

from openbb_quant import commands


async def main() -> int:
    try:
        async with commands._client:
            overall = await commands.overall_performance()
            snapshot = await commands.portfolio_snapshot()
            curve = await commands.portfolio_equity_curve(normalize=True)
    except httpx.HTTPError as exc:
        print(f"gateway request failed: {exc}", file=sys.stderr)
        return 1

    print("─── Overall performance ───────────────────────────")
    print(f"  Total value      : {overall.total_portfolio_value}")
    print(f"  Daily return     : {overall.weighted_daily_return}")
    print(f"  Max drawdown     : {overall.combined_max_drawdown}")
    print(f"  Active strategies: {overall.active_strategies}")
    print()
    print("  Allocation:")
    for sid, weight in overall.allocation.items():
        print(f"    {sid:<20} {weight}")
    print()

    print("─── Latest snapshot ───────────────────────────────")
    print(f"  Snapshot date    : {snapshot.snapshot_date}")
    print(f"  Total value      : {snapshot.total_portfolio_value}")
    print(f"  Combined drawdown: {snapshot.combined_drawdown}")
    print()

    print(f"─── Portfolio equity curve ({len(curve)} points) ──")
    if not curve:
        print("  (no points)")
    else:
        head = curve[:5]
        tail = curve[-5:] if len(curve) > 5 else []
        for p in head:
            print(f"  {p.date}  {p.value}")
        if tail:
            print("  …")
            for p in tail:
                print(f"  {p.date}  {p.value}")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
