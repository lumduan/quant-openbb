"""Async HTTP client that proxies GET requests to ``quant-api-gateway``.

Modeled on the csm-set ``GatewayClient``: shared ``httpx.AsyncClient``,
``X-API-Key`` header injection, exponential-backoff retry on 5xx, and
immediate raise on 4xx. All methods are fully type-annotated.
"""

from __future__ import annotations

import asyncio
import logging
from types import TracebackType
from typing import Any

import httpx

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS: float = 30.0
DEFAULT_MAX_ATTEMPTS: int = 3
DEFAULT_BACKOFF_SECONDS: tuple[float, ...] = (1.0, 2.0, 4.0)


class GatewayClient:
    """Async client for the quant-api-gateway ``/api/v2`` surface.

    The client is reusable: instantiate once, share across requests, and
    close via ``async with`` or an explicit ``await client.close()``.

    Args:
        base_url: Gateway base URL, e.g.
            ``http://quant-api-gateway:8000/api/v2``. No trailing slash
            required.
        api_key: Shared internal API key, injected as ``X-API-Key`` on every
            outbound request.
        timeout: Per-request timeout in seconds.
        max_attempts: Total attempts (initial + retries) on 5xx.
        backoff_seconds: Per-attempt sleep durations. Indexed by 0-based
            ``attempt_index``; clamped to the last value when ``max_attempts``
            exceeds the sequence length.
        transport: Optional custom ``httpx.AsyncBaseTransport`` for tests
            (e.g. ``respx.MockTransport``).
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        backoff_seconds: tuple[float, ...] = DEFAULT_BACKOFF_SECONDS,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._max_attempts = max_attempts
        self._backoff_seconds = backoff_seconds
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            transport=transport,
        )

    async def __aenter__(self) -> GatewayClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client. Idempotent."""
        await self._client.aclose()

    async def get(self, path: str, **params: Any) -> Any:
        """Issue a GET against ``base_url/path`` and return parsed JSON.

        Path is joined to ``base_url`` after stripping any leading slash.
        Query parameters with ``None`` values are dropped.

        Retries on 5xx up to ``max_attempts`` with exponential backoff.
        Raises immediately on 4xx (no retry).

        Args:
            path: Path under ``base_url`` (e.g. ``engines/catalog``).
            **params: Query parameters. ``None`` values are removed before
                sending.

        Returns:
            Parsed JSON body (typically ``dict`` or ``list``).

        Raises:
            httpx.HTTPStatusError: For any 4xx response, or for a 5xx after
                all retries are exhausted.
            httpx.HTTPError: For network-level errors after retries.
        """
        clean_path = path.lstrip("/")
        clean_params = {k: v for k, v in params.items() if v is not None}
        headers = {"X-API-Key": self._api_key}

        last_exc: Exception | None = None
        for attempt in range(self._max_attempts):
            _LOGGER.debug(
                "gateway GET attempt %d/%d path=%s params=%s",
                attempt + 1,
                self._max_attempts,
                clean_path,
                clean_params,
            )
            try:
                response = await self._client.get(
                    clean_path,
                    params=clean_params,
                    headers=headers,
                )
            except httpx.HTTPError as exc:
                last_exc = exc
                _LOGGER.debug(
                    "gateway GET network error on attempt %d: %s",
                    attempt + 1,
                    exc,
                )
                if attempt + 1 >= self._max_attempts:
                    break
                await self._sleep_for_attempt(attempt)
                continue

            status = response.status_code
            if 400 <= status < 500:
                _LOGGER.error(
                    "gateway returned client error %d for %s; not retrying",
                    status,
                    clean_path,
                )
                response.raise_for_status()
            if status >= 500:
                _LOGGER.debug(
                    "gateway returned %d on attempt %d/%d for %s",
                    status,
                    attempt + 1,
                    self._max_attempts,
                    clean_path,
                )
                last_exc = httpx.HTTPStatusError(
                    f"Server error {status}",
                    request=response.request,
                    response=response,
                )
                if attempt + 1 >= self._max_attempts:
                    break
                await self._sleep_for_attempt(attempt)
                continue

            return response.json()

        assert last_exc is not None
        _LOGGER.error(
            "gateway GET failed after %d attempts for %s: %s",
            self._max_attempts,
            clean_path,
            last_exc,
        )
        raise last_exc

    async def _sleep_for_attempt(self, attempt_index: int) -> None:
        """Sleep for the configured backoff window for the given attempt."""
        clamped = min(attempt_index, len(self._backoff_seconds) - 1)
        await asyncio.sleep(self._backoff_seconds[clamped])
