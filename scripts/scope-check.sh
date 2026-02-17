#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

branch="$(git rev-parse --abbrev-ref HEAD)"
allow_shared="${SCOPE_ALLOW_SHARED:-0}"

# Use merge-base against main so checks are stable across rebases.
if git show-ref --verify --quiet refs/heads/main; then
  base_ref="main"
else
  base_ref="$(git rev-list --max-parents=0 HEAD | tail -n 1)"
fi

merge_base="$(git merge-base HEAD "$base_ref")"

changed_files="$(
  {
    git diff --name-only --diff-filter=ACMR "${merge_base}..HEAD"
    git diff --name-only --diff-filter=ACMR
    git diff --name-only --cached --diff-filter=ACMR
  } | awk 'NF' | sort -u
)"

if [[ -z "$changed_files" ]]; then
  log "scope-check: no changed files"
  exit 0
fi

shared_file_allowed() {
  [[ "$allow_shared" == "1" ]]
}

is_allowed() {
  local f="$1"
  case "$branch" in
    codex/integrator|main)
      return 0
      ;;
    codex/feat-commands*)
      case "$f" in
        src/qual/commands/*|src/qual/commands/*/*) return 0 ;;
        src/qual/cli.py) shared_file_allowed && return 0 ;;
      esac
      return 1
      ;;
    codex/feat-context-storage*)
      case "$f" in
        src/qual/context/*|src/qual/context/*/*|src/qual/storage/*|src/qual/storage/*/*) return 0 ;;
        src/qual/config.py) shared_file_allowed && return 0 ;;
      esac
      return 1
      ;;
    codex/feat-ux-flow*)
      case "$f" in
        src/qual/ui/*|src/qual/ui/*/*|src/qual/drafting/*|src/qual/drafting/*/*|src/qual/engine/*|src/qual/engine/*/*) return 0 ;;
        src/qual/app.py) shared_file_allowed && return 0 ;;
      esac
      return 1
      ;;
    *)
      log "scope-check: no policy for branch '$branch'; skipping"
      return 0
      ;;
  esac
}

violations=()
while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  if ! is_allowed "$file"; then
    violations+=("$file")
  fi
done <<< "$changed_files"

if (( ${#violations[@]} > 0 )); then
  log "scope-check: disallowed file changes on branch '$branch':"
  for file in "${violations[@]}"; do
    printf ' - %s\n' "$file"
  done
  log "Use integrator approval and rerun with SCOPE_ALLOW_SHARED=1 if this is intentional."
  exit 1
fi

log "scope-check: passed for branch '$branch'"
