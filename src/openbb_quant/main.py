"""Standalone FastAPI app for ``openbb_quant``.

Used by the container CMD (``uvicorn openbb_quant.main:app``) to expose
the proxy router without depending on OpenBB Platform's full app bootstrap.
A ``/health`` endpoint is exposed for the Docker HEALTHCHECK and for
container-level liveness probes.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.include_router(router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness probe used by the container HEALTHCHECK."""
    return {"status": "ok"}
