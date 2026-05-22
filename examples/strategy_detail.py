#!/usr/bin/env python3
"""Print a strategy-detail summary using the typed commands.

Reads ``STRATEGY_ID`` from the environment, then calls
``equity_curve(id)``, ``strategy_report(id)``, and ``list_strategies()``
from :mod:`openbb_quant.commands`.

Run with: ``STRATEGY_ID=csm-set uv run python examples/strategy_detail.py``
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
        "Usage: STRATEGY_ID=<id> uv run python examples/strategy_detail.py",
        file=sys.stderr,
    )
    return 1


async def main() -> int:
    strategy_id = os.environ.get("STRATEGY_ID")
    if not strategy_id:
        return _usage_and_exit()

    try:
        async with commands._client:
            strategies = await commands.list_strategies()
            curve = await commands.equity_curve(strategy_id)
            report = await commands.strategy_report(strategy_id)
    except httpx.HTTPError as exc:
        print(f"gateway request failed: {exc}", file=sys.stderr)
        return 1

    strategy = next((s for s in strategies if s.id == strategy_id), None)
    if strategy is None:
        print(f"strategy not found: {strategy_id}", file=sys.stderr)
        return 1

    print("─── Strategy ──────────────────────────────────────")
    print(f"  ID           : {strategy.id}")
    print(f"  Name         : {strategy.name}")
    print(f"  Type         : {strategy.type}")
    print(f"  Active       : {strategy.active}")
    print(f"  Capital weight: {strategy.capital_weight}")
    print()

    print(f"─── Report as of {report.as_of} ──────────────")
    headline = report.report.get("headline", {})
    if not headline:
        print("  (no headline KPIs in report)")
    else:
        for k, v in headline.items():
            print(f"  {k:<24} {v}")
    print()

    print(f"─── Equity curve ({len(curve)} points) ────────────")
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
