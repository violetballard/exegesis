## feat-commands Fixer Gate Evidence

- Reviewer packet: `fixer__feat-commands__20260514T020047Z.prompt.txt`
- Required fix 1: branch HEAD will advance with this evidence-only commit so planner/router can re-emit the handoff for live reviewer handling; offline fallback is not treated as approval.
- Required fix 2: failing gate output was not reproduced when re-run; all required gates passed on this worktree.

## Gate Results

- `make scope-check`: passed
- `./quality-format.sh --check`: passed
- `./quality-lint.sh`: passed
- `./quality-test.sh`: passed, 480 tests run, 1 skipped
- `./typecheck-test.sh`: passed
- `make ci`: passed, 480 tests run, 1 skipped

## 2026-05-15 Metadata Correction

- Reviewer packet: `fixer__feat-commands__20260515T160501Z.prompt.txt`
- Scope-check / ownership note: `feat-commands` owned path is `src/qual/commands/**`, not `src/qual/engine/**`.
- Approved shared-test exception remains explicit for `tests/unit/test_commands_catalog.py`.
- Implementation behavior unchanged; this reissues packet metadata only.

## 2026-05-15 Demo-Path Mapping Correction

- Reviewer packet: `fixer__feat-commands__20260515T190500Z.prompt.txt`

### Completed Tasks with Canonical Demo-Path Step Mapping

1. Add deterministic command catalog (`command_names()`, `command_cli_contract()`, canonical tuple preservation) — advances "open project/document" by providing the stable CLI surface the engine uses to resolve `bootstrap`/`open-project`/`open-document` tokens into canonical commands.
2. Add CLI compatibility exact-action routes (`_COMMAND_CLI_COMPATIBILITY_EXACT_ACTIONS`) — advances "open project/document" and "retrieve relevant material" by mapping legacy CLI tokens (`retrieve`, `search`, `basket-add`, etc.) to their canonical engine actions so the engine loop can dispatch reliably.
3. Add command handler delegation contracts (`_COMMAND_HANDLER_DELEGATIONS`) — advances "plan or revise" and "apply or reject a patch" by binding `diff-preview`/`revise`/`apply`/`reject` commands to their engine handlers so the engine loop can execute patch-review steps.
4. Add retrieval prerequisite validation (`_validate_cli_compatibility_exact_actions`) — advances "retrieve relevant material" and "promote/gather context into the basket" by enforcing that compatibility tokens only route to engine actions within their declared flow step, preventing cross-step drift.
5. Add focused regression tests in `tests/unit/test_commands_catalog.py` — advances all demo-path steps by catching catalog drift before it breaks any engine-loop command resolution.

### Scope-check / Ownership Note (Corrected)

- Lane: `feat-commands`
- Owned path: `src/qual/commands/**`
- Implementation files changed: `src/qual/commands/catalog.py`, `src/qual/commands/__init__.py`, `src/qual/commands/diff_preview.py`
- Approved shared-test exception: `tests/unit/test_commands_catalog.py`
- No files outside `src/qual/commands/**` were modified (excluding the approved test exception).

### Canonical Demo-Path Step Advanced

This work makes **"open project/document"** more real. The command-catalog drift guard removes a concrete blocker for that step because the engine's "open project/document" flow depends on the CLI surface resolving `bootstrap`, `open-project`, `open-document`, and `document-open` tokens to a single canonical command with a stable engine-action route. Without the catalog validation (`command_cli_contract()` against `command_names()`), legacy token aliases could silently diverge from the canonical names, causing the engine to fail to dispatch `ExegesisAppService.open_project`/`open_document`. The drift guard ensures the CLI entrypoint surface and the engine dispatch table stay in lockstep, so the first step of the canonical demo path executes reliably. Additionally, the exact-action routes for `retrieve`/`search`/`basket-add` tokens unblock the downstream "retrieve relevant material" and "promote/gather context into the basket" steps by guaranteeing those tokens resolve to their canonical `context-basket` command and the corresponding `ExegesisAppService.search_project`/`add_basket_item` engine actions.

## 2026-05-15 Reissued Packet (fixer__feat-commands__20260515T213255Z)

- Reviewer packet: `fixer__feat-commands__20260515T213255Z.prompt.txt`
- Verdict received: `CHANGES_REQUESTED`
- Required fix 1 (scope-check/ownership note): already corrected above — lane is `feat-commands`, owned path is `src/qual/commands/**`, approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- Required fix 2 (canonical demo-path step): already stated above — advances "open project/document" and downstream retrieval/patch-review steps.
- Required fix 3 (reissue metadata-only packet): this section serves as the reissued packet. No implementation change required.

### Corrected Scope-check / Ownership Note

- Lane: `feat-commands`
- Owned path: `src/qual/commands/**`
- Implementation files changed: `src/qual/commands/catalog.py`, `src/qual/commands/__init__.py`, `src/qual/commands/diff_preview.py`
- Approved shared-test exception: `tests/unit/test_commands_catalog.py`
- No files outside `src/qual/commands/**` were modified (excluding the approved test exception).

### Canonical Demo-Path Step Advanced

Stable CLI command contract for the engine-first path steps covered by `bootstrap`/project-open, `context-basket`/retrieval, and `diff-preview`/patch review. The catalog drift guard ensures the CLI surface and engine dispatch table remain in lockstep so the "open project/document" step executes reliably, with downstream retrieval and patch-review tokens resolving to their canonical engine actions.

## 2026-05-16 Corrected Packet Reissue Trigger

- Reviewer packet: `R__CHANGES__codex-feat-commands__d6b6d1fe0623c471bdf780fc9329916976d5f6e2__20260515T224949Z.md`
- Required fixes are packet metadata and packet-generation fixes; command implementation remains unchanged.
- The control plane now emits lane-specific ownership notes for `feat-commands` instead of the stale engine-owned path note.
- The lane metadata now includes canonical demo-path step labels for each completed task.
- This branch advances with an evidence-only handoff note so planner can re-emit the same implementation through corrected packet generation.

## 2026-05-16 Integrator Handback Recheck

- Reviewer packet: `R__CHANGES__codex-feat-commands__eec030e17958c1e3097974f7aa1cabaa3acfaaa1__20260516T195443Z.md`
- Approval packet: `R__APPROVED__codex-feat-commands__eec030e17958c1e3097974f7aa1cabaa3acfaaa1__20260516T193422Z.md`
- Required fix 1: reproduced the integration inputs by rerunning the lane gates on branch `codex/feat-commands` at `eec030e17958c1e3097974f7aa1cabaa3acfaaa1`; no local gate failure or merge conflict reproduced.
- Required fix 2: no command-code change was needed because the integration output reported a patch-empty integration with matching approved files and all post-merge checks passing.
- Required fix 3: this evidence-only commit advances branch HEAD so the control plane can emit a fresh feature packet for review without editing hidden `.codex` metadata from the fixer.

### Gate Results

- `make scope-check`: passed
- `./quality-format.sh --check`: passed
- `./quality-lint.sh`: passed
- `./quality-test.sh`: passed, 491 tests run, 1 skipped
- `./typecheck-test.sh`: passed
- `make ci`: passed, 491 tests run, 1 skipped

### Canonical Demo-Path Step Advanced

Stable CLI control surface for the canonical engine loop. This recheck preserves the command contract that supports open project/document, retrieve relevant material, gather context into the basket, preview/apply or reject a patch, and persist handoff state without changing runtime behavior.

## 2026-05-16 Duplicate Integration Handback Recheck

- Reviewer packet: `fixer__feat-commands__20260516T201232Z.prompt.txt`
- Approval packet: `R__APPROVED__codex-feat-commands__22e55cb83dea914cbc897acadb749163bc0b502a__20260516T200613Z.md`
- Required fix 1: reproduced the reported integration condition from the captured output. The integrator reported no merge commit because the reviewed implementation slice from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` was already byte-equivalent on `main`, while the full lane branch still contains broad stale history outside the reviewed command slice.
- Required fix 2: no command implementation failure, merge conflict, or failing gate was present to fix. `make scope-check` passed locally on `codex/feat-commands`, matching the integrator output that post-merge checks passed on `main`.
- Required fix 3: this evidence-only commit advances branch HEAD again so the control plane can emit a fresh feature packet without requiring hidden `.codex` metadata edits from the sandboxed fixer.

### Gate Results

- `make scope-check`: passed
- `./quality-format.sh --check`: passed
- `./quality-lint.sh`: passed
- `./quality-test.sh`: passed, 491 tests run, 1 skipped
- `./typecheck-test.sh`: passed
- `make ci`: passed, 491 tests run, 1 skipped

### Canonical Demo-Path Step Advanced

Stable CLI control surface for the canonical engine loop. This recheck preserves the command contract that supports open project/document, retrieve relevant material, gather context into the basket, preview/apply or reject a patch, and persist handoff state without changing runtime behavior.

## 2026-05-16 Integrator Handback Recheck II

- Reviewer packet: `fixer__feat-commands__20260516T200416Z.prompt.txt`
- Approval packet: `R__APPROVED__codex-feat-commands__f2cd1e85ce66417ef89594731cabb64d49a23168__20260516T195738Z.md`
- Required fix 1: reproduced the reported integration condition from the captured output. The integrator did not report a command-code failure, merge conflict, or failing gate; it reported a blocked/no-op integration because the approved two-file implementation was already patch-equivalent on `main` as `eda0197b8 merge: consume approved feat-commands f8d860ed`.
- Required fix 2: no runtime command-code change was needed. The lane worktree re-ran the integration gates cleanly, confirming the blocker is the empty already-integrated cherry-pick state rather than a failing command implementation.
- Required fix 3: this evidence-only commit advances branch HEAD so the control plane can emit a fresh feature packet for review without editing hidden `.codex` metadata from the fixer.

### Gate Results

- `make scope-check`: passed
- `./quality-format.sh --check`: passed
- `./quality-lint.sh`: passed
- `./quality-test.sh`: passed, 491 tests run, 1 skipped
- `./typecheck-test.sh`: passed
- `make ci`: passed, 491 tests run, 1 skipped

### Canonical Demo-Path Step Advanced

Stable CLI control surface for the canonical engine loop. This recheck preserves the command contract that supports open project/document, retrieve relevant material, gather context into the basket, preview/apply or reject a patch, and persist handoff state without changing runtime behavior.
