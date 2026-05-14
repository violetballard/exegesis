#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT_DIR"

if [ ! -d tests ]; then
  echo "No tests directory found."
  exit 1
fi

set -- tests/*.sh
if [ "$1" = "tests/*.sh" ]; then
  echo "No test files found in tests/."
  exit 1
fi

for test_file in "$@"; do
  echo "[test] $test_file"
  sh "$test_file"
done

echo "[test] passed"
