"""FastAPI dependency for optional inbound API-key authentication.

When ``QUANT_OPENBB_INTERNAL_API_KEY`` is empty (the default) every request
is allowed.  When non-empty, the request MUST carry an ``X-API-Key`` header
whose value matches (constant-time comparison).
"""

from __future__ import annotations

import logging
import secrets

from fastapi import Depends, HTTPException, Request, status

from openbb_quant.config import QuantOpenBBSettings, get_settings

_LOGGER = logging.getLogger(__name__)


def verify_api_key(
    request: Request,
    settings: QuantOpenBBSettings = Depends(get_settings),
) -> None:
    """Optionally require X-API-Key on inbound requests to the proxy router."""
    expected = settings.internal_api_key.get_secret_value().strip()
    if not expected:
        return

    actual = (request.headers.get("X-API-Key") or "").strip()
    if not actual:
        _LOGGER.warning("Inbound request missing X-API-Key header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    if not secrets.compare_digest(actual, expected):
        _LOGGER.warning("Inbound request has incorrect X-API-Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
