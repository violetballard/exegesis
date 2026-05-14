#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT_DIR"

for test_file in tests/unit/test_*.py; do
  test_module=${test_file#tests/unit/}
  test_module=${test_module%.py}
  echo "[test] tests.unit.$test_module"
  python3 -m unittest "tests.unit.$test_module" -q
done
