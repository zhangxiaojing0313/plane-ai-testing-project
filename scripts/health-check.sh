#!/usr/bin/env bash
set -euo pipefail

PLANE_BASE_URL="$(printenv PLANE_BASE_URL 2>/dev/null || true)"
base_url_source="PLANE_BASE_URL"
if [[ -z "$PLANE_BASE_URL" ]]; then
  PLANE_BASE_URL="http://127.0.0.1:8082"
  base_url_source="safe local default"
fi
PLANE_COMPOSE_PROJECT="$(printenv PLANE_COMPOSE_PROJECT 2>/dev/null || true)"
failed=0

section() {
  printf '\n===== %s =====\n' "$1"
}

section "HTTP health check"
printf 'Target URL source: %s\n' "$base_url_source"
if ! http_status="$(curl --silent --show-error --location --connect-timeout 5 --max-time 15 --output /dev/null --write-out '%{http_code}' "$PLANE_BASE_URL")"; then
  printf 'HTTP request failed\n'
  failed=1
else
  printf 'HTTP status: %s\n' "$http_status"
  case "$http_status" in
    2??|3??) printf 'HTTP result: PASS\n' ;;
    *) printf 'HTTP result: FAIL\n'; failed=1 ;;
  esac
fi

section "Docker container status"
if ! command -v docker >/dev/null 2>&1; then
  printf 'Docker command is unavailable\n'
  failed=1
else
  if ! all_containers="$(docker ps -a --format '{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Label "com.docker.compose.project"}}')"; then
    printf 'Unable to read Docker container status\n'
    failed=1
  else
    if [[ -n "$PLANE_COMPOSE_PROJECT" ]]; then
      scoped_containers="$(printf '%s\n' "$all_containers" | awk -F '\t' -v project="$PLANE_COMPOSE_PROJECT" '$4 == project')"
    else
      scoped_containers="$(printf '%s\n' "$all_containers" | awk -F '\t' 'tolower($2 " " $4) ~ /plane/')"
    fi

    if [[ -z "$scoped_containers" ]]; then
      printf '%s\n' "No Plane-scope containers found. Set the non-sensitive PLANE_COMPOSE_PROJECT variable if the Compose project name does not include 'plane'."
      failed=1
    else
      printf 'ID\tNAME\tSTATUS\tCOMPOSE_PROJECT\n'
      printf '%s\n' "$scoped_containers"
      if printf '%s\n' "$scoped_containers" | awk -F '\t' 'tolower($3) ~ /(restarting|unhealthy)/ { found=1 } END { exit !found }'; then
        printf 'Container health: FAIL (restarting or unhealthy container detected)\n'
        failed=1
      else
        printf 'Container health: PASS (no restarting or unhealthy container detected)\n'
      fi
    fi
  fi
fi

section "Result"
if [[ "$failed" -ne 0 ]]; then
  printf '%s\n' "Health check failed. Review the output above; no sensitive environment values were printed."
  exit 1
fi

printf '%s\n' "Health check passed."
