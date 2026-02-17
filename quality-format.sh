#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT_DIR"

MODE="write"
if [ "${1-}" = "--check" ]; then
  MODE="check"
elif [ "${1-}" != "" ]; then
  echo "Usage: $0 [--check]"
  exit 2
fi

FILES=$(find . -type f \
  -not -path "./.git/*" \
  -not -path "./.codex/*" \
  -not -path "./tests/.tmp/*" \
  \( -name "*.md" -o -name "*.sh" -o -name ".editorconfig" -o -name ".gitignore" \))

status=0
for file in $FILES; do
  if [ "$MODE" = "check" ]; then
    if perl -ne 'exit 1 if /[\t ]+$/;' "$file"; then
      :
    else
      echo "Needs formatting (trailing whitespace): $file"
      status=1
    fi

    if [ -s "$file" ] && [ "$(tail -c 1 "$file" | wc -l | tr -d ' ')" -eq 0 ]; then
      echo "Needs formatting (missing final newline): $file"
      status=1
    fi
  else
    perl -i -pe 's/[\t ]+$//' "$file"
    if [ -s "$file" ] && [ "$(tail -c 1 "$file" | wc -l | tr -d ' ')" -eq 0 ]; then
      printf '\n' >> "$file"
    fi
  fi
done

if [ "$MODE" = "check" ]; then
  [ "$status" -eq 0 ] && echo "[format] check passed"
  exit "$status"
fi

echo "[format] write passed"
