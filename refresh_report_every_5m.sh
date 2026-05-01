#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting report auto-generation loop (every 5 minutes)..."
while true; do
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Regenerating report..."
  OPEN_REPORT=0 CI=true python china_semiconductor_report.py || true
  sleep 300
done
