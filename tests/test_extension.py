"""Smoke tests for ``openbb_quant.extension``."""

from __future__ import annotations

from openbb_quant.extension import QuantExtension
from openbb_quant.router import router


def test_extension_exposes_router() -> None:
    assert QuantExtension.router is router


def test_extension_router_has_all_endpoints() -> None:
    assert len(QuantExtension.router.routes) == 18
