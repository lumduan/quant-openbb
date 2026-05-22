# CLAUDE.md — quant-openbb

## What this is

`quant-openbb` is the OpenBB Platform host for the `openbb_quant` router
extension. It proxies the 16 `/api/v2/engines/*` endpoints served by
`quant-api-gateway` and joins the umbrella `quant-network` on host port
`:8500`. It is one of five peer sub-projects under the
[quant-trading-system umbrella](../CLAUDE.md).

Phase 5 of the `feature-openbb-transition` roadmap migrates the React
dashboard onto this service.

## Tech stack

- Python 3.11 + `uv`
- `openbb-core>=1.6.9,<2.0` (extension framework; we do NOT depend on
  full `openbb` or `openbb[all]`)
- FastAPI + `httpx[asyncio]` for the proxy router
- Pydantic Settings v2 for configuration
- ruff (lint + format), mypy `--strict`, pytest with `pytest-asyncio`,
  `respx` for transport-level HTTP mocking, `pytest-cov` for coverage

## Repository layout

```
src/openbb_quant/      # the importable package
  __init__.py
  auth.py              # verify_api_key — optional inbound X-API-Key dependency
  config.py            # QuantOpenBBSettings, QUANT_OPENBB_* env vars
  client.py            # GatewayClient — async httpx + X-API-Key + 5xx retry
  router.py            # APIRouter — 16 proxy endpoints under /api/v2
  extension.py         # QuantExtension class (entry-point target)
  models.py            # Documentation-level Pydantic models
  main.py              # Standalone FastAPI app for `uvicorn …main:app`
tests/                 # pytest suite (target ≥80% coverage)
  test_auth.py         # inbound auth tests (5 cases)
examples/              # populated in Phase 3+
Dockerfile             # multi-stage; runs openbb-build as hard requirement
docker-compose.yml     # quant-network external, host :8500 → :8000
```

## Quality gate (run before every push)

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src tests
uv run pytest                       # cov + fail-under 80 set in pyproject.toml
```

All four commands must exit 0 before a commit can be considered ready.
Apply ruff auto-fixes via `uv run ruff check --fix src tests` and
`uv run ruff format src tests`.

## Bring-up order (matters)

```
1. quant-infra-db        # creates the quant-network and the DBs
2. quant-api-gateway     # the upstream this service proxies
3. quant-openbb          # this service
```

Health checks:

- Gateway: `curl http://localhost:8000/health`
- OpenBB:  `curl http://localhost:8500/health`

`docker compose up -d` here will **fail** if `quant-network` does not
already exist — bring up `quant-infra-db` first.

## Configuration

All settings come from `QUANT_OPENBB_*` env vars (see `.env.example`).
The most important ones:

| Variable | Purpose |
|---|---|
| `QUANT_OPENBB_GATEWAY_BASE_URL` | Where the proxy points (default: docker service name) |
| `QUANT_OPENBB_INTERNAL_API_KEY` | Must match the gateway's `INTERNAL_API_KEY`. Also controls **inbound** auth on `/api/v2/*` (see [Inbound auth](#inbound-auth)). |
| `QUANT_OPENBB_LOG_LEVEL` | Python logging level |
| `QUANT_OPENBB_CORS_ALLOW_ORIGINS` | JSON list; restrict in production |

Never commit `.env`. Only `.env.example` is tracked.

## Inbound auth

When `QUANT_OPENBB_INTERNAL_API_KEY` is **non-empty**, every request to
`/api/v2/*` must carry an `X-API-Key` header matching this value. The
check uses `secrets.compare_digest` for constant-time comparison, and
failures return HTTP 401 with a JSON body.

- **Empty key** (default): no auth — backward compatible.
- **Non-empty key**: all proxy endpoints require the header. `/health` is
  always open (it is on the app, not on the router).
- The dependency lives in `auth.py` and is applied via
  `app.include_router(router, dependencies=[Depends(verify_api_key)])` in
  `main.py`.

## Known gotchas

- **`openbb-build` in the Docker runtime stage** — required for the
  extension to be discoverable when running inside OpenBB Platform's full
  app. The Dockerfile runs it without a `|| true` fallback (per the
  umbrella playbook §11). If build fails here, do not silence it —
  inspect the package install order and the venv location.
- **`quant-network` must exist before `docker compose up`** — the compose
  file declares it `external: true`. If you see "network not found",
  bring up `quant-infra-db` first.
- **`_client` is initialised at import time** in `router.py`. Tests must
  patch `openbb_quant.router._client` rather than instantiating a new
  client. The `mock_client` fixture in `tests/conftest.py` does this
  correctly.
- **Booleans serialise as lowercase** in httpx query params (`normalize=true`,
  not `True`). Tests must assert on the wire format, not Python repr.
- **Coverage budget** is 80% (enforced by `pytest --cov-fail-under=80`).
  Current coverage is ≈98% — keep documentation-level modules
  (`models.py`, `extension.py`) covered by minimal smoke tests.

## Phase 2 status

Bootstrapped 2026-05-22. See the executable plan at
[`../plans/feature-openbb-transition/phase_2_create_quant_openbb_subproject.md`](../plans/feature-openbb-transition/phase_2_create_quant_openbb_subproject.md).
