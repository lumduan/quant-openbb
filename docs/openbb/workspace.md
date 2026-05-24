---
tags:
  - openbb
  - workspace
  - documentation
  - widget
  - dashboard
  - mcp
  - ai
  - fastapi
  - reference
status: reference
created: 2026-05-24
---

# OpenBB Workspace — Comprehensive Documentation Notes

> Source: https://docs.openbb.co/workspace | Last scraped: 2026-05
> OpenBB Workspace is a secure application for enterprise AI workflows combining flexible data integration, customizable UI components, and AI capabilities in a single solution. Live at: https://pro.openbb.co

---

## Table of Contents

- [[#Getting Started]]
- [[#Analyst — Widgets]]
- [[#Analyst — Dashboards]]
- [[#Analyst — Apps]]
- [[#Analyst — AI Features (Copilot)]]
- [[#Excel Add-in]]
- [[#Developers — Data Integration]]
- [[#Developers — Widget Types]]
- [[#Developers — Widget Parameters]]
- [[#Developers — Widget Configuration]]
- [[#Developers — JSON Specs (widgets.json & apps.json)]]
- [[#Agents — Workspace MCP]]

---

## Getting Started
### - [Workspace Overview](https://docs.openbb.co/workspace)
### - [Progressive Web App (PWA)](https://docs.openbb.co/workspace/getting-started/pwa)
### - [OpenBB Python Package](https://docs.openbb.co/workspace/getting-started/platform-installer)
### - [FAQs](https://docs.openbb.co/workspace/getting-started/faqs)


---

## Workspace Overview
> https://docs.openbb.co/workspace

OpenBB Workspace is a **secure enterprise AI workflow platform** that combines:
- **Production-Ready UI Framework** — fully customizable, team-shared dashboards
- **Unified Data Integration** — proprietary + licensed + public data in one interface
- **AI Agent Integration** — deploy any AI agent (proprietary, open-source, third-party) in a controlled environment
- **Enterprise-Grade Deployment** — on-premises or private cloud; role-based access controls

### Key Concepts

#### Widgets
Self-contained data components with:
- **Data Source**: internal or external API
- **Metadata**: title, description, category, sub-category, source
- **Visual Layer**: tables, charts, PDFs, images, newsfeeds, etc.
- **Parameters**: configurable inputs for user interaction

#### Dashboards
- Personal analytical spaces starting from a blank canvas
- Add widgets and **link parameters** (change a ticker in one widget → all linked widgets update)
- Supports static files (PDFs, images, spreadsheets), AI-generated artifacts, notes
- Shareable with the whole organization

#### AI Agents (Copilot)
- Contextually aware: understand widget relationships, maintain multi-query context
- Can monitor dashboards for anomalies, respond to queries, generate visualizations
- Produce **artifacts** (text, tables, charts) that go back onto the dashboard

#### Apps
- Pre-built dashboard templates for specific workflows
- Curated widgets + linked parameters + default AI agent + custom prompts
- Examples: portfolio management, market surveillance, fundamental research
- Unlimited apps, shareable across teams

---

## Getting Started (PWA & Installation)
> https://docs.openbb.co/workspace/getting-started/pwa

### Progressive Web App (PWA)
Install at `https://pro.openbb.co` as a PWA for:
- App-like experience (runs in its own window)
- Quick launch from dock/taskbar/home screen
- Cross-platform (desktop + mobile)
- Better performance via cached resources

**Desktop**: Chrome/Edge → install icon in address bar
**iOS**: Safari → Share → Add to Home Screen
**Android**: Chrome → 3-dot menu → Add to Home Screen

### OpenBB Python Package (Platform Installer)
> https://docs.openbb.co/workspace/getting-started/platform-installer

Integrates the open-source [ODP Python Package](https://github.com/OpenBB-finance/OpenBB) (350+ datasets) into OpenBB Workspace in ~5 minutes.
- Runs on `http://127.0.0.1:6900` by default
- Use **ngrok** to expose locally and access from mobile
- Filter available widgets via the [widgets filter page](https://my.openbb.co/app/platform/widgets) → download `widget_settings.json`
- Safari/Brave need HTTPS — use self-signed cert with `openbb-api --ssl_keyfile localhost.key --ssl_certfile localhost.crt`

### FAQs
> https://docs.openbb.co/workspace/getting-started/faqs

**Auth on custom backend**: Configure Header or Query Parameter auth when adding backend in Workspace.
**Refresh issues**: Check `refetchInterval`, `staleTime`, `runButton` settings.
**Debug checklist**: Backend running? URL correct? Test with curl/Postman? Browser console CORS errors? Valid JSON in widgets.json?
**Parameter grouping**: Use identical `paramName` across widgets so they synchronize.
**Dynamic dropdowns**: Set `type: "endpoint"` + `optionsEndpoint` URL on the param.

---

## Analyst — Widgets
> https://docs.openbb.co/workspace/analysts/widgets/overview

### Core Widgets
- **Table widget**: sortable, filterable, exportable AgGrid table
- **Chart widget**: line, bar, area, pie, scatter, heatmap, etc. (powered by AgGrid + Plotly)
- **Metric widget**: key KPIs with labels, values, delta changes
- **Markdown widget**: rich-text notes / analysis with markdown formatting
- **News widget**: newsfeed with article preview and full body
- **PDF/Image/File viewer**: view PDFs and images inline

### Interacting With Data
- **Sorting & Filtering**: click column headers; filter by value
- **Cell click grouping**: click a cell → filters linked widgets by that value (requires `renderFn: "cellOnClick"` + `actionType: "groupBy"`)
- **Chart view toggle**: switch between table and chart using toolbar
- **Export**: download data as CSV/Excel
- **Sparklines**: mini inline charts inside table cells

### Static Files
- Upload PDFs, images, text files, spreadsheets directly to dashboards
- Files stored in workspace and remain on the dashboard

### AI-generated Widgets
- Copilot outputs (tables, charts, markdown) can be saved as dashboard widgets
- "Generative UI" feature adds them automatically when enabled

### Sandbox Widgets
- Pre-built demo widgets available at Apps tab → OpenBB Sandbox
- For demo/inspiration only — not for production financial decisions

---

## Analyst — Dashboards
> https://docs.openbb.co/workspace/analysts/dashboards

- **Blank canvas**: add widgets, PDFs, notes, AI artifacts
- **Parameter linking**: same `paramName` across widgets = synchronized updates
- **Navigation bar / tabs**: organize widgets into tab groups
- **Sharing**: share with team members; becomes an organizational asset
- **Grid layout**: 40-column grid; each widget has `x`, `y`, `w`, `h` positioning

---

## Analyst — Apps
> https://docs.openbb.co/workspace/analysts/apps

Apps = pre-configured dashboard templates:
- Curated widget set with linked parameters
- Pre-selected AI agent for the workflow
- Custom **prompts** that auto-tag relevant widgets
- Examples: portfolio management, macro analysis, earnings review

Apps are defined in `apps.json` and served via your API. See [[#Developers — JSON Specs (widgets.json & apps.json)]].

---

## Analyst — AI Features (Copilot)
> https://docs.openbb.co/workspace/analysts/ai-features/copilot-basics

### Copilot Basics
The OpenBB Copilot is an AI-powered financial analyst assistant integrated into Workspace. Built on latest OpenAI models (Azure OpenAI available for enterprise).

**Interface structure**:
- **Header**: conversation management (new chat, clear, fullscreen, hide)
- **Body**: chat window with step-by-step reasoning, charts, tables, code output
- **Footer**: context management — add widgets, attach files, open prompt library, select agent

**Prompt Library**: save and reuse complex prompts (can tag specific widgets for context)

### Context Management
> https://docs.openbb.co/workspace/analysts/ai-features/copilot-context

Context priority (highest to lowest):

| Priority | Type | Description |
|---|---|---|
| 1 | **Explicit** | Widgets, skills, or MCP tools tagged directly |
| 2 | **Skill** | Skills added under AI Library |
| 3 | **MCP Tool** | Active MCP tools connected to Copilot |
| 4 | **Attached Files** | PDFs, Excel, CSV uploaded to chat |
| 5 | **Dashboard** | All widgets on current dashboard (all tabs) |
| 6 | **Conversation** | Current conversation history |
| 7 | **Global Data** | All widgets in workspace (when Global Data ON) |
| 8 | **Web Search** | Real-time web search (when Web Search ON) |

**Explicit context**:
- Tag a widget with `@widget-name` or "Add to context" button
- Tag a skill with `/skill:skill-name`
- Tag an MCP tool with `/` command

**Global Data**: when enabled, Copilot can pull from entire widget library beyond current dashboard. Metadata quality is critical for this to work.

**Web Search**: fallback when workspace data is insufficient or for real-time info.

### MCP Tools (for Analysts)
> https://docs.openbb.co/workspace/analysts/ai-features/mcp-tools

Connect Copilot to third-party data providers via MCP (Model Context Protocol):
- Supports HTTP/SSE protocols (not STDIO — use [supergateway](https://github.com/supercorp-ai/supergateway) for STDIO)
- Uses [use-mcp library](https://github.com/modelcontextprotocol/use-mcp)
- **Configure**: Copilot → MCP server menu → Manage MCP servers → Add server (name + URL + optional auth header)
- **Select tools**: enable/disable individual tools per server
- **Explicit call**: type `/` → select specific tool to guarantee invocation
- **Widget matching**: configure `mcp_tool` in `widgets.json` to link a widget to an MCP tool → click the `*` citation to "Add matching widget to dashboard"

### Generative UI
> https://docs.openbb.co/workspace/analysts/ai-features/generative-ui

When Generative UI is enabled, Copilot can:
- **Update widget parameters** automatically based on your prompt
- **Add widgets from Global Data** to the dashboard when it finds relevant data
- **Add markdown note widgets** with text content directly on the dashboard
- **Add/edit navigation bar** (tabs) on the dashboard
- **Create widgets on the fly** from its own outputs (tables, charts, notes → interactive dashboard widgets)

### Skills
> https://docs.openbb.co/workspace/analysts/ai-features/skills

Skills = reusable instruction sets for Copilot.

**Creating**: AI Library → Skills tab → Add Skill → name + description + instructions
**Invoking**:
- Mention the skill name in your prompt (Copilot auto-detects)
- Force with `/skill:skill-name`
- Type `/` to see all available skills + MCP tools

**Built-in example**: `/openbb-html-report` — generates a full HTML report from dashboard data

---

## Excel Add-in
> https://docs.openbb.co/workspace/analysts/excel-addin/excel-overview

Two functions:
- **OBB.GET** — fetches data from any connected OpenBB backend endpoint directly into Excel cells
- **OBB.WIDGET** — embeds an OpenBB widget directly inside an Excel sheet

**Installation**: available in Microsoft AppSource or via direct install from OpenBB Workspace settings.

---

## Developers — Data Integration
> https://docs.openbb.co/workspace/developers/data-integration

A **custom backend** is an API that returns data in a format OpenBB Workspace understands, with widgets specified in a `widgets.json` file.

**Steps**:
1. Create API server (FastAPI, Flask, Express, etc.)
2. Create `widgets.json` to define widget properties (name, description, category, endpoint, type, params)
3. Connect to OpenBB Workspace via "Manage Backends"

**Hello World example** (FastAPI + `@register_widget` decorator):
```python
from fastapi import FastAPI
from openbb_workspace import register_widget

app = FastAPI()

@register_widget({
    "name": "Hello World",
    "description": "A simple markdown widget",
    "category": "Hello World",
    "type": "markdown",
    "endpoint": "hello_world",
    "gridData": {"w": 12, "h": 4},
    "source": "None",
    "params": []
})
@app.get("/hello_world")
def hello_world():
    return "# Hello World"
```

The `@register_widget` decorator builds the `widgets.json` entry. Alternatively, write `widgets.json` manually.

**Reference Backend**: see [backend-examples-for-openbb-workspace](https://github.com/OpenBB-finance/backend-examples-for-openbb-workspace) for tested, documented examples.

---

## Developers — Widget Types

### [Markdown](https://docs.openbb.co/workspace/developers/widget-types/markdown)
Returns markdown string. Supports images (converted to base64).
```python
@register_widget({"name": "...", "type": "markdown", "endpoint": "...", "gridData": {"w": 12, "h": 4}})
@app.get("/markdown_widget")
def markdown_widget():
    return "# Markdown Widget"
```

### [HTML](https://docs.openbb.co/workspace/developers/widget-types/html)
Returns server-rendered HTML. **JavaScript is NOT executed** (security restriction). All interactivity via server-side logic + CSS.
```python
from fastapi.responses import HTMLResponse

@register_widget({"name": "...", "type": "html", "endpoint": "...", "gridData": {"w": 40, "h": 20}})
@app.get("/html_widget", response_class=HTMLResponse)
def html_widget():
    return "<html><body>...</body></html>"
```

### [Metric](https://docs.openbb.co/workspace/developers/widget-types/metric)
Displays KPIs with label, value, and delta. Returns a list of metric objects or a single metric.
```python
@register_widget({"name": "...", "type": "metric", "endpoint": "...", "gridData": {"w": 5, "h": 5}})
@app.get("/metric_widget")
def metric_widget():
    return [
        {"label": "Total Users", "value": "1,234,567", "delta": "+5.2%"},
        {"label": "Revenue",     "value": "$45.2M",    "delta": "+2.1%"}
    ]
```

### [File Viewer](https://docs.openbb.co/workspace/developers/widget-types/file-viewer)
Displays PDFs and other files. Two approaches:
- **PDF via URL** (`"type": "pdf"`) — return a URL reference (efficient for large files)
- **PDF via base64** — return base64-encoded content inline

### [AgGrid Table/Charts](https://docs.openbb.co/workspace/developers/widget-types/aggrid-table-charts)
Default table widget powered by AG Grid. Supports:
- Column definitions, sorting, filtering, grouping
- Built-in chart view (20+ chart types)
- Sparklines inside cells
- `enableCharts: true` in `widgets.json` to enable chart switching

### [SSRM Mode (Server-Side Row Model)](https://docs.openbb.co/workspace/developers/widget-types/ssrm_mode)
For very large datasets — server-side pagination, filtering, sorting.
```json
{ "type": "ssrm_table", "endpoint": "data-ssrm" }
```
The widget type **must** be `"ssrm_table"`.

### [Plotly Charts](https://docs.openbb.co/workspace/developers/widget-types/plotly-charts)
Returns `fig.to_json()` (parsed with `json.loads`). Type = `"chart"`.

**Theme support**: accept `theme: str = "dark"` parameter — Workspace passes the user's current theme.
- Dark background: `#151518` | Light: `#FFFFFF`

**Raw data toggle**: set `"raw": true` in widgets.json + `raw: bool = False` param → Copilot can access underlying data.

**Toolbar config**: use `plotly_config.py` helper for reusable toolbar/styling.

```python
@register_widget({"name": "...", "type": "chart", "endpoint": "...", "gridData": {"w": 40, "h": 15}})
@app.get("/plotly_chart")
def get_plotly_chart(theme: str = "dark"):
    fig = go.Figure()
    # ... build chart ...
    return json.loads(fig.to_json())
```

### [Newsfeed](https://docs.openbb.co/workspace/developers/widget-types/newsfeed)
Returns list of article objects. Type = `"newsfeed"`.
```python
# Each article:
{
    "title":   "Article Title",
    "date":    "2024-01-15T10:30:00",  # ISO 8601
    "author":  "Author Name",
    "excerpt": "Short preview...",
    "body":    "# Full Article\n\nMarkdown supported..."
}
```

### [Live Grid](https://docs.openbb.co/workspace/developers/widget-types/live-grid)
Real-time WebSocket table. Type = `"live_grid"`.
- `wsEndpoint`: WebSocket endpoint for live updates
- `wsRowIdColumn`: column that links WebSocket updates to table rows
- `enableCellChangeWs: false` on specific columns to prevent WS updates
- `renderFn: "showCellChange"` + `renderFnParams.colorValueKey` for color-coded updates

```python
@register_widget({
    "type": "live_grid",
    "endpoint": "live_grid_data",
    "wsEndpoint": "live_grid_ws",
    "data": {
        "wsRowIdColumn": "symbol",
        "table": { "columnsDefs": [...] }
    }
})
```

### [Omni / SQL / Python](https://docs.openbb.co/workspace/developers/widget-types/omni)
Versatile widget that can return **markdown, table, or chart** dynamically. Uses **POST** requests (not GET). Requires `prompt` param.

```python
class DataFormat(BaseModel):
    data_type: str
    parse_as: Literal["text", "table", "chart"]

class OmniWidgetResponse(BaseModel):
    content: Any
    data_format: DataFormat
    citable: bool = False

@app.post("/omni-widget")
async def get_omni(data: str | dict = Body(...)):
    if isinstance(data, str): data = json.loads(data)
    prompt = data.get("prompt", "")
    # Return text:
    return OmniWidgetResponse(content=prompt, data_format=DataFormat(data_type="object", parse_as="text"))
```

**SQL Widget**: use `"language": "sql"` param for SQL syntax highlighting; replace `DATA` with actual table name.
**Python Widget**: use `"language": "python"` param for Python syntax highlighting; execute code in restricted namespace with `go` (plotly).

**Config**:
```json
{ "type": "omni", "endpoint": "omni-widget",
  "params": [{"paramName": "prompt", "type": "text", "show": false}] }
```

### [YouTube](https://docs.openbb.co/workspace/developers/widget-types/youtube)
Returns a YouTube URL as `PlainTextResponse`. Type = `"youtube"`.
- **With AI transcript**: set `"raw": true` in config; endpoint returns URL normally but transcript when `?raw=true`
- Return transcript as `PlainTextResponse(content=transcript, media_type="text/markdown")`

### [TradingView Charts](https://docs.openbb.co/workspace/developers/widget-types/tradingview-charts)
Implements TradingView UDF (Universal Data Feed) protocol. Type = `"advanced_charting"`.

Required UDF endpoints:
- `GET /udf/config` — supported resolutions, exchanges, symbol types
- `GET /udf/search` — symbol search
- `GET /udf/symbols` — symbol info (name, type, pricescale, session, timezone)
- `GET /udf/history` — OHLCV data: `{"s": "ok", "t": [...], "o": [...], "h": [...], "l": [...], "c": [...], "v": [...]}`
- `GET /udf/time` — server timestamp

```python
@register_widget({
    "type": "advanced_charting",
    "endpoint": "/udf",
    "data": {"defaultSymbol": "AAPL", "updateFrequency": 60000}
})
def tradingview_chart(): pass
```

### [Highcharts](https://docs.openbb.co/workspace/developers/widget-types/highcharts)
Type = `"chart-highcharts"`. Uses `highcharts_core` Python package.
```bash
pip install highcharts-core
```
Returns `chart.to_dict()`. Supports full theme customization.

### [Vega-Lite](https://docs.openbb.co/workspace/developers/widget-types/vega-lite)
Type = `"chart-vegalite"`. Returns a valid Vega-Lite JSON specification. No extra Python package required (optionally use `altair`).
```python
return {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "width": "container", "height": "container",
    "data": {"values": [...]},
    "mark": {"type": "bar", "color": "#60a5fa"},
    "encoding": {"x": {"field": "era", "type": "nominal"}, "y": {"field": "total", "type": "quantitative"}}
}
```

---

## Developers — Widget Parameters

### [Parameter Positioning](https://docs.openbb.co/workspace/developers/widget-parameters/parameter-positioning)
By default all params in one row. Use nested arrays for multi-row layout:
```json
"params": [
    [],                  // empty row 1 (skip)
    [                    // row 2
        {"paramName": "ticker", "type": "text", ...},
        {"paramName": "date",   "type": "date", ...}
    ],
    [                    // row 3
        {"paramName": "show_volume", "type": "boolean", ...}
    ]
]
```
Order within each row = display order.

### [Date Picker](https://docs.openbb.co/workspace/developers/widget-parameters/date-picker)
```json
{"paramName": "date_picker", "type": "date", "value": "$currentDate-1d", "label": "Select Date"}
```
**Date modifiers**: `$currentDate±N[h/d/w/M/y]` — e.g. `$currentDate-2y`, `$currentDate+1d`. Set `null` for no default.

### [Text Input](https://docs.openbb.co/workspace/developers/widget-parameters/text-input)
```json
{"paramName": "text_box", "type": "text", "value": "hello", "label": "Enter Text"}
```
**Multi-value**: add `"multiple": true` — users can type comma-separated values.

### Boolean Toggle
```json
{"paramName": "show_volume", "type": "boolean", "value": true, "label": "Show Volume"}
```

### [Number Input](https://docs.openbb.co/workspace/developers/widget-parameters/number-input)
```json
{"paramName": "number_box", "type": "number", "value": 20, "label": "Enter Number"}
```

### Dropdown (Static)
```json
{"paramName": "interval", "type": "text", "value": "1d", "options": [
    {"label": "Daily", "value": "1d"},
    {"label": "Weekly", "value": "1w"}
]}
```

### Dropdown (Dynamic / Endpoint)
```json
{"paramName": "ticker", "type": "endpoint", "optionsEndpoint": "/get_tickers", "value": "AAPL"}
```
Endpoint returns: `[{"label": "Apple", "value": "AAPL"}, ...]`

### Multi-select Dropdown
Add `"multiSelect": true` to any param with options. Selected values sent as comma-separated string.

### [Dependent Dropdown](https://docs.openbb.co/workspace/developers/widget-parameters/dependent-dropdown)
Second dropdown filters based on first dropdown's value:
```json
{
    "paramName": "document_type",
    "type": "endpoint",
    "optionsEndpoint": "/document_options",
    "optionsParams": {"category": "$category"}  // $category = value of 'category' param
}
```
The `$paramName` syntax references another parameter's current value.

---

## Developers — Widget Configuration

### [Grid Size](https://docs.openbb.co/workspace/developers/widget-configuration/grid-size)
```json
"gridData": {"w": 20, "h": 9}
```
- **Width (w)**: 10–40 units (40 = full width, 12 = good default)
- **Height (h)**: 4–100 units (4–8 for simple, 8–20 for standard)
- Optional: `minW`, `minH`, `maxW`, `maxH`

### [Render Functions](https://docs.openbb.co/workspace/developers/widget-configuration/render-functions)
Customize cell display in `columnsDefs`:

| Function | Description |
|---|---|
| `greenRed` | Green/red color based on positive/negative value |
| `titleCase` | Convert text to Title Case |
| `hoverCard` | Show extra info on hover |
| `cellOnClick` | Trigger action on cell click (groupBy, openUrl, sendToAgent) |
| `columnColor` | Conditional cell color based on rules |
| `showCellChange` | Highlight cell changes (Live Grid only) |

**Color rules**: conditions: `eq`, `ne`, `gt`, `lt`, `gte`, `lte`, `between`, `contains`, `notContains`

```json
"renderFn": "columnColor",
"renderFnParams": {
    "colorRules": [
        {"condition": "between", "range": {"min": 50, "max": 90}, "color": "blue", "fill": true},
        {"condition": "lt", "value": 50, "color": "red", "fill": true},
        {"condition": "gt", "value": 90, "color": "green", "fill": true}
    ]
}
```

**Hover card**:
```json
"renderFn": "hoverCard",
"renderFnParams": {
    "hoverCard": {
        "cellField": "value",
        "title": "Details",
        "markdown": "### {value}\n- **Info:** {description}"
    }
}
```

**Cell click → group by** (filters linked widgets):
```json
"renderFn": "cellOnClick",
"renderFnParams": {
    "actionType": "groupBy",
    "groupBy": {"paramName": "symbol", "valueField": "companyId"}
}
```
Use `valueField` when displayed value ≠ API param value (e.g., company name vs ticker).

**Cell click → send to agent**:
```json
"renderFn": "cellOnClick",
"renderFnParams": {
    "actionType": "sendToAgent",
    "sendToAgent": {
        "markdown": "Analyze **{company}** with revenue ${revenue}M",
        "agentId": "financial-analyst-agent"  // optional
    }
}
```
Template variables: `{fieldName}` references row data fields.

**Multiple render functions**: pass array `"renderFn": ["cellOnClick", "columnColor"]`

### [Stale Time / Refetch Interval](https://docs.openbb.co/workspace/developers/widget-configuration/stale-time)
```json
"refetchInterval": 900000,   // ms (15 min default); or cron "0 10 * * 1-5"
"staleTime":       300000,   // ms (5 min default) — refresh on next visit after this
"dataUpdateDisplay": "0 10 * * 1-5"  // cron for "Data update" tooltip
```
`refetchInterval` minimum: 1000ms. `false` = no auto-refresh.

### Run Button
```json
"runButton": true  // shows run button instead of refresh; data only refreshes on manual click
```

---

## Developers — JSON Specs (widgets.json & apps.json)

### [widgets.json Reference](https://docs.openbb.co/workspace/developers/json-specs/widgets-json-reference)

Each key in `widgets.json` maps to one widget. Full attribute list:

**Top-level fields**:
| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✓ | Display name |
| `description` | string | ✓ | Description for user + AI (important for Copilot!) |
| `endpoint` | string | ✓ | API endpoint path |
| `wsEndpoint` | string | | WebSocket endpoint (Live Grid only) |
| `category` | string | | Widget category |
| `subCategory` | string | | Sub-category |
| `type` | string | | `"table"` (default), `"chart"`, `"markdown"`, `"metric"`, `"newsfeed"`, `"live_grid"`, `"ssrm_table"`, `"html"`, `"youtube"`, `"advanced_charting"`, `"chart-highcharts"`, `"chart-vegalite"`, `"omni"` |
| `raw` | boolean | | Plotly raw data toggle (default false) |
| `runButton` | boolean | | Show run button (default false) |
| `exportable` | boolean | | Allow data export (default true) |
| `gridData` | object | | `{w, h, minW, minH, maxW, maxH}` |
| `refetchInterval` | number/string | | ms or cron (default 900000) |
| `staleTime` | number | | ms (default 300000) |
| `dataUpdateDisplay` | string | | Cron expression for tooltip |
| `source` | array of strings | | Data source labels |
| `mcp_tool` | object | | `{mcp_server, tool_id}` to link widget to MCP tool |
| `imgUrl` | string | | Preview image URL for widget picker |
| `params` | array | | Parameter definitions (see below) |
| `data` | object | | Table/grid configuration |

**`data` object** (for AgGrid widgets):
```json
"data": {
    "dataKey": "customKey",
    "wsRowIdColumn": "symbol",
    "table": {
        "enableCharts": true,
        "showAll": true,
        "transpose": false,
        "enableAdvanced": true,
        "enableFormulas": true,
        "formatterFn": "none",
        "chartView": {
            "enabled": true,
            "chartType": "column",
            "cellRangeCols": {"line": ["ticker", "weight"]}
        },
        "columnsDefs": [...]
    }
}
```

**`columnsDefs` fields**:
| Field | Description |
|---|---|
| `field` | JSON data field name |
| `headerName` | Column header label |
| `chartDataType` | `"category"`, `"series"`, `"time"`, `"excluded"` |
| `cellDataType` | `"text"`, `"number"`, `"boolean"`, `"date"`, `"dateString"`, `"object"` |
| `align` | `"left"`, `"center"`, `"right"` |
| `formatterFn` | `"int"`, `"none"`, `"percent"`, `"normalized"`, `"normalizedPercent"`, `"dateToYear"` |
| `decimalPlaces` | Override decimal places for this column |
| `renderFn` | Render function(s) |
| `renderFnParams` | Render function config |
| `width`, `maxWidth`, `minWidth` | Column size in px |
| `hide` | Boolean |
| `pinned` | `"left"` or `"right"` |
| `prefix`, `suffix` | Add prefix/suffix to cell values |
| `headerTooltip` | Tooltip on hover over header |
| `sparkline` | `{type: "line"/"area"/"bar", dataField, options: {...}}` |

**`params` fields**:
| Field | Description |
|---|---|
| `paramName` | URL param name |
| `type` | `"date"`, `"text"`, `"ticker"`, `"number"`, `"boolean"`, `"endpoint"`, `"form"`, `"tabs"` |
| `value` | Default value |
| `label` | UI label |
| `description` | Tooltip description |
| `show` | Display in UI (default true) |
| `options` | `[{label, value, extraInfo?}]` for static dropdown |
| `optionsEndpoint` | URL for dynamic options |
| `optionsParams` | Params to pass to options endpoint (use `$paramName` to reference other params) |
| `multiSelect` | Allow multiple selection |
| `multiple` | Allow multiple text values (comma-separated) |
| `language` | `"sql"` or `"python"` for syntax highlighting (Omni widget) |
| `style` | `{"popupWidth": 450}` |

**Special: Date Modifier**: `$currentDate±N[h/d/w/M/y]`, e.g. `$currentDate-2y`. Set `null` for no default.

**ChartView chart types**: column, groupedColumn, stackedColumn, normalizedColumn, bar, groupedBar, stackedBar, normalizedBar, line, scatter, bubble, pie, donut, area, stackedArea, normalizedArea, histogram, radarLine, radarArea, nightingale, radialColumn, radialBar, sunburst, rangeBar, rangeArea, boxPlot, treemap, heatmap, waterfall

**formatterFn**: `int`, `none`, `percent`, `normalized`, `normalizedPercent`, `dateToYear`

**Example complete widget**:
```json
{
  "custom_widget": {
    "name": "Custom Widget",
    "description": "Demo widget",
    "endpoint": "custom-endpoint",
    "type": "table",
    "gridData": {"w": 20, "h": 9},
    "refetchInterval": 900000,
    "staleTime": 300000,
    "mcp_tool": {"mcp_server": "Financial Data", "tool_id": "get_company_revenue_data"},
    "data": {
      "table": {
        "enableCharts": true,
        "columnsDefs": [
          {"field": "symbol", "headerName": "Symbol", "renderFn": "cellOnClick",
           "renderFnParams": {"actionType": "groupBy", "groupBy": {"paramName": "symbol"}}},
          {"field": "pct_change", "headerName": "% Change", "renderFn": "greenRed", "formatterFn": "percent"}
        ]
      }
    },
    "params": [
      {"paramName": "startDate", "type": "date", "value": "$currentDate-30d", "label": "Start Date"},
      {"paramName": "ticker",    "type": "text", "value": "AAPL",             "label": "Ticker"}
    ],
    "source": ["My API"]
  }
}
```

### [apps.json Reference](https://docs.openbb.co/workspace/developers/json-specs/apps-json-reference)

Served via `GET /apps.json` endpoint in your FastAPI app.

**Top-level fields**:
| Field | Description |
|---|---|
| `name` | App name |
| `description` | App description |
| `img` | Thumbnail URL or base64 (ideal: 250×200px) |
| `img_dark` / `img_light` | Optional dark/light mode thumbnails |
| `allowCustomization` | Boolean |
| `selected_agent` | Default AI agent ID |
| `authentication` | Auth requirements |
| `tabs` | Collection of tabs `{id, name, layout}` |
| `groups` | Synchronized parameter groups `{name, type, paramName, widgetIds, defaultValue}` |
| `prompts` | Array of suggested prompt strings for the AI agent |
| `mcp_servers` | Array of `{name, description, url}` — surfaces MCP server as available for the app |

**Tab layout** (each widget in layout):
- `i`: widget ID (endpoint `test/widget_1` → id `test_widget_1`)
- `x`, `y`, `w`, `h`: grid position + size
- `state`: widget state/params

**Group types**: `param` or `endpointParam` — syncs `paramName` across `widgetIds`.

**Example prompts**:
```json
"prompts": [
    "What is the latest CPI inflation momentum?",
    "Show me the year-over-year Core CPI.",
    "Plot the 2-year and 10-year Treasury yields."
]
```

**Endpoint setup**:
```python
@app.get("/apps.json")
async def get_apps():
    with open("apps.json", "r") as f:
        return JSONResponse(content=json.load(f))
```

---

## Agents — Workspace MCP
> https://docs.openbb.co/agents/workspace-mcp-overview

### Overview

The **Workspace MCP** is a local sidecar that exposes your live OpenBB Workspace browser session as MCP tools. External agents (Codex, Claude Code, Cursor, custom agents) can use it to:
- Inspect dashboards and widget state
- Fetch live widget data
- Create/update/delete widgets
- Manage tabs and navigation
- Register backends and instantiate apps

**Two directions of MCP in OpenBB**:
| Direction | Description |
|---|---|
| **Workspace MCP** | External agent → Workspace (Workspace = tool server) |
| **MCP tools in Copilot** | Workspace Copilot → external MCP servers |

**Architecture**:
```
MCP client/agent
    │ streamable HTTP MCP
    ▼
Workspace MCP sidecar (http://127.0.0.1:8787/mcp)
    │ WebSocket bridge
    ▼
OpenBB Workspace browser tab
    │ Workspace frontend state + backend calls
    ▼
Dashboards, widgets, apps, data backends, skills
```

### [Quickstart](https://docs.openbb.co/agents/workspace-mcp-quickstart)

**1. Start the sidecar**:
```bash
# macOS/Linux/WSL
curl -LsSf https://raw.githubusercontent.com/OpenBB-finance/workspace-mcp/main/scripts/run.sh | sh

# Windows PowerShell
powershell -ExecutionPolicy Bypass -Command "Invoke-RestMethod https://raw.githubusercontent.com/OpenBB-finance/workspace-mcp/main/scripts/run.ps1 | Invoke-Expression"
```
Default: `http://127.0.0.1:8787` | MCP endpoint: `http://127.0.0.1:8787/mcp`

**2. Check health**: `curl http://127.0.0.1:8787/health`

**3. Connect Workspace**: Hamburger menu → Workspace MCP Companion → set URL → Connect

**4. Configure MCP client**:
```json
// .mcp.json
{
  "mcpServers": {
    "workspace_mcp": {
      "type": "http",
      "url": "http://127.0.0.1:8787/mcp"
    }
  }
}
```
```bash
# Claude Code
claude mcp add --transport http workspace_mcp http://127.0.0.1:8787/mcp
# Codex
codex mcp add workspace_mcp --url http://127.0.0.1:8787/mcp
```

**5. Validate**: Ask agent to `Call get_workspace_snapshot and tell me the active dashboard id and visible tabs.`

**CORS**: by default allows `https://pro.openbb.co` and loopback. For custom origin:
```bash
workspace-mcp --cors-allow https://example.openbb.dev
```

### [Workspace MCP Tools](https://docs.openbb.co/agents/workspace-mcp-tools)

> **Rule**: Always start with `get_workspace_snapshot`. Use identifiers from the response — never invent UUIDs.

**Return shape**:
```json
{"ok": true, "command": "get_workspace_snapshot", "request_id": "cmd_...", "message": "ok", "data": {}, "error": null}
```

#### Discovery Tools
| Tool | Description |
|---|---|
| `get_workspace_snapshot` | Full current state: dashboards, layout, widgets, skills, tools |
| `list_available_widgets` | List widgets from a backend; filter by `origin` or `backend_id` |
| `get_widget_schema` | Exact creation contract for one widget (params, layout defaults) |
| `get_params_options` | Dynamic options for a widget parameter (when `requires_options_lookup: true`) |
| `get_skill_content` | Load a skill body by `slug` |

#### Data Tools
| Tool | Description |
|---|---|
| `get_widget_data` | Fetch live widget data; use `raw: true` in `data_args` for chart widgets to get rows |

#### Dashboard & Navigation Tools
| Tool | Description |
|---|---|
| `manage_dashboard` | Create/read/update dashboard (`operation: "create"/"read"/"update"`) |
| `navigate_workspace` | Navigate to dashboard or switch tab (`operation: "dashboard"/"tab"`) |
| `manage_navigation_bar` | Create/add_tabs/remove_tabs/rename_tabs |
| `update_widget_layout` | Move/resize widget on 40-column grid (`x, y, w, h`) |

Grid note: Navigation bar typically at `y: 0, h: 2`, so content starts at `y: 2`.
- Full width: `w: 40` | Half: `w: 20` | Quarter: `w: 10`

#### Widget Lifecycle Tools
| Tool | Description |
|---|---|
| `read_widget` | Read one widget's config/data by `widget_uuid` |
| `create_widget` | Create backend widget (call `list_available_widgets` + `get_widget_schema` first) |
| `update_widget` | Update widget params/config (not layout — use `update_widget_layout`) |
| `delete_widget` | Delete one widget |

#### Generated Artifact Tools
| Tool | Description |
|---|---|
| `add_generative_widget` | Create note/table/chart/HTML widget from inline data |

```json
// Note
{"widget_type": "note", "name": "Summary", "data": "# Summary\n\nKey findings..."}

// Chart
{"widget_type": "chart", "name": "Revenue", "data": [{"q": "Q1", "rev": 100}],
 "chart_params": {"chartType": "bar", "xKey": "q", "yKey": ["rev"]}}
```
`chart_params` keys are camelCase: `chartType`, `xKey`, `yKey`, `angleKey`, `calloutLabelKey`.

#### Backend & App Tools
| Tool | Description |
|---|---|
| `manage_backends` | List/add/update/refresh/remove backends |
| `manage_apps` | List/read/instantiate apps from a backend |

```json
// Add backend
{"operation": "add", "name": "My Backend", "url": "http://127.0.0.1:8000",
 "endpoint_headers": [{"key": "X-Auth-Token", "value": "token", "location": "headers"}]}

// Instantiate app
{"operation": "instantiate", "backend_id": "uuid", "app_name": "Macro Dashboard", "activate": true}
```

#### Agent Tools
| Tool | Description |
|---|---|
| `assign_tasks_to_agents` | Delegate tasks to configured Workspace agents |

#### Example Workflows

**Create dashboard with tabs and note**:
```
manage_dashboard    → {operation: "create", name: "My Dashboard", activate: true}
manage_navigation_bar → {operation: "create", tabs: [{name: "Overview"}, {name: "Charts"}]}
navigate_workspace  → {operation: "tab", tab_id: "overview"}
add_generative_widget → {widget_type: "note", data: "# Overview\n\nConnected!"}
```

**Add a backend widget**:
```
get_workspace_snapshot  → get current state
list_available_widgets  → {origin: "My Backend"}
get_widget_schema       → {origin: "My Backend", widget_id: "company_filings"}
create_widget           → {origin: "My Backend", widget_id: "company_filings", data_args: {symbol: "AAPL"}}
```

**Register backend + open app**:
```
manage_backends → {operation: "add", name: "Local Backend", url: "http://127.0.0.1:8000"}
manage_backends → {operation: "list"}
manage_apps     → {operation: "list", backend_id: "uuid"}
manage_apps     → {operation: "instantiate", backend_id: "uuid", template_id: "macro", activate: true}
```

**Read chart data as rows**:
```
get_widget_data → {origin: "Backend", widget_id: "chart", widget_uuid: "uuid", data_args: {symbol: "AAPL", raw: true}}
```

### [App Builder Resources](https://docs.openbb.co/agents/app-builder-resources)

Agent-facing resources for building OpenBB apps, available via Workspace MCP:

| Resource URI | Purpose |
|---|---|
| `openbb://workspace/app-builder/index` | **Start here** — routes to right resource |
| `openbb://workspace/guides/build-an-app` | Build a new app backend |
| `openbb://workspace/guides/debug-app` | Debug a broken app |
| `openbb://workspace/specs/widgets-json` | Edit widgets.json |
| `openbb://workspace/specs/apps-json` | Edit apps.json |
| `openbb://workspace/validation/common-errors` | Fix validation errors |
| `openbb://workspace/examples/python-fastapi/minimal` | Minimal FastAPI example |

**Install as skill** (for agents with skill support):
```bash
npx skills add https://github.com/OpenBB-finance/workspace-mcp --skill openbb-app-builder
```

### Trust & Security Model
- Treat any connected MCP client as **trusted** (can read state + mutate dashboards)
- Keep sidecar on `127.0.0.1` (loopback) — never expose on `0.0.0.0` or public network
- Operates within existing authenticated browser session
- Does not manage auth tokens, billing, org settings, or share dashboards

---

## Quick Reference — Widget Type Summary

| `type` value | Use case | Notes |
|---|---|---|
| `"table"` | Default AgGrid table | Most common |
| `"markdown"` | Text/notes/analysis | Returns markdown string |
| `"html"` | Custom styled HTML | No JS execution |
| `"metric"` | KPI tiles | Returns `{label, value, delta}` |
| `"chart"` | Plotly interactive charts | Returns `fig.to_json()` |
| `"chart-highcharts"` | Highcharts charts | `pip install highcharts-core` |
| `"chart-vegalite"` | Vega-Lite charts | Declarative JSON spec |
| `"newsfeed"` | News articles | Returns `[{title, date, author, excerpt, body}]` |
| `"live_grid"` | Real-time WebSocket table | Requires `wsEndpoint` |
| `"ssrm_table"` | Large dataset server-side table | Server-side pagination/filtering |
| `"omni"` | Dynamic text/table/chart via POST | Requires `prompt` param |
| `"youtube"` | Embedded YouTube player | Returns URL as PlainTextResponse |
| `"advanced_charting"` | TradingView OHLCV charts | UDF protocol required |
| `"pdf"` | PDF file viewer | Returns URL or base64 |

## Quick Reference — Parameter Types

| `type` | UI element | Notes |
|---|---|---|
| `"date"` | Date picker | Supports `$currentDate±N[h/d/w/M/y]` |
| `"text"` | Text input or dropdown | Add `options` for dropdown; `multiSelect` for multi; `multiple` for comma-separated |
| `"number"` | Number input | Numeric values |
| `"boolean"` | Toggle switch | `true`/`false` |
| `"endpoint"` | Dynamic dropdown | `optionsEndpoint` fetches options at runtime |
| `"ticker"` | Ticker symbol input | |
| `"form"` | Input form group | |
| `"tabs"` | Tab selector | |


