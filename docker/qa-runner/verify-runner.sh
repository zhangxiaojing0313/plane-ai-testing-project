#!/bin/bash
# verify-runner.sh — QA Runner environment verification
# Runs INSIDE the plane-qa-runner container (non-root).
set -euo pipefail

PASS=0
FAIL=0
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

check() {
    local label="$1"; shift
    if "$@" >/dev/null 2>&1; then
        echo -e "${GREEN}[PASS]${NC} $label"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}[FAIL]${NC} $label"
        FAIL=$((FAIL + 1))
    fi
}

echo "========================================="
echo " Plane QA Runner Verification"
echo " Hostname: $(hostname)"
echo " User:     $(whoami)"
echo " Date:     $(date -Is)"
echo "========================================="
echo ""

# ── Core tools ──────────────────────────────────────────
echo "--- Core Tools ---"
check "java -version"           java -version
check "git --version"           git --version
check "python3 --version"       python3 --version
check "pip --version"           pip --version
check "node --version"          node --version
check "npm --version"           npm --version
check "docker --version"        docker --version
check "curl available"          curl --version
check "bash available"          bash --version
check "rsync available"         rsync --version

# ── Python venv & packages ───────────────────────────────
echo ""
echo "--- Python QA Environment ---"
QA_VENV="${QA_VENV:-/home/jenkins/qa-venv}"
if [ -f "$QA_VENV/bin/python" ]; then
    check "qa-venv python"      "$QA_VENV/bin/python" --version
    check "pytest installed"    "$QA_VENV/bin/pip" show pytest
    check "requests installed"  "$QA_VENV/bin/pip" show requests
else
    echo -e "${RED}[FAIL]${NC} QA venv not found at $QA_VENV"
    FAIL=$((FAIL + 1))
fi

# ── Playwright ───────────────────────────────────────────
echo ""
echo "--- Playwright ---"
check "npx playwright --version"  npx playwright --version
check "chromium installed"        test -d "/home/jenkins/.cache/ms-playwright" -o \
                                  -d "/home/jenkins/.cache/ms-playwright*" -o \
                                  -d "/root/.cache/ms-playwright" -o \
                                  -d "/root/.cache/ms-playwright*"

# ── Network ──────────────────────────────────────────────
echo ""
echo "--- Network ---"
check "plane:8090 reachable"   curl -sI --max-time 10 http://host.docker.internal:8090
check "jenkins:8081 reachable" curl -sI --max-time 10 http://host.docker.internal:8081

# ── Docker access ────────────────────────────────────────
echo ""
echo "--- Docker ---"
DOCKER_OK=false
if docker ps --filter name=plane-app-plane-db-1 --format '{{.Names}}' 2>/dev/null | grep -q plane-app-plane-db-1; then
    echo -e "${GREEN}[PASS]${NC} docker can query plane-app-plane-db-1"
    PASS=$((PASS + 1))
    DOCKER_OK=true
else
    echo -e "${RED}[FAIL]${NC} docker cannot query plane-app-plane-db-1"
    FAIL=$((FAIL + 1))
fi

# ── Source access (read-only) ────────────────────────────
echo ""
echo "--- Project Source (read-only) ---"
if [ -d /opt/plane-source ]; then
    echo -e "${GREEN}[PASS]${NC} /opt/plane-source mounted"
    PASS=$((PASS + 1))
    echo "  Files: $(ls /opt/plane-source | head -10 | tr '\n' ' ')"
else
    echo -e "${RED}[FAIL]${NC} /opt/plane-source NOT mounted"
    FAIL=$((FAIL + 1))
fi

# ── Summary ──────────────────────────────────────────────
echo ""
echo "========================================="
echo " Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo "========================================="

exit $FAIL
