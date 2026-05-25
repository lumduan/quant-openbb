# Plan — Portfolio Metrics Endpoint for OpenBB Metric Widget

| Field | Value |
|---|---|
| Feature slug | `feature-portfolio-metrics` |
| Date | 2026-05-25 |
| Sub-repos | `quant-api-gateway`, `quant-openbb` |
| Umbrella note | `plans/feature-openbb-transition/ROADMAP.md` (Phase 3 completion note) |
| Branch (both sub-repos) | `feat/portfolio-metrics` |
| Coverage gates | gateway ≥90% (existing), openbb ≥80% (existing) |

---

## Context

OpenBB's **Metric widget** expects each data point as `{label, value, delta}` strings — large value on top, an optional smaller delta underneath. The gateway today returns `PortfolioSnapshotResponse` with raw `Decimal` fields (`weighted_daily_return`, `combined_drawdown`, `total_portfolio_value`), which the dashboard formatted client-side. To make the snapshot drop-in compatible with OpenBB's Metric widget, we add a new endpoint `GET /api/v2/engines/portfolio/metrics` that returns pre-formatted strings with arrow indicators (↑ gain / ↓ loss / → flat) and a day-over-day delta computed against the previous snapshot.

Two design clarifications resolved up front:
- **Metric shape**: both `value` and `delta` are populated. `value` is the current metric (arrows for percentages, plain for currency); `delta` is the day-over-day change vs the previous snapshot (arrow-formatted). Falls back to `None` when no previous snapshot exists or a source field is null.
- **Conventions over prompt**: tests extend `tests/api/v2/test_engines.py` (not a new file); gateway coverage gate stays at 90%; the openbb proxy returns `Any` with no `response_model`, matching the other 16 proxy endpoints.

---

## Scope

**In scope**
- New formatting utilities (`format_percentage`, `format_currency`, Decimal-precise)
- New Pydantic models: `MetricItem`, `PortfolioMetricsResponse`
- New service function `build_metrics_response()` + helper `query_previous_snapshot()`
- New endpoints: `GET /engines/portfolio/metrics` and `GET /engines/portfolio/metrics/{snapshot_date}` (mirrors the snapshot pair)
- OpenBB proxy route + tests
- Docs: gateway reference + openbb README + completion plan file

**Out of scope**
- Modifying the existing snapshot endpoint (additive only)
- v1 endpoint mirror (this is v2-only; OpenBB consumes v2)
- Frontend Metric widget config wiring beyond the README example (`widgets.json` lives in `quant-openbb`'s extension, but no live deployment in this PR)
- Caching strategy changes (reuse `portfolio_snapshot_ttl_seconds`)

---

## Critical files & reuse map

**Reuse (do not duplicate):**
- `quant-api-gateway/src/services/cache.py` — `get_cached`, `set_cached`, `CacheError`
- `quant-api-gateway/src/services/portfolio.py` — `query_latest_snapshot`, `query_snapshot_by_date`, `_row_to_snapshot_response`
- `quant-api-gateway/src/services/errors.py` — `ServiceError`
- `quant-api-gateway/src/config.py` — `get_settings()`, `portfolio_snapshot_ttl_seconds`
- `quant-api-gateway/src/db/postgres.py` — `get_pool()`
- `quant-openbb/src/openbb_quant/client.py` — `GatewayClient` (auth + retry already handled)
- `quant-openbb/src/openbb_quant/router.py` — existing `_client` instance

**Create:**
- `quant-api-gateway/src/utils/__init__.py`, `quant-api-gateway/src/utils/formatting.py`
- `quant-openbb/docs/plans/feature-portfolio-metrics.md` (this file)

**Modify:**
- `quant-api-gateway/src/schemas/gateway.py` — add `MetricItem`, `PortfolioMetricsResponse`
- `quant-api-gateway/src/services/portfolio.py` — add `query_previous_snapshot`, `build_metrics_response`
- `quant-api-gateway/src/api/v2/engines/portfolio.py` — add two new routes
- `quant-api-gateway/tests/api/v2/test_engines.py` — extend with metrics tests
- `quant-api-gateway/docs/reference/portfolio.md` — endpoint reference
- `quant-openbb/src/openbb_quant/router.py` — add proxy route(s)
- `quant-openbb/tests/test_router.py` — extend with proxy tests
- `quant-openbb/README.md` — add Metric widget example section + new row in the proxied endpoints table
- `plans/feature-openbb-transition/ROADMAP.md` (umbrella) — Phase 3 completion note

---

## Implementation phases

### Phase A — Plan file & branches
- Create `feat/portfolio-metrics` in both sub-repos.
- Copy this plan to `quant-openbb/docs/plans/feature-portfolio-metrics.md` and commit as `docs(plan): feature-portfolio-metrics scaffold`.

### Phase B — quant-api-gateway implementation
1. **B1** — `src/utils/formatting.py`: `format_percentage(value, decimals=2, use_arrows=True)` and `format_currency(value, currency="USD")`. Pure Decimal, ROUND_HALF_UP, no float.
2. **B2** — `src/schemas/gateway.py`: add `MetricItem` (`label`, `value`, `delta: str | None`) and `PortfolioMetricsResponse` (`snapshot_date`, `metrics: list[MetricItem]`, `computed_at` with UTC validator). Both frozen.
3. **B3** — `src/services/portfolio.py`: add `query_previous_snapshot(pool, before_date)` and `build_metrics_response(current, previous)`. Three metrics in fixed order — Daily Return, Portfolio Drawdown, Total Portfolio Value. Delta = current − previous, arrow-formatted; `None` when no previous snapshot or source field null. Private `_format_currency_delta(diff)` wraps `format_currency` with arrows.
4. **B4** — `src/api/v2/engines/portfolio.py`: add `@router.get("/metrics")` and `@router.get("/metrics/{snapshot_date}")` with cache keys `portfolio_metrics:latest` / `portfolio_metrics:{date}`, TTL `portfolio_snapshot_ttl_seconds`. Same cache-aside pattern as snapshot.
5. **B5** — `tests/api/v2/test_engines.py`: formatting unit tests + endpoint integration tests (see acceptance criteria).

### Phase C — quant-openbb proxy
1. **C1** — `src/openbb_quant/router.py`: add two routes mirroring the snapshot proxy pair. Return `Any`, no `response_model`. `_client` already injects `X-API-Key`.
2. **C2** *(optional)* — `src/openbb_quant/models.py`: add `PortfolioMetrics` / `MetricItem` documentation models (`extra="allow"`). Skip if it bloats the PR.
3. **C3** — `tests/test_router.py`: two tests using the existing `mock_client` / `http_client` fixtures.

### Phase D — Documentation
- **D1** `quant-api-gateway/docs/reference/portfolio.md`: append endpoint reference with example response, arrow legend, cache behavior, 404 behavior, delta semantics.
- **D2** `quant-openbb/README.md`: add row in the proxied endpoints table and a "OpenBB Metric Widget Example" section with the `widgets.json` config.
- **D3** This plan file: append `## Completion Notes` (date, branch, commit SHAs, test results, deviations).

### Phase E — Quality gate, commits, umbrella update
- Run in both sub-repos: `uv run ruff check src tests`, `uv run ruff format --check src tests`, `uv run mypy src tests`, `uv run pytest` (gateway `--cov-fail-under=90`, openbb `--cov-fail-under=80`). All four must exit 0.
- Commits:
  - Gateway: `feat(portfolio): add formatted metrics endpoint for OpenBB Metric widget`
  - OpenBB:  `feat(router): proxy portfolio metrics endpoint for Metric widget`
- Push both branches to origin.
- Umbrella `main`: add Phase 3 completion bullet to `plans/feature-openbb-transition/ROADMAP.md` and commit as `docs(roadmap): note portfolio metrics endpoint completion`.

---

## Acceptance criteria

- [ ] `GET /api/v2/engines/portfolio/metrics` returns `PortfolioMetricsResponse` with exactly 3 metrics in fixed order: Daily Return, Portfolio Drawdown, Total Portfolio Value.
- [ ] Each metric's `value` uses arrows for percentages and `$NNN,NNN.NN` formatting for currency.
- [ ] `delta` is populated when a previous snapshot exists and the underlying field is non-null; otherwise `null`.
- [ ] Null `combined_drawdown` → drawdown metric `value == "N/A"`, `delta is None`.
- [ ] Cache hit serves without DB query; cache failures degrade gracefully (200 with warning log).
- [ ] OpenBB proxy returns the gateway response verbatim, forwards `X-API-Key`.
- [ ] Both sub-repos pass `ruff check`, `ruff format --check`, `mypy src tests`, `pytest` (gateway ≥90% cov, openbb ≥80% cov).
- [ ] Docs updated: gateway `portfolio.md`, openbb `README.md`, plan completion notes, umbrella ROADMAP.
- [ ] Two commits pushed to `feat/portfolio-metrics` (one per sub-repo); umbrella commit lands on `main`.

---

## Verification (end-to-end, after both sub-repos pushed and rebuilt)

1. Bring up infra-db + gateway: `cd quant-infra-db && docker compose up -d && cd ../quant-api-gateway && docker compose up -d`.
2. Seed at least two consecutive portfolio snapshot rows so day-over-day delta has data.
3. Hit the gateway directly:
   ```
   curl -H "X-API-Key: $INTERNAL_API_KEY" http://localhost:8000/api/v2/engines/portfolio/metrics | jq
   ```
   Expect 3 metric items with arrow-formatted `value` strings and populated `delta` strings (or `null` if only one snapshot exists).
4. Bring up openbb: `cd ../quant-openbb && docker compose up -d`. Hit the proxy:
   ```
   curl -H "X-API-Key: $QUANT_OPENBB_INBOUND_API_KEY" http://localhost:8500/engines/portfolio/metrics | jq
   ```
   Response shape must match the gateway response byte-for-byte.
5. Run the full test suites in both sub-repos (`uv run pytest`) — all green, coverage gates satisfied.
6. *(Optional)* Drop the example `widgets.json` snippet into a local OpenBB Workspace to confirm the Metric widget renders the three KPIs with arrows.

---

## Appendix — Full AI agent prompt (verbatim)

> You are implementing an enhancement to the quant-trading-system's portfolio snapshot
> endpoint to serve metrics formatted for OpenBB's Metric widget (label/value/delta format).
> Work across two sub-projects: quant-api-gateway (implement metrics formatting backend) and
> quant-openbb (proxy the endpoint). Follow all project standards: Python 3.11 + uv, type
> hints, async/await, Pydantic v2 frozen models, 80%+ test coverage, ruff + mypy --strict.
>
> ===== PHASE 1: PLAN & BRANCH (QUANT-OPENBB) =====
>
> 1. Create a comprehensive plan file at quant-openbb/docs/plans/feature-portfolio-metrics.md
>    Save it before any coding. Use the format from plans/feature-openbb-transition/
>    phase_0_research_openbb_evaluation.md as a reference. The plan must include:
>      • Objective: enhance /engines/portfolio/snapshot to serve Metric widget-compatible
>        output with percentage formatting and ↑/↓ arrows
>      • Scope: split across two sub-projects (quant-api-gateway + quant-openbb)
>      • Deliverables: new endpoint, formatting utility, tests, docs
>      • Acceptance criteria (testable, measurable)
>      • Full AI agent prompt appended at end (this prompt)
>
> 2. Create a new branch: git checkout -b feat/portfolio-metrics
>
> ===== PHASE 2: QUANT-API-GATEWAY IMPLEMENTATION =====
>
> 3. Create formatting utility module at quant-api-gateway/src/utils/formatting.py:
>    • format_percentage(value: Decimal, decimals: int = 2, use_arrows: bool = True) → str
>      - Multiply by 100
>      - Round to decimals (default 2)
>      - If use_arrows:
>        - If value > 0: return f"↑ +{formatted_value}%"
>        - If value < 0: return f"↓ {formatted_value}%"
>        - If value == 0: return "→ 0.00%"
>      - If not use_arrows: return f"{sign}{formatted_value}%"
>    • format_currency(value: Decimal, currency: str = "USD") → str
>      - Format with thousands separators
>      - Example: "$998,142.71"
>    • Both functions must handle Decimal precisely (no float conversions)
>
> 4. Extend quant-api-gateway/src/schemas/gateway.py:
>    • Add new Pydantic model PortfolioMetricsResponse:
>      - snapshot_date: date (description: "Date of this metrics snapshot")
>      - metrics: list[MetricItem] where MetricItem is:
>        - label: str (e.g., "Daily Return", "Drawdown", "Portfolio Value")
>        - value: str (formatted value, e.g., "+0.63%", "-4.22%", "$998,142.71")
>        - delta: str (optional, formatted delta, e.g., "↑ +0.63%", "↓ -4.22%")
>      - computed_at: datetime (description: "UTC timestamp when computed")
>    • Use frozen=True, ConfigDict, Field descriptions
>    • Ensure all Decimal fields maintain precision
>
> 5. Update quant-api-gateway/src/services/portfolio.py:
>    • Add function: async def build_metrics_response(snapshot: dict[str, Any])
>      → PortfolioMetricsResponse
>    • Logic:
>      - Extract weighted_daily_return → format_percentage()
>      - Extract combined_drawdown (handle None) → format_percentage() or "N/A"
>      - Extract total_portfolio_value → format_currency()
>      - Build metrics list: [daily_return_metric, drawdown_metric, value_metric]
>      - Return PortfolioMetricsResponse(snapshot_date, metrics, computed_at)
>
> 6. Add new endpoint to quant-api-gateway/src/api/v2/engines/portfolio.py:
>    • @router.get("/metrics", response_model=PortfolioMetricsResponse)
>      async def get_metrics_v2(snapshot_date: date | None = None):
>        - Get snapshot from DB (via query_snapshot_by_date or query_latest_snapshot)
>        - Call build_metrics_response(snapshot)
>        - Return PortfolioMetricsResponse
>        - Cache result with key "portfolio_metrics:{snapshot_date}" or "portfolio_metrics:latest"
>    • OR add metrics field to existing PortfolioSnapshotResponse (append only)
>    • If append-only: add optional metrics: PortfolioMetricsResponse | None = None
>
> 7. Update quant-api-gateway tests/api/v2/engines/test_portfolio.py:
>    • test_get_metrics_returns_formatted_percentages()
>    • test_get_metrics_formats_negative_return()
>    • test_get_metrics_handles_null_drawdown()
>    • test_get_metrics_formats_currency()
>    • test_formatting_edge_cases()
>    • All tests must use respx for HTTP mocking or asyncpg connection pooling
>    • Ensure ≥90% coverage on new formatting functions
>
> ===== PHASE 3: QUANT-OPENBB PROXY IMPLEMENTATION =====
>
> 8. Update quant-openbb/src/openbb_quant/router.py:
>    • Add new route (if not already present):
>      @router.get("/engines/portfolio/metrics", response_model=PortfolioMetricsResponse)
>      async def proxy_portfolio_metrics(snapshot_date: date | None = None):
>        if snapshot_date:
>          result = await _client.get(f"engines/portfolio/metrics/{snapshot_date.isoformat()}")
>        else:
>          result = await _client.get("engines/portfolio/metrics")
>        return result
>    • Ensure X-API-Key header forwarded (handled by _client)
>    • Use existing GatewayClient for auth + retry logic
>
> 9. Update quant-openbb/tests/test_router.py:
>    • test_proxy_portfolio_metrics_endpoint()
>    • test_metrics_endpoint_auth_forwarded()
>    • test_metrics_response_format_matches_gateway()
>
> ===== PHASE 4: DOCUMENTATION & FINALIZATION =====
>
> 10. Create/update documentation:
>     a. quant-api-gateway/docs/reference/portfolio.md
>     b. quant-openbb/README.md (OpenBB Metric Widget Example section)
>     c. quant-openbb/docs/plans/feature-portfolio-metrics.md (completion notes)
>
> 11. Quality gate (run locally before commit):
>     a. In quant-api-gateway/:
>        uv run ruff check src tests
>        uv run ruff format --check src tests
>        uv run mypy src tests
>        uv run pytest --cov=src --cov-fail-under=80
>     b. In quant-openbb/:
>        uv run ruff check src tests
>        uv run ruff format --check src tests
>        uv run mypy src tests
>        uv run pytest --cov=src --cov-fail-under=80
>
> 12. Commit and push:
>     git add -A
>     git commit -m "feat(portfolio): add formatted metrics endpoint for OpenBB Metric widget"
>     git push origin feat/portfolio-metrics
>
> 13. Update umbrella repo plan status:
>     • Open plans/feature-openbb-transition/ROADMAP.md
>     • Find Phase 3 section → add note about completion
>     • Commit to umbrella main

### Deviations from this prompt (decided up front, with user approval)

| Prompt said | Plan does | Reason |
|---|---|---|
| `tests/api/v2/engines/test_portfolio.py` | Extend `tests/api/v2/test_engines.py` | The codebase has all v2 engine tests in one file; matching conventions. |
| Gateway coverage gate 80% | Keep at 90% | Existing `pyproject.toml` enforces 90%; no reason to lower. |
| OpenBB proxy with `response_model=PortfolioMetricsResponse` | OpenBB proxy returns `Any`, no `response_model` | All 16 existing proxy endpoints return raw gateway JSON; matches conventions and avoids duplicating the schema. |
| MetricItem `value` plain + `delta` arrowed | Both populated; `value` arrow-formatted (percentages), plain currency; `delta` = day-over-day change vs previous snapshot, arrow-formatted | The user prompt's field descriptions and example response disagreed; user selected the day-over-day variant. Requires `query_previous_snapshot` helper. |
| Single endpoint `/metrics` with optional `snapshot_date` query param | Two endpoints: `/metrics` (latest) + `/metrics/{snapshot_date}` (path param) | Mirrors the existing snapshot pair (path params, not query params); consistent with v2 engine surface. |

---

## Completion Notes

*(Populated at the end of Phase E.)*
