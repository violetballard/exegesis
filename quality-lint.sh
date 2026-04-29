#!/usr/bin/env sh
set -eu

ROOT_DIR=${QUAL_ROOT_DIR:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)}
cd "$ROOT_DIR"

list_repo_files() {
  git ls-files -z --cached --others --exclude-standard | while IFS= read -r -d '' file; do
    case "$file" in
      .codex/*|.local_app_data/*|tests/.tmp/*)
        continue
        ;;
      *)
        printf '%s\0' "$file"
        ;;
    esac
  done
}

lint_shell_syntax() {
  file=$1
  first_line=$(sed -n '1p' "$file")
  case "$first_line" in
    '#!'*bash*)
      bash -n "$file"
      ;;
    *)
      sh -n "$file"
      ;;
  esac
}

echo "[lint] shell syntax"
tmp_files=$(mktemp)
trap 'rm -f "$tmp_files"' EXIT INT TERM
list_repo_files > "$tmp_files"

while IFS= read -r -d '' file; do
  case "$file" in
    *.sh) lint_shell_syntax "$file" ;;
  esac
done < "$tmp_files"

echo "[lint] trailing whitespace"
status=0
while IFS= read -r -d '' file; do
  case "$file" in
    *.md)
      continue
      ;;
  esac
  if perl -ne 'exit 1 if /[\t ]+$/;' "$file"; then
    :
  else
    echo "Trailing whitespace found in non-Markdown file: $file"
    status=1
  fi
done < "$tmp_files"

if [ "$status" -ne 0 ]; then
  exit "$status"
fi

echo "[lint] passed"
