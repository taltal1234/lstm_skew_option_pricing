#!/usr/bin/env bash
# Runs the whole pipeline on synthetic data in the WRDS layout. Needs no WRDS login.
set -euo pipefail
cd "$(dirname "$0")/.."
export SMOKE_TEST=1
python tests/make_mock_data.py
python pipeline/02_build_dataset.py
python pipeline/03_train.py
python pipeline/04_evaluate.py
test -s results_mock/tables/walk/tables.md && echo "smoke test passed"
