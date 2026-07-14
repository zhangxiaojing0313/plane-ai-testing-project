#!/usr/bin/env bash
set -euo pipefail

section() {
  printf '\n===== %s =====\n' "$1"
}

version_or_missing() {
  local label="$1"
  shift

  if command -v "$1" >/dev/null 2>&1; then
    printf '%s: ' "$label"
    "$@" 2>&1 | head -n 1
  else
    printf '%s: NOT INSTALLED\n' "$label"
  fi
}

section "Host identity"
printf 'Hostname: %s\n' "$(hostname)"
printf 'User: %s\n' "$(whoami)"
printf 'Working directory: %s\n' "$(pwd)"

section "Operating system"
if [[ -r /etc/os-release ]]; then
  grep -E '^PRETTY_NAME=' /etc/os-release || cat /etc/os-release
else
  uname -a
fi

section "CPU"
if command -v lscpu >/dev/null 2>&1; then
  lscpu
else
  awk -F': ' '/model name|Hardware|processor/ { print; found=1 } END { if (!found) print "CPU details unavailable" }' /proc/cpuinfo
fi

section "Memory"
if command -v free >/dev/null 2>&1; then
  free -h
else
  awk '/MemTotal|MemAvailable/ { print }' /proc/meminfo
fi

section "Disk"
df -hT "$(pwd)"

section "Tool versions"
version_or_missing "Docker" docker --version
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  printf 'Docker Compose: '
  docker compose version
elif command -v docker-compose >/dev/null 2>&1; then
  printf 'Docker Compose: '
  docker-compose --version
else
  printf 'Docker Compose: NOT INSTALLED\n'
fi
version_or_missing "Git" git --version
if command -v python3 >/dev/null 2>&1; then
  printf 'Python: '
  python3 --version
elif command -v python >/dev/null 2>&1; then
  printf 'Python: '
  python --version
else
  printf 'Python: NOT INSTALLED\n'
fi
version_or_missing "Node.js" node --version

section "Selected listening ports"
if command -v ss >/dev/null 2>&1; then
  for port in 8080 8081 8082 8443 3306 5432 6379 5672 9000 9001; do
    if ss -ltnH "sport = :$port" 2>/dev/null | grep -q .; then
      printf 'Port %s: LISTENING\n' "$port"
      ss -ltnH "sport = :$port" 2>/dev/null
    else
      printf 'Port %s: NOT LISTENING\n' "$port"
    fi
  done
else
  printf 'ss: NOT INSTALLED; selected ports were not checked\n'
fi

section "Safety note"
printf '%s\n' "This script intentionally does not print environment variables, passwords, tokens, cookies, API keys, or private configuration values."
