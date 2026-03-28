#!/usr/bin/env sh
set -eu

ROOT_DIR=${QUAL_ROOT_DIR:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)}
cd "$ROOT_DIR"

list_repo_files() {
  git ls-files -z --cached --others --exclude-standard | while IFS= read -r -d '' file; do
    case "$file" in
      .codex/*|tests/.tmp/*|.local_app_data/*)
        continue
        ;;
      *.md|*.sh|.editorconfig|.gitignore)
        printf '%s\0' "$file"
        ;;
    esac
  done
}

MODE="write"
if [ "${1-}" = "--check" ]; then
  MODE="check"
elif [ "${1-}" != "" ]; then
  echo "Usage: $0 [--check]"
  exit 2
fi

tmp_files=$(mktemp)
trap 'rm -f "$tmp_files"' EXIT INT TERM
list_repo_files > "$tmp_files"

if [ "$MODE" = "check" ]; then
  status=0
  while IFS= read -r -d '' file; do
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
  done < "$tmp_files"
  if [ "$status" -eq 0 ]; then
    echo "[format] check passed"
  fi
  exit "$status"
fi

while IFS= read -r -d '' file; do
  perl -i -pe 's/[\t ]+$//' "$file"
  if [ -s "$file" ] && [ "$(tail -c 1 "$file" | wc -l | tr -d ' ')" -eq 0 ]; then
    printf '\n' >> "$file"
  fi
done < "$tmp_files"

echo "[format] write passed"
