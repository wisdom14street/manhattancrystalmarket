#!/usr/bin/env bash
# Refresh products from namastebookshop.com and rebuild ./dist. Extra args go to build.py
# (e.g. --preview, --base=/manhattancrystalmarket, --site=https://...).
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/fetch.py
python3 scripts/build.py "$@"
