#!/usr/bin/env bash
# End-to-end check: every Phase 3 dashboard-relevant endpoint is reachable
# through the OpenBB proxy and returns valid JSON.
#
# Usage:
#   OPENBB_BASE_URL=http://localhost:8500 STRATEGY_ID=csm-set \
#     scripts/verify_openbb_integration.sh
#
# Exit codes: 0 — all checks passed; 1 — one or more checks failed;
#             2 — required tool (curl or jq) missing.

set -euo pipefail

OPENBB_BASE="${OPENBB_BASE_URL:-http://localhost:8500}"
STRATEGY_ID="${STRATEGY_ID:-csm-set}"

if ! command -v curl >/dev/null 2>&1 || ! command -v jq >/dev/null 2>&1; then
    echo "verify_openbb_integration.sh requires curl and jq on PATH" >&2
    exit 2
fi

PASS=0
FAIL=0

ENDPOINTS=(
    "/health"
    "/api/v2/engines/catalog"
    "/api/v2/engines/portfolio/overall-performance"
    "/api/v2/engines/portfolio/snapshot"
    "/api/v2/engines/portfolio/strategies"
    "/api/v2/engines/backtest/strategies/${STRATEGY_ID}/report"
)

echo "Verifying ${OPENBB_BASE} (STRATEGY_ID=${STRATEGY_ID})"
echo "──────────────────────────────────────────────────────"

for path in "${ENDPOINTS[@]}"; do
    url="${OPENBB_BASE}${path}"
    body_file="$(mktemp)"
    # -s silent, -o body, -w status only; do not -f so we can read the body on 4xx/5xx
    status=$(curl -s -o "${body_file}" -w "%{http_code}" "${url}" || echo "000")
    if [[ "${status}" == "200" ]] && jq empty "${body_file}" >/dev/null 2>&1; then
        echo "✓ PASS: ${path} (HTTP ${status})"
        PASS=$((PASS + 1))
    else
        echo "✗ FAIL: ${path} (HTTP ${status})"
        head -c 200 "${body_file}" >&2 || true
        echo >&2
        FAIL=$((FAIL + 1))
    fi
    rm -f "${body_file}"
done

echo "──────────────────────────────────────────────────────"
echo "Passed: ${PASS} / Total: $((PASS + FAIL))"

if (( FAIL > 0 )); then
    exit 1
fi
