#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT_DIR"

echo "[lint] shell syntax"
find . -type f -name "*.sh" -not -path "./.git/*" -print | while IFS= read -r file; do
  sh -n "$file"
done

echo "[lint] trailing whitespace"
if command -v rg >/dev/null 2>&1; then
  if rg -n "[[:blank:]]+$" --glob "!*.md" --glob "!.git/**" --glob "!.codex/**" .; then
    echo "Trailing whitespace found in non-Markdown files."
    exit 1
  fi
else
  if grep -RInE "[[:blank:]]+$" . \
    --exclude="*.md" \
    --exclude-dir=".git" \
    --exclude-dir=".codex"; then
    echo "Trailing whitespace found in non-Markdown files."
    exit 1
  fi
fi

echo "[lint] passed"
