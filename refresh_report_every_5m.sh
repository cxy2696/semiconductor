#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

INTERVAL_SECONDS="${INTERVAL_SECONDS:-300}"
RUN_ONCE="${RUN_ONCE:-0}"

if [[ "${1:-}" == "--once" ]]; then
  RUN_ONCE="1"
fi

run_generation() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Regenerating report..."
  OPEN_REPORT="${OPEN_REPORT:-0}" CI="${CI:-true}" python china_semiconductor_report.py
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
