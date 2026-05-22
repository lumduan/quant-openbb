"""Settings for the openbb_quant extension.

Reads ``QUANT_OPENBB_*`` environment variables (plus a local ``.env`` if
present) into a typed Pydantic Settings model. ``get_settings`` is cached so
that the same instance is shared across the process.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class QuantOpenBBSettings(BaseSettings):
    """Runtime configuration for the openbb_quant extension."""

    model_config = SettingsConfigDict(
        env_prefix="QUANT_OPENBB_",
        env_file=".env",
        extra="ignore",
    )

    gateway_base_url: str = "http://quant-api-gateway:8000/api/v2"
    internal_api_key: SecretStr = SecretStr("")
    log_level: str = "INFO"
    cors_allow_origins: list[str] = ["*"]


@lru_cache
def get_settings() -> QuantOpenBBSettings:
    """Return the process-wide settings instance (lazy + cached)."""
    return QuantOpenBBSettings()
