#!/usr/bin/env bash
# Rebuild the database from scratch (drops existing app.db) and print demo tokens.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=venv/bin/python
[[ -x "$PY" ]] || PY=python3
rm -f app.db
"$PY" database/seed_data.py
