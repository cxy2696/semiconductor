#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$REPO_ROOT"

INTERVAL_SECONDS="${INTERVAL_SECONDS:-3600}"
RUN_ONCE="${RUN_ONCE:-0}"
REFRESH_RETRIES="${REFRESH_RETRIES:-1}"
if [[ -z "${PYTHON_BIN:-}" ]]; then
  if [[ -x "${REPO_ROOT}/.venv/bin/python" ]]; then
    PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
  else
    PYTHON_BIN="python3"
  fi
fi

if [[ "${1:-}" == "--once" ]]; then
  RUN_ONCE="1"
fi

run_generation_once() {
  OPEN_REPORT="${OPEN_REPORT:-0}" CI="${CI:-true}" "${PYTHON_BIN}" scripts/build_dashboard.py
}

run_generation() {
  local attempt=0
  local max_attempts=$((REFRESH_RETRIES + 1))
  while (( attempt < max_attempts )); do
    attempt=$((attempt + 1))
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Regenerating report (attempt ${attempt}/${max_attempts})..."
    if run_generation_once; then
      return 0
    fi
    if (( attempt < max_attempts )); then
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] Attempt ${attempt} failed. Retrying in 20s..."
      sleep 20
    fi
  done
  return 1
}

if [[ "$RUN_ONCE" == "1" ]]; then
  echo "Running single refresh cycle..."
  run_generation
  echo "Single refresh cycle completed."
  exit 0
fi

echo "Starting report auto-generation loop (every ${INTERVAL_SECONDS} seconds)..."
while true; do
  if ! run_generation; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Refresh failed. Will retry after sleep."
  fi
  sleep "${INTERVAL_SECONDS}"
done
