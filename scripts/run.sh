#!/usr/bin/env bash
# Development launcher. Uses the repo venv if present, otherwise python3.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=venv/bin/python
[[ -x "$PY" ]] || PY=python3
if [[ ! -f app.db ]]; then
  echo "[run.sh] No app.db found - seeding first (this also prints demo tokens)."
  "$PY" database/seed_data.py
fi
exec "$PY" app.py
