#!/usr/bin/env sh
set -eu

if [ ! -f README.md ]; then
  echo "README.md missing"
  exit 1
fi

for file in quality-lint.sh quality-format.sh quality-test.sh typecheck-test.sh; do
  [ -f "$file" ] || {
    echo "Missing required quality script: $file"
    exit 1
  }
  [ -x "$file" ] || {
    echo "Script is not executable: $file"
    exit 1
  }
done

echo "smoke passed"
