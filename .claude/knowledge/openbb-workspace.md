---
name: openbb-workspace
description: OpenBB Workspace JSON specs, widget types, Dashboard connector patterns, and gotchas
metadata:
  type: reference
---

# OpenBB Workspace — Quick Reference

> Full source: [`docs/openbb/workspace.md`](../../docs/openbb/workspace.md) —
> scraped from https://docs.openbb.co/workspace, 2026-05.

## Widget manifest (`widgets.json`)

Served at `GET /widgets.json`. Each top-level key = one widget ID.

**Required fields**: `name`, `description`, `endpoint`
**Default `type`**: `"table"` (use this for everything unless you have a Plotly endpoint)

| `type` value | What the endpoint must return |
|---|---|
| `"table"` | Bare JSON array `[{...}, ...]` |
| `"chart"` | Plotly figure JSON `{data: [...], layout: {...}}` |
| `"metric"` | `{label, value, delta}` |
| `"markdown"` | Plain text or markdown string |
| `"newsfeed"` | Array of news articles |

**Common optional fields**: `category`, `subCategory`, `params`, `data`,
`refetchInterval` (default 900000ms), `staleTime` (default 300000ms),
`exportable`, `runButton`, `gridData`, `source`, `imgUrl`, `raw`.

### `data` object (AgGrid / table widgets)

```json
"data": {
    "table": {
        "enableCharts": true,
        "chartView": {"enabled": true, "chartType": "line"},
        "columnsDefs": [
            {"field": "date", "headerName": "Date", "chartDataType": "time"},
            {"field": "value", "headerName": "Value", "chartDataType": "series"}
        ]
    }
}
```

- `enableCharts: true` adds a chart toggle to the table toolbar — no Plotly endpoint needed.
- `chartView.chartType` can be: line, column, bar, area, scatter, pie, donut, etc.
- `columnsDefs` fields: `field`, `headerName`, `chartDataType` (`"category"`, `"series"`, `"time"`, `"excluded"`), `cellDataType`, `formatterFn`, `renderFn`, `width`, `hide`, `pinned`.

### `params` schema

| Field | Notes |
|---|---|
| `paramName` | URL query parameter name |
| `type` | `"text"`, `"date"`, `"number"`, `"boolean"`, `"ticker"`, `"endpoint"`, `"form"`, `"tabs"` |
| `value` | Default; date modifier: `$currentDate-1d`, `$currentDate-30d`, `$currentDate-2y` |
| `label` | Display label in the UI |
| `description` | Tooltip |
| `show` | Default true |
| `options` | Static dropdown: `[{label, value}]` |
| `optionsEndpoint` | Dynamic dropdown URL |

## App templates (`apps.json`)

Served at `GET /apps.json`. Returns a **list** of app objects.

**Required**: `name`, `img` (can be `""`), `description`.
**Key fields**: `tabs` (collection of `{id, name, layout}`), `groups` (param sync),
`prompts` (AI suggestions), `allowCustomization`.

**Tab layout**: 40-column grid. Each widget: `{i: "widget_id", x, y, w, h}`.
Widget ID = endpoint with `/` replaced by `_` (e.g. `engines/catalog` → `engines_catalog`).

**Groups** sync params across widgets:
```json
"groups": [{
    "name": "Strategy",
    "type": "param",
    "paramName": "strategy_id",
    "defaultValue": "csm-set",
    "widgetIds": ["widget_a", "widget_b"]
}]
```

## Agent definitions (`agents.json`)

Served at `GET /agents.json`. Returns an object keyed by agent ID.

```json
{
  "agent-id": {
    "agent_id": "agent-id",
    "name": "Display Name",
    "description": "...",
    "endpoints": {"query": "/api/v1/agent/query"},
    "features": {
      "streaming": true,
      "widget-dashboard-select": true,
      "widget-dashboard-search": true
    }
  }
}
```

## `templates.json`

Some Workspace versions request `GET /templates.json`. Return the same
payload as `apps.json`.

## Gotchas we hit

- **`type: "chart"`** — only works if the endpoint returns Plotly figure JSON.
  Our proxy endpoints return plain arrays, so we use `type: "table"` with
  `enableCharts: true` instead.
- **`img` is required** in apps.json — use `""` if you don't have a thumbnail.
- **CORS** — the Dashboard runs at `pro.openbb.co` in the browser, so your
  server MUST return `access-control-allow-origin: *` (or the specific origin).
- **`wsEndpoint`** — only relevant for `type: "live_grid"`. Leave it out otherwise.
- **Auth** — the Dashboard connector supports Header auth. Configure `X-API-Key`
  with the right value in the "Connect backend" dialog.
- **Date params** — use `$currentDate-1d` (not hardcoded dates) so dashboards
  stay current.
- **`columnsDefs`** — without explicit column definitions, AgGrid auto-detects
  types. Add `columnsDefs` when you need chart-ready data types or custom formatting.

## Dashboard connector setup

| Field | Value |
|---|---|
| Name | Any label (e.g. `quant-openbb`) |
| Endpoint URL | `https://openbb.candythink.com` (or `http://host:8500` for local) |
| Validate widgets | Yes |
| Auth Key | `X-API-Key` |
| Auth Value | Must match `QUANT_OPENBB_INTERNAL_API_KEY` |
| Auth Location | Header |
