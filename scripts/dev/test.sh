#!/usr/bin/env bash
# Run the full unittest suite (no external test deps required).
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=venv/bin/python
[[ -x "$PY" ]] || PY=python3
exec "$PY" -m unittest discover -s tests -v
