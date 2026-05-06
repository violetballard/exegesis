#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

branch="$(git rev-parse --abbrev-ref HEAD)"
allow_shared="${SCOPE_ALLOW_SHARED:-0}"
include_worktree="${SCOPE_INCLUDE_WORKTREE:-0}"
ignore_lane_noise="${SCOPE_IGNORE_LANE_NOISE:-1}"
scope_window="${SCOPE_WINDOW:-auto}"

if [[ "$scope_window" == "auto" ]]; then
  case "$branch" in
    codex/feat-*)
      scope_window="recent"
      ;;
    *)
      scope_window="full"
      ;;
  esac
fi

if [[ "$scope_window" == "recent" ]]; then
  changed_files="$(git show --name-only --pretty=format: --diff-filter=ACMR HEAD | awk 'NF' | sort -u)"
else
  # Use merge-base against integrator when available, otherwise main.
  if git show-ref --verify --quiet refs/heads/codex/integrator; then
    base_ref="codex/integrator"
  elif git show-ref --verify --quiet refs/heads/main; then
    base_ref="main"
  else
    base_ref="$(git rev-list --max-parents=0 HEAD | tail -n 1)"
  fi

  merge_base="$(git merge-base HEAD "$base_ref")"
  changed_files="$(git diff --name-only --diff-filter=ACMR "${merge_base}..HEAD" | awk 'NF' | sort -u)"
fi

# Optional: include staged/unstaged edits for stricter local preflight checks.
if [[ "$include_worktree" == "1" ]]; then
  changed_files="$(
    {
      printf '%s\n' "$changed_files"
      git diff --name-only --diff-filter=ACMR
      git diff --name-only --cached --diff-filter=ACMR
    } | awk 'NF' | sort -u
  )"
fi

if [[ -z "$changed_files" ]]; then
  log "scope-check: no changed files"
  exit 0
fi

shared_file_allowed() {
  [[ "$allow_shared" == "1" ]]
}

is_approved_shared_test() {
  local f="$1"
  case "$branch" in
    codex/feat-commands*)
      case "$f" in
        tests/unit/test_commands_catalog.py|tests/unit/test_diff_preview.py) return 0 ;;
      esac
      ;;
    codex/feat-context-storage*)
      case "$f" in
        tests/unit/test_context_storage_recovery.py) return 0 ;;
      esac
      ;;
    codex/feat-retrieval-fts*)
      case "$f" in
        tests/unit/test_unified_retrieval.py) return 0 ;;
      esac
      ;;
  esac
  return 1
}

is_allowed() {
  local f="$1"
  if shared_file_allowed && is_approved_shared_test "$f"; then
    return 0
  fi
  if [[ "$ignore_lane_noise" == "1" ]]; then
    case "$f" in
      .codex/*|.agents/*|.git-*/**|.git-*/?|.git-box/*|.git-local/*|.git-real/*|.git-copy/*|.git-local-root/*|.git-worktree-local/*|.pycache_global/*|.git.box|.git.box-backup|.git.original_box|.git_alt_index|.git.orig|.git.remote)
        return 0
        ;;
      handoff/*|handoff.block/*|handoffs/*)
        return 0
        ;;
      THREAD.md|THREAD_PACKET.md|AGENTS.md|INTEGRATION.md)
        return 0
        ;;
      .gitignore|scripts/scope-check.sh|foo.txt|foo.lock|tmp_check.txt|tmpfile.md)
        return 0
        ;;
    esac
  fi
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
        src/qual/context/*|src/qual/context/*/*|src/qual/storage/*|src/qual/storage/*/*|engine/src/exegesis_engine/state/*|engine/src/exegesis_engine/state/*/*|engine/src/exegesis_engine/storage/*|engine/src/exegesis_engine/storage/*/*) return 0 ;;
        src/qual/config.py) shared_file_allowed && return 0 ;;
      esac
      return 1
      ;;
    codex/feat-retrieval-fts*)
      case "$f" in
        src/qual/retrieval/*|src/qual/retrieval/*/*|src/qual/engine/retrieval/*|src/qual/engine/retrieval/*/*|engine/src/exegesis_engine/retrieval/*|engine/src/exegesis_engine/retrieval/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-a2ui-contract*)
      case "$f" in
        src/qual/ui/a2ui.py|shared/src/exegesis_shared/contracts/*|shared/src/exegesis_shared/contracts/*/*|shared/src/exegesis_shared/models/*|shared/src/exegesis_shared/models/*/*|shared/src/exegesis_shared/types/*|shared/src/exegesis_shared/types/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-engine-runs*)
      case "$f" in
        src/qual/engine/*|src/qual/engine/*/*|src/qual/drafting/*|src/qual/drafting/*/*|engine/src/exegesis_engine/api/*|engine/src/exegesis_engine/api/*/*|engine/src/exegesis_engine/workflow/*|engine/src/exegesis_engine/workflow/*/*|engine/src/exegesis_engine/patches/*|engine/src/exegesis_engine/patches/*/*|engine/src/exegesis_engine/audit/*|engine/src/exegesis_engine/audit/*/*|engine/src/exegesis_engine/services/*|engine/src/exegesis_engine/services/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-console-shell*)
      case "$f" in
        client-textual/src/exegesis_textual/app/*|client-textual/src/exegesis_textual/app/*/*|client-textual/src/exegesis_textual/layout/*|client-textual/src/exegesis_textual/layout/*/*|client-textual/src/exegesis_textual/panes/*|client-textual/src/exegesis_textual/panes/*/*|client-textual/src/exegesis_textual/commands/*|client-textual/src/exegesis_textual/commands/*/*|client-textual/src/exegesis_textual/shortcuts/*|client-textual/src/exegesis_textual/shortcuts/*/*|client-textual/src/exegesis_textual/inspectors/*|client-textual/src/exegesis_textual/inspectors/*/*|client-textual/src/exegesis_textual/theme/*|client-textual/src/exegesis_textual/theme/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-console-workflow*)
      case "$f" in
        client-textual/src/exegesis_textual/workflow/*|client-textual/src/exegesis_textual/workflow/*/*|client-textual/src/exegesis_textual/cards/*|client-textual/src/exegesis_textual/cards/*/*|client-textual/src/exegesis_textual/events/*|client-textual/src/exegesis_textual/events/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-ocr-import*)
      case "$f" in
        src/qual/imports/*|src/qual/imports/*/*|src/qual/ocr/*|src/qual/ocr/*/*|engine/src/exegesis_engine/imports/*|engine/src/exegesis_engine/imports/*/*|engine/src/exegesis_engine/ocr/*|engine/src/exegesis_engine/ocr/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-literature-import*)
      case "$f" in
        src/qual/literature/*|src/qual/literature/*/*|engine/src/exegesis_engine/literature/*|engine/src/exegesis_engine/literature/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-rag-index*)
      case "$f" in
        src/qual/rag/*|src/qual/rag/*/*|engine/src/exegesis_engine/rag/*|engine/src/exegesis_engine/rag/*/*|engine/src/exegesis_engine/retrieval/rag/*|engine/src/exegesis_engine/retrieval/rag/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-qual-coding*)
      case "$f" in
        src/qual/coding/*|src/qual/coding/*/*|src/qual/project_folders/*|src/qual/project_folders/*/*|engine/src/exegesis_engine/coding/*|engine/src/exegesis_engine/coding/*/*|engine/src/exegesis_engine/project_folders/*|engine/src/exegesis_engine/project_folders/*/*|client-textual/src/exegesis_textual/coding/*|client-textual/src/exegesis_textual/coding/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-editor-basics*)
      case "$f" in
        src/qual/editor/*|src/qual/editor/*/*|engine/src/exegesis_engine/editor/*|engine/src/exegesis_engine/editor/*/*|client-textual/src/exegesis_textual/editor/*|client-textual/src/exegesis_textual/editor/*/*|client-textual/src/exegesis_textual/shortcuts/editor/*|client-textual/src/exegesis_textual/shortcuts/editor/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-citations*)
      case "$f" in
        src/qual/citations/*|src/qual/citations/*/*|engine/src/exegesis_engine/citations/*|engine/src/exegesis_engine/citations/*/*|shared/src/exegesis_shared/citations/*|shared/src/exegesis_shared/citations/*/*|client-textual/src/exegesis_textual/citations/*|client-textual/src/exegesis_textual/citations/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-export*)
      case "$f" in
        src/qual/export/*|src/qual/export/*/*|engine/src/exegesis_engine/export/*|engine/src/exegesis_engine/export/*/*|client-textual/src/exegesis_textual/export/*|client-textual/src/exegesis_textual/export/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-zotero-import*)
      case "$f" in
        src/qual/zotero/*|src/qual/zotero/*/*|engine/src/exegesis_engine/zotero/*|engine/src/exegesis_engine/zotero/*/*|client-textual/src/exegesis_textual/zotero/*|client-textual/src/exegesis_textual/zotero/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-formatting-bar*)
      case "$f" in
        src/qual/formatting/*|src/qual/formatting/*/*|engine/src/exegesis_engine/formatting/*|engine/src/exegesis_engine/formatting/*/*|client-textual/src/exegesis_textual/formatting/*|client-textual/src/exegesis_textual/formatting/*/*) return 0 ;;
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
