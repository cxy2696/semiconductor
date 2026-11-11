#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -x ".venv/bin/python" ]]; then PYTHON_BIN=".venv/bin/python"; fi
"$PYTHON_BIN" -m semcore serve --port "${PORT:-8000}"
