# Connecting quant-openbb to the OpenBB Workspace

The OpenBB Workspace at [pro.openbb.co](https://pro.openbb.co) can connect to
locally running API backends via its **Data Connectors** feature. This is the
"Connect backend" form you see in the dashboard — it registers your
`quant-openbb` service so the Workspace can call its endpoints and render
widgets.

## Architecture

```
quant-openbb (FastAPI, port 8500)
       |
       |  Workspace calls your endpoints
       |  e.g. GET /api/v2/engines/catalog
       |
       v
OpenBB Workspace (pro.openbb.co)
  → Data Connectors → Connect backend
  → form fields: Name, Endpoint URL, Auth, Validate widgets
```

The Workspace runs in your browser. It reaches your local API via the address
you enter — typically `http://127.0.0.1:<port>`.

---

## 1. Quick connect (standalone mode)

This is the simplest approach. Your `quant-openbb` is already running as a
standalone FastAPI app on port 8500.

### 1.1 Start quant-openbb

```bash
uv sync
cp .env.example .env       # fill in QUANT_OPENBB_INTERNAL_API_KEY
uv run uvicorn openbb_quant.main:app --reload --port 8500
curl -sf http://localhost:8500/health
```

### 1.2 Fill in the Connect backend form

At `pro.openbb.co` → **Data Connectors** → **Add Data**:

| Field | Value | Notes |
| --- | --- | --- |
| **Name** | `quant-trading-system` | Any descriptive name you want |
| **Endpoint URL** | `http://127.0.0.1:8500` | The API root. Use `localhost` if `127.0.0.1` doesn't work. |
| **Validate widgets** | `No` | The endpoints don't have OpenBB widget annotations |
| **Key** | `X-API-Key` | Same header name used for gateway outbound calls |
| **Value** | your `QUANT_OPENBB_INTERNAL_API_KEY` value | From your `.env` |
| **Location** | `Header` | |

- Click **Test** to verify the connection reaches `/health`
- If the test passes, click **Add**

### 1.3 Verify in the Workspace

Once connected, try searching for one of the proxied endpoints in the Workspace
search bar:

```
/api/v2/engines/catalog
/api/v2/engines/portfolio/overall-performance
/api/v2/engines/portfolio/strategies
```

The raw JSON response will be displayed. To get rich table/metric/chart widgets
instead, see section 4 below.

---

## 2. Connect via openbb-api (with widget support)

The `openbb-api` command is an alternative to `uvicorn` that wraps your FastAPI
app with OpenBB Platform metadata, making endpoints discoverable as rich
widgets in the Workspace. It comes from the `openbb-platform-api` package.

### 2.1 Install openbb-platform-api

```bash
uv add openbb-platform-api
```

Or install the full OpenBB platform:

```bash
uv add openbb
```

### 2.2 Launch with openbb-api

```bash
uv run openbb-api --app src/openbb_quant/main.py --reload
```

This starts the server on `http://127.0.0.1:6900` by default. To use a
different port:

```bash
uv run openbb-api --app src/openbb_quant/main.py --port 8500 --reload
```

### 2.3 Fill in the Connect backend form

Same fields as section 1.2, but the Endpoint URL should match whatever port
`openbb-api` is using (default `http://127.0.0.1:6900`).

---

## 3. Authentication

`quant-openbb` now supports optional inbound API-key authentication. It reuses
the same `QUANT_OPENBB_INTERNAL_API_KEY` from your `.env`.

**When the key is set (non-empty):**
- Every `/api/v2/*` request must carry an `X-API-Key` header matching the key.
- Failures return HTTP 401 with a JSON body.

**When the key is empty (default):**
- All requests are allowed — backward compatible.

`/health` is always open (it runs on the app, not the router).

In the Workspace "Connect backend" form, fill in the auth section:

| Field | Value |
| --- | --- |
| **Key** | `X-API-Key` |
| **Value** | your `QUANT_OPENBB_INTERNAL_API_KEY` value |
| **Location** | `Header` |

---

## 4. Enhancing endpoints for rich widgets

By default, the quant proxy endpoints return raw JSON (typed `Any`), which the
Workspace displays as plain text. To get rich **table**, **metric**, and
**chart** widgets, return properly typed responses from annotated endpoints.

### 4.1 Table widget example

```python
from typing import Annotated
from fastapi import FastAPI, Query
from openbb_core.provider.abstract.data import Data
from pydantic import Field

class StrategySummary(Data):
    """Active strategy in the portfolio."""
    id: str = Field(title="Strategy ID", description="Gateway-registered strategy slug")
    name: str = Field(title="Name")
    type: str = Field(title="Type")
    capital_weight: float = Field(
        title="Capital Weight",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    active: bool = Field(title="Active")

@app.get("/api/v2/engines/portfolio/strategies")
async def list_strategies() -> list[StrategySummary]:
    """Registered portfolio strategies."""
    raw = await _client.get("engines/portfolio/strategies")
    return [StrategySummary.model_validate(r) for r in raw]
```

### 4.2 Metric widget example

```python
@app.get("/api/v2/engines/portfolio/overall-performance")
async def overall_perf() -> str:
    """Aggregate portfolio performance KPI."""
    raw = await _client.get("engines/portfolio/overall-performance")
    md = f"""# Portfolio Overview
| Metric | Value |
|---|---|
| Total Value | ${raw['total_portfolio_value']:,.2f} |
| Daily Return | {raw['weighted_daily_return']:.4%} |
| Max Drawdown | {raw['combined_max_drawdown']:.4%} |
| Active Strategies | {raw['active_strategies']} |
"""
    return md
```

### 4.3 Available widget types

| Return type | Widget rendered |
| --- | --- |
| `str` | Markdown card |
| `list[dict]` | Table |
| `list[BaseModel]` | Rich table (column titles, units, formatting) |
| `dict` (Plotly JSON) | Chart |
| `OBBject` | OpenBB-standard response |

### 4.4 OpenBB annotations that drive the UI

| Mechanism | Effect in Workspace |
| --- | --- |
| `Field(title="...")` | Column header |
| `Field(description="...")` | Column hover tooltip |
| `Query(description="...")` | Parameter hover tooltip |
| `Literal["A","B"]` | Dropdown parameter |
| `json_schema_extra={"x-unit_measurement": "percent"}` | Percent formatting |
| `json_schema_extra={"x-frontend_multiply": 100}` | Auto-multiply decimals → percents |
| Docstring on endpoint | Widget description in search results |

---

## 5. Docker + Workspace connectivity

When running in Docker, the Workspace (running in your browser) needs to reach
the container's host port.

### 5.1 Default compose (already works)

The `docker-compose.yml` already maps host `:8500` → container `:8000`:

```yaml
ports:
  - "8500:8000"
```

In the Connect backend form, use `http://127.0.0.1:8500` as the Endpoint URL.
The browser connects to the host port, which forwards to the container.

### 5.2 Full-platform mode in Docker

To also have OpenBB data providers available through the same container, switch
the entry point and add provider packages:

```bash
# In pyproject.toml, add:
uv add openbb openbb-yfinance
```

```dockerfile
# In Dockerfile, after the builder stage:
RUN uv pip install openbb openbb-yfinance --prefix /opt/venv
```

Override the CMD in `docker-compose.yml`:

```yaml
services:
  quant-openbb:
    command:
      - uvicorn
      - openbb_core.api.rest_api:app
      - --host
      - "0.0.0.0"
      - --port
      - "8000"
```

Then in the Connect backend form, Endpoint URL is still `http://127.0.0.1:8500`.

---

## 6. Running both modes simultaneously

Standalone proxy on `:8500`, full platform on another port:

```bash
# Terminal 1 — standalone proxy
uv run uvicorn openbb_quant.main:app --port 8500

# Terminal 2 — full platform (quant + providers)
uv run uvicorn openbb_core.api.rest_api:app --port 8501
```

Register both as separate backends in the Workspace if needed.

---

## 7. Troubleshooting

### Test fails ("unable to connect")

- Verify the server is running: `curl -sf http://127.0.0.1:8500/health`
- In Docker, ensure the port mapping is correct: `docker compose ps`
- Safari/Brave block HTTP connections to localhost. Use Chrome, or set up
  HTTPS via [OpenBB's self-signed certificate guide](https://docs.openbb.co/odp/desktop/backends#self-signed-certificate).

### Endpoints return 502/504

The upstream gateway is down. Bring-up order: `quant-infra-db` →
`quant-api-gateway` → `quant-openbb`.

### Widgets show as raw JSON instead of tables/charts

Endpoints return untyped JSON (`Any`). To get rich widgets, wrap responses in
typed Pydantic models (see section 4) or return Markdown strings.

### openbb-api not found

Install the package: `uv add openbb-platform-api`

### ngrok for remote access

To access your local quant-openbb from anywhere (e.g., mobile):

```bash
ngrok http 8500
```

In the Connect backend form, replace the Endpoint URL with the ngrok
forwarding URL (e.g., `https://abc123.ngrok.io`). Add an auth header:

| Field | Value |
| --- | --- |
| **Key** | `ngrok-skip-browser-warning` |
| **Value** | `x` |
| **Location** | `Header` |
