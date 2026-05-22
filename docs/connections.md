# Connecting quant-openbb to OpenBB data providers

`quant-openbb` runs in one of two modes:

| Mode | Entry point | What loads |
| --- | --- | --- |
| **Standalone** (default) | `uvicorn openbb_quant.main:app` | Only the quant proxy router |
| **Full Platform** | `uvicorn openbb_core.api.rest_api:app` | Quant extension + all installed OpenBB providers |

Standalone mode only proxies the quant-api-gateway. To use OpenBB data providers
(polygon, yfinance, alpha_vantage, etc.) alongside the quant extension, run in
full-platform mode and configure provider credentials.

---

## 1. Full-platform mode (local)

### 1.1 Install the full OpenBB package

The default `pyproject.toml` depends on `openbb-core` only (the extension
framework). To add data providers, install the full `openbb` meta-package plus
any provider extensions you need:

```bash
uv add openbb
uv add openbb-yfinance        # example: Yahoo Finance provider
uv add openbb-polygon          # example: Polygon.io provider
```

After adding providers, rebuild static assets so the extension and providers are
discovered:

```bash
uv run openbb-build
```

### 1.2 Configure provider credentials

OpenBB looks for credentials in three places (checked in order):

1. **`~/.openbb_platform/.env`** — user-level, persisted across projects
2. **Environment variables** — `OPENBB_<PROVIDER>_API_KEY` etc.
3. **OpenBB Hub** — cloud-synced credentials at [my.openbb.co](https://my.openbb.co/app/platform)

**Option A — local `.env` file (recommended for dev)**

Create `~/.openbb_platform/.env`:

```bash
mkdir -p ~/.openbb_platform
cat > ~/.openbb_platform/.env << 'EOF'
# Data provider API keys
POLYGON_API_KEY=your_polygon_key_here

# OpenBB Hub credentials (optional, for synced preferences)
OPENBB_HUB_BACKEND=https://my.openbb.co
OPENBB_HUB_PAT=your_personal_access_token_here
EOF
```

**Option B — environment variables**

Export directly in your shell or in the service's `.env`:

```bash
export POLYGON_API_KEY=your_polygon_key_here
```

**Option C — OpenBB Hub (cloud credentials)**

1. Create an account at [my.openbb.co](https://my.openbb.co/app/platform)
2. Generate a Personal Access Token (PAT) in Settings
3. Set the PAT:

```bash
mkdir -p ~/.openbb_platform
echo 'OPENBB_HUB_PAT=your_pat_here' >> ~/.openbb_platform/.env
```

4. Log in via the CLI:

```bash
uv run openbb login
```

Provider API keys can then be entered through the Hub web UI and are synced
to your local machine automatically.

### 1.3 Start the full platform

```bash
uv run uvicorn openbb_core.api.rest_api:app --reload --port 8500
```

This starts the full OpenBB Platform with:
- **`/api/v2/engines/*`** — the quant proxy endpoints
- **`/api/v1/provider/*`** — OpenBB data provider endpoints (if providers installed)

Health check:

```bash
curl -sf http://localhost:8500/health                    # quant extension
curl -sf http://localhost:8500/api/v2/engines/catalog    # engine catalog
```

### 1.4 Verify a provider works

If you installed `openbb-yfinance`:

```bash
curl http://localhost:8500/api/v1/provider/yfinance/equity/price/historical \
  -G -d 'symbol=AAPL' -d 'start_date=2026-01-01'
```

---

## 2. Full-platform mode (Docker)

### 2.1 Extend the Dockerfile for providers

The default `Dockerfile` installs `openbb-core` only and runs `openbb-build`
(which will fail if the full `openbb` package is absent). To add providers,
extend the build:

```dockerfile
# Append to the builder stage (after the existing COPY + RUN)
# Install the full openbb package and provider extensions
RUN uv pip install openbb openbb-yfinance openbb-polygon --prefix /opt/venv
RUN openbb-build
```

Or, add the providers to `pyproject.toml` as dependencies so `uv sync` picks
them up automatically:

```bash
uv add openbb openbb-yfinance
```

Then rebuild the image:

```bash
docker compose build --no-cache
```

### 2.2 Mount credentials into the container

The OpenBB Platform reads `~/.openbb_platform/.env` at startup. Mount it as a
volume in `docker-compose.yml`:

```yaml
services:
  quant-openbb:
    # ... existing config ...
    volumes:
      - ${HOME}/.openbb_platform:/home/appuser/.openbb_platform:ro
```

Create the credentials file on the host first:

```bash
mkdir -p ~/.openbb_platform
cat > ~/.openbb_platform/.env << 'EOF'
POLYGON_API_KEY=your_key_here
EOF
```

### 2.3 Switch the CMD to the full platform

Override the command in `docker-compose.yml`:

```yaml
services:
  quant-openbb:
    # ... existing config ...
    command:
      - uvicorn
      - openbb_core.api.rest_api:app
      - --host
      - "0.0.0.0"
      - --port
      - "8000"
```

---

## 3. Running both modes simultaneously

You can run the standalone proxy on `:8500` and the full platform on another
port:

```bash
# Terminal 1 — standalone proxy (quant only)
uv run uvicorn openbb_quant.main:app --port 8500

# Terminal 2 — full platform (quant + providers)
uv run uvicorn openbb_core.api.rest_api:app --port 8501
```

Both share the same `QUANT_OPENBB_GATEWAY_BASE_URL` and `QUANT_OPENBB_INTERNAL_API_KEY`
settings.

---

## 4. Troubleshooting

**`openbb-build` fails with `ModuleNotFoundError: No module named 'openbb'`**

The full `openbb` package is not installed. Either install it (`uv add openbb`)
or, if you only need standalone mode, remove the `RUN openbb-build` line from
the Dockerfile.

**Extension not discovered in full-platform mode**

Run `openbb-build` after adding or removing provider packages. This rebuilds
the static asset registry so the platform knows about all extensions.

**401/403 from provider endpoints**

Provider credentials are missing or invalid. Verify:

```bash
ls -la ~/.openbb_platform/.env
grep -E 'API_KEY|HUB_PAT' ~/.openbb_platform/.env
```

**Container can't read `~/.openbb_platform/`**

Ensure the volume path exists on the host and the container user has read
permissions. The runtime image runs as `root` by default; if you add a
non-root user, adjust ownership accordingly.
