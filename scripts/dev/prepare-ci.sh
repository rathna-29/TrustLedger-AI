#!/usr/bin/env bash
# Reproducible test env for CI / fresh clones.
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements/base.txt
./venv/bin/python database/seed_data.py
