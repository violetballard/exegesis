#!/usr/bin/env sh
set -eu

ROOT_DIR=${QUAL_ROOT_DIR:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)}
cd "$ROOT_DIR"
unset QUAL_ROOT_DIR

if [ ! -d tests ]; then
  echo "No tests directory found."
  exit 1
fi

set -- tests/*.sh
if [ "$1" != "tests/*.sh" ]; then
  for test_file in "$@"; do
    echo "[test] $test_file"
    sh "$test_file"
  done
elif find tests -type f -name 'test_*.py' -print -quit | grep -q .; then
  echo "[test] python unittest discovery"
  if find tests/unit -type f -name 'test_*.py' -print -quit 2>/dev/null | grep -q .; then
    python3 -m unittest discover -s tests/unit -p "test_*.py" -v
  else
    python3 -m unittest discover -s tests -p "test_*.py" -v
  fi
else
  echo "No test files found in tests/."
  exit 1
fi

echo "[test] passed"
