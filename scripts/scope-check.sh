#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

branch="${SCOPE_BRANCH_OVERRIDE:-$(git rev-parse --abbrev-ref HEAD)}"
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

is_lane_owned_unit_test() {
  local f="$1"
  case "$branch" in
    codex/feat-commands*)
      case "$f" in tests/unit/test_commands*.py) return 0 ;; esac
      ;;
    codex/feat-context-storage*)
      case "$f" in tests/unit/test_context*.py|tests/unit/test_storage*.py|tests/unit/test_state*.py) return 0 ;; esac
      ;;
    codex/feat-retrieval-fts*)
      case "$f" in tests/unit/test_retrieval*.py|tests/unit/test_fts*.py) return 0 ;; esac
      ;;
    codex/feat-a2ui-contract*)
      case "$f" in tests/unit/test_a2ui*.py) return 0 ;; esac
      ;;
    codex/feat-engine-runs*)
      case "$f" in tests/unit/test_engine*.py|tests/unit/test_draft*.py|tests/unit/test_workflow*.py|tests/unit/test_patch*.py|tests/unit/test_audit*.py) return 0 ;; esac
      ;;
    codex/feat-ocr-import*)
      case "$f" in tests/unit/test_import*.py|tests/unit/test_ocr*.py) return 0 ;; esac
      ;;
    codex/feat-literature-import*)
      case "$f" in tests/unit/test_literature*.py) return 0 ;; esac
      ;;
    codex/feat-rag-index*)
      case "$f" in tests/unit/test_rag*.py) return 0 ;; esac
      ;;
    codex/feat-qual-coding*)
      case "$f" in tests/unit/test_coding*.py|tests/unit/test_project_folder*.py) return 0 ;; esac
      ;;
    codex/feat-editor-basics*)
      case "$f" in tests/unit/test_editor*.py) return 0 ;; esac
      ;;
    codex/feat-citations*)
      case "$f" in tests/unit/test_citation*.py) return 0 ;; esac
      ;;
    codex/feat-export*)
      case "$f" in tests/unit/test_export*.py) return 0 ;; esac
      ;;
    codex/feat-zotero-import*)
      case "$f" in tests/unit/test_zotero*.py) return 0 ;; esac
      ;;
    codex/feat-formatting-bar*)
      case "$f" in tests/unit/test_format*.py) return 0 ;; esac
      ;;
    codex/feat-developer-provider-config*)
      case "$f" in tests/unit/test_provider*.py|tests/unit/test_credential*.py) return 0 ;; esac
      ;;
    codex/feat-project-transfer*)
      case "$f" in tests/unit/test_project_transfer*.py) return 0 ;; esac
      ;;
    codex/feat-cop-lite-licensing*)
      case "$f" in tests/unit/test_license*.py|tests/unit/test_lite*.py|tests/unit/test_nanonets_usage*.py) return 0 ;; esac
      ;;
  esac
  return 1
}

is_feature_branch() {
  case "$branch" in
    codex/feat-*) return 0 ;;
  esac
  return 1
}

is_main_equivalent_control_plane_sync() {
  local f="$1"
  is_feature_branch || return 1
  case "$f" in
    .codex/kickoff_packets/*|THREAD_OWNERSHIP.md|packet_garden/tools/planner.py|scripts/scope-check.sh)
      ;;
    *)
      return 1
      ;;
  esac
  git show-ref --verify --quiet refs/heads/main || return 1
  git cat-file -e "main:$f" 2>/dev/null || return 1
  git cat-file -e "HEAD:$f" 2>/dev/null || return 1
  git diff --quiet main HEAD -- "$f"
}

is_control_plane_file() {
  local f="$1"
  case "$f" in
    packet_garden/*|packet_garden/*/*)
      return 0
      ;;
    .agents/*|.agents/*/*)
      return 0
      ;;
    .codex/*|.codex/*/*)
      return 0
      ;;
    THREAD.md|THREAD_PACKET.md|THREAD_OWNERSHIP.md|INTEGRATION.md|AGENTS.md)
      return 0
      ;;
    scripts/scope-check.sh|scripts/common.sh)
      return 0
      ;;
    REMOTE_MONITORING_SPEC.md|docs/remote_monitoring/*|docs/remote_monitoring/*/*)
      return 0
      ;;
  esac
  return 1
}

is_allowed() {
  local f="$1"
  if is_feature_branch && is_control_plane_file "$f"; then
    return 1
  fi
  if shared_file_allowed && is_approved_shared_test "$f"; then
    return 0
  fi
  if is_lane_owned_unit_test "$f"; then
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
        engine/src/exegesis_engine/api/cli.py) return 0 ;;
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
        src/qual/retrieval/*|src/qual/retrieval/*/*|src/qual/engine/retrieval/*|src/qual/engine/retrieval/*/*|engine/src/exegesis_engine/retrieval/*|engine/src/exegesis_engine/retrieval/*/*|tests/unit/test_retrieval_sparse_promotion_provenance.py) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-a2ui-contract*)
      case "$f" in
        src/qual/ui/a2ui.py|src/qual/ui/test_a2ui_fallback_safety.py|shared/src/exegesis_shared/contracts/*|shared/src/exegesis_shared/contracts/*/*|shared/src/exegesis_shared/models/*|shared/src/exegesis_shared/models/*/*|shared/src/exegesis_shared/types/*|shared/src/exegesis_shared/types/*/*|tests/unit/test_a2ui_contract.py) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-engine-runs*)
      case "$f" in
        src/qual/engine/*|src/qual/engine/*/*|src/qual/drafting/*|src/qual/drafting/*/*|engine/src/exegesis_engine/api/*|engine/src/exegesis_engine/api/*/*|engine/src/exegesis_engine/workflow/*|engine/src/exegesis_engine/workflow/*/*|engine/src/exegesis_engine/patches/*|engine/src/exegesis_engine/patches/*/*|engine/src/exegesis_engine/audit/*|engine/src/exegesis_engine/audit/*/*|engine/src/exegesis_engine/services/*|engine/src/exegesis_engine/services/*/*|engine/src/exegesis_engine/state/models.py|tests/unit/test_bulk_draft_routing.py|tests/unit/test_engine_package_exports.py|tests/unit/test_engine_run_pipeline.py|tests/unit/test_policy_gate.py|tests/unit/test_retrieval_payload_basket.py) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-console-shell*)
      case "$f" in
        client-textual/*|client-textual/*/*) return 0 ;;
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
    codex/feat-developer-provider-config*)
      case "$f" in
        src/qual/providers/*|src/qual/providers/*/*|src/qual/credentials/*|src/qual/credentials/*/*|engine/src/exegesis_engine/providers/*|engine/src/exegesis_engine/providers/*/*|engine/src/exegesis_engine/credentials/*|engine/src/exegesis_engine/credentials/*/*|client-textual/src/exegesis_textual/providers/*|client-textual/src/exegesis_textual/providers/*/*|client-textual/src/exegesis_textual/commands/provider_config/*|client-textual/src/exegesis_textual/commands/provider_config/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-project-transfer*)
      case "$f" in
        engine/src/exegesis_engine/project_transfer/*|engine/src/exegesis_engine/project_transfer/*/*|shared/src/exegesis_shared/project_transfer/*|shared/src/exegesis_shared/project_transfer/*/*|client-textual/src/exegesis_textual/project_transfer/*|client-textual/src/exegesis_textual/project_transfer/*/*|desktop-shell/workstation/project_transfer/*|desktop-shell/workstation/project_transfer/*/*|docs/project_transfer/*|docs/project_transfer/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-desktop-packaging*)
      case "$f" in
        desktop-shell/*|desktop-shell/*/*|scripts/packaging/*|scripts/packaging/*/*|scripts/release/*|scripts/release/*/*|docs/packaging/*|docs/packaging/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-cop-lite-licensing*)
      case "$f" in
        engine/src/exegesis_engine/licensing/*|engine/src/exegesis_engine/licensing/*/*|engine/src/exegesis_engine/lite_gateway/*|engine/src/exegesis_engine/lite_gateway/*/*|engine/src/exegesis_engine/nanonets_usage/*|engine/src/exegesis_engine/nanonets_usage/*/*|client-textual/src/exegesis_textual/licensing/*|client-textual/src/exegesis_textual/licensing/*/*|client-textual/src/exegesis_textual/imports/*|client-textual/src/exegesis_textual/imports/*/*|shared/src/exegesis_shared/licensing/*|shared/src/exegesis_shared/licensing/*/*|shared/src/exegesis_shared/nanonets_usage/*|shared/src/exegesis_shared/nanonets_usage/*/*|docs/licensing/*|docs/licensing/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-browser-pdf-capture*)
      case "$f" in
        browser-extension/*|browser-extension/*/*|engine/src/exegesis_engine/browser_capture/*|engine/src/exegesis_engine/browser_capture/*/*|client-textual/src/exegesis_textual/browser_capture/*|client-textual/src/exegesis_textual/browser_capture/*/*|shared/src/exegesis_shared/browser_capture/*|shared/src/exegesis_shared/browser_capture/*/*|desktop-shell/browser_extension/*|desktop-shell/browser_extension/*/*|scripts/browser_extension/*|scripts/browser_extension/*/*|docs/browser_extension/*|docs/browser_extension/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-python-sidecar-api*)
      case "$f" in
        engine/src/exegesis_engine/sidecar/*|engine/src/exegesis_engine/sidecar/*/*|shared/src/exegesis_shared/sidecar/*|shared/src/exegesis_shared/sidecar/*/*|desktop-shell/sidecar/*|desktop-shell/sidecar/*/*|scripts/sidecar/*|scripts/sidecar/*/*|docs/sidecar/*|docs/sidecar/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-native-workstation*)
      case "$f" in
        desktop-shell/workstation/*|desktop-shell/workstation/*/*|desktop-shell/native/*|desktop-shell/native/*/*|desktop-shell/packaging/*|desktop-shell/packaging/*/*|scripts/workstation/*|scripts/workstation/*/*|scripts/packaging/*|scripts/packaging/*/*|scripts/release/*|scripts/release/*/*|docs/workstation/*|docs/workstation/*/*|docs/packaging/*|docs/packaging/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-open-access-deep-research*)
      case "$f" in
        engine/src/exegesis_engine/research/*|engine/src/exegesis_engine/research/*/*|engine/src/exegesis_engine/research_providers/*|engine/src/exegesis_engine/research_providers/*/*|engine/src/exegesis_engine/import_batches/*|engine/src/exegesis_engine/import_batches/*/*|desktop-shell/workstation/research/*|desktop-shell/workstation/research/*/*|desktop-shell/workstation/import_batches/*|desktop-shell/workstation/import_batches/*/*|shared/src/exegesis_shared/research/*|shared/src/exegesis_shared/research/*/*|docs/research/*|docs/research/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-quant-analysis*)
      case "$f" in
        desktop-shell/workstation/StatsCore/*|desktop-shell/workstation/StatsCore/*/*|desktop-shell/workstation/StatsBridge/*|desktop-shell/workstation/StatsBridge/*/*|desktop-shell/workstation/datasets/*|desktop-shell/workstation/datasets/*/*|desktop-shell/workstation/quant_analysis/*|desktop-shell/workstation/quant_analysis/*/*|shared/src/exegesis_shared/datasets/*|shared/src/exegesis_shared/datasets/*/*|shared/src/exegesis_shared/quant_analysis/*|shared/src/exegesis_shared/quant_analysis/*/*|docs/quant_analysis/*|docs/quant_analysis/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-advanced-qual-visuals*)
      case "$f" in
        engine/src/exegesis_engine/qual_visualizations/*|engine/src/exegesis_engine/qual_visualizations/*/*|engine/src/exegesis_engine/codebook/*|engine/src/exegesis_engine/codebook/*/*|desktop-shell/workstation/qual_visualizations/*|desktop-shell/workstation/qual_visualizations/*/*|shared/src/exegesis_shared/qual_visualizations/*|shared/src/exegesis_shared/qual_visualizations/*/*|docs/qual_visualizations/*|docs/qual_visualizations/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-confidential-collaboration*)
      case "$f" in
        engine/src/exegesis_engine/collaboration/*|engine/src/exegesis_engine/collaboration/*/*|engine/src/exegesis_engine/confidential_sync/*|engine/src/exegesis_engine/confidential_sync/*/*|desktop-shell/workstation/collaboration/*|desktop-shell/workstation/collaboration/*/*|shared/src/exegesis_shared/collaboration/*|shared/src/exegesis_shared/collaboration/*/*|shared/src/exegesis_shared/confidential_sync/*|shared/src/exegesis_shared/confidential_sync/*/*|docs/collaboration/*|docs/collaboration/*/*) return 0 ;;
      esac
      return 1
      ;;
    codex/feat-ipad-native-lite*)
      case "$f" in
        client-ipad/lite/*|client-ipad/lite/*/*|client-ipad/shared/*|client-ipad/shared/*/*|shared/src/exegesis_shared/ipad_lite/*|shared/src/exegesis_shared/ipad_lite/*/*|docs/ipad_lite/*|docs/ipad_lite/*/*) return 0 ;;
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
  if is_main_equivalent_control_plane_sync "$file"; then
    continue
  fi
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
