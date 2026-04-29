# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Corrected review target: the full current `codex/feat-commands` branch tip containing this packet refresh commit.
- Rejected review target reconciled by this packet: `e76d7de06e11109e40237b8b447110043cbe7621` and its predecessor `0fb860a1c160321585d711911bfce0c2f2242d07`.
- Merge base used for file accounting: `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- Risk classification: high-risk, because the branch tip includes `src/qual/cli.py`, which `THREAD_OWNERSHIP.md` marks as shared-by-approval and integrator-locked.
- Explicit approval/accounting note: `src/qual/cli.py` remains in scope only for the reviewer-required parser/catalog contract fix. It does not change model routing or provider configuration. Integrator approval is required before merge.

## Required Handoff Fields

- Branch name: `codex/feat-commands`
- Scope completed: command catalog metadata now has deterministic command identity, flow/demo metadata, an MVP command smoke plan, a live argparse parser-surface contract, and regression coverage for parser/catalog drift. The review target is the full branch tip, not a narrowed command-catalog-only commit.
- Roadmap item(s) affected: `Milestone 1: Bootstrap Flow Stabilization`, `Milestone 2: Test Hardening`, and the active MVP `feat-commands` lane.
- Vision capability affected: `Operator-first control surface`, because CLI command discovery and parsing stay reliable, and `Retrieval-first context handling`, because retrieval and context-basket CLI fallback surfaces stay deterministic.
- Routing/provider impact note: no model routing, provider configuration, or provider selection behavior touched.
- Proposed README.md patch text: none.

## High-Risk Budget Accounting

- Task budget: `4`.
- Time budget: `30m` for the required-fix packet refresh.
- Size limit for this required-fix commit: metadata-only changes to `THREAD.md` and `THREAD_PACKET.md`.
- Risk reason: `src/qual/cli.py` is shared-by-approval/integrator-locked and remains part of the actual branch-tip implementation diff.
- Early review trigger status: triggered by `src/qual/cli.py`; this packet explicitly routes that file to reviewer/integrator approval instead of narrowing the review basis.

## Tasks Completed

1. Branch-truthful review basis: regenerated this handoff against the actual branch tip instead of asking review to ignore implementation/test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Shared-file accounting: classified the work as high-risk and explicitly retained `src/qual/cli.py` as shared-by-approval/integrator-locked implementation scope.
3. Implementation/test ledger: included the post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation/test commits that affect `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
4. Demo-path and gate traceability: mapped each numbered task to canonical demo-path steps and reran the required gates against the corrected final tree.

## Canonical Demo-Path Mapping

Canonical sequence: `open document`, `retrieve relevant material`, `gather context into basket`, `plan/revise`, `apply/reject patch`, `persist state`, `continue working`.

1. Branch-truthful review basis advances `plan/revise` by giving reviewer/integrator a complete, accurate implementation basis for the command-lane plan.
2. Shared-file accounting advances `continue working` by making the CLI fallback risk explicit before merge instead of hiding an integrator-locked parser change.
3. Implementation/test ledger advances `retrieve relevant material` and `gather context into basket` by keeping retrieval and `context-basket` command parsing/catalog metadata tied to the live parser surface.
4. Demo-path and gate traceability advances `open document`, `apply/reject patch`, and `persist state` by documenting the exported MVP smoke argv for `bootstrap`, `diff-preview`, and terminal handoff flows.

Final demo-path statement: this branch makes `retrieve relevant material` and `gather context into basket` more real by preventing parser/catalog drift for retrieval and `context-basket` CLI fallback commands; it also makes `open document`, `apply/reject patch`, and `persist state` more concrete through catalog-owned MVP smoke argv.

## Implementation Ledger

- `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`: command catalog parser-contract implementation and tests in `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- `3f180d67ca82eebdce9da411fc2da5356064d46f`: implementation fixer that keeps `src/qual/cli.py` in scope, builds top-level parser choices from catalog tokens, updates `src/qual/commands/catalog.py`, and expands `tests/unit/test_commands_catalog.py`.
- `c320dafa67733469fac8c60aa1ec3b54d2ef6c97`: implementation commit exporting MVP command smoke-plan APIs through `src/qual/commands/__init__.py` and `src/qual/commands/catalog.py`.
- `153c1271575ee1ea4256378f560c255254fef2c6a`: test plus packet correction commit; modifies `tests/unit/test_commands_catalog.py`, `THREAD.md`, and `THREAD_PACKET.md`.
- `2aef59c6d4fe888a238bd0b696adf6b4cd720382`: parser-drift test plus packet correction commit; modifies `tests/unit/test_commands_catalog.py`, `THREAD.md`, and `THREAD_PACKET.md`.
- `0fb860a1c160321585d711911bfce0c2f2242d07`: packet refresh commit rejected by reviewer packet `20260429T184651Z`; superseded by this branch-truthful required-fix packet.
- This required-fix commit: metadata-only packet refresh in `THREAD.md` and `THREAD_PACKET.md`; no implementation/test files are excluded from the review target.

## Complete Branch-Tip File List

Actual merge diff from `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27` to the full branch tip containing this packet refresh commit:

- `THREAD.md`
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/cli.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

## Ownership And Scope

- Lane-owned files: `src/qual/commands/**`.
- Lane-owned files changed: `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, and `src/qual/commands/diff_preview.py`.
- Shared-by-approval/integrator-locked implementation file changed: `src/qual/cli.py`.
- Shared/integrator-locked edits: YES. Explicit integrator approval is required for `src/qual/cli.py`.
- Shared tests changed: `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`, retained as regression coverage for the command catalog and diff-preview contracts.
- Integrator-owned files changed: none.
- Routing/provider impact: none.

## Commands Run

- `make scope-check`: PASS on the exact full-branch-tip tree submitted for review.
- `./quality-format.sh --check`: PASS on the exact full-branch-tip tree submitted for review.
- `./quality-lint.sh`: PASS on the exact full-branch-tip tree submitted for review.
- `./quality-test.sh`: PASS on the exact full-branch-tip tree submitted for review.
- `./typecheck-test.sh`: PASS on the exact full-branch-tip tree submitted for review.
- `make ci`: PASS on the exact full-branch-tip tree submitted for review.

## Risks And Blockers

- Risk: `src/qual/cli.py` is shared-by-approval/integrator-locked. The edit is intentionally retained in scope for the parser/catalog contract fix and requires integrator approval.
- Residual risk: branch history is long, but the complete branch-tip file list above is the review basis for the actual merge diff.
- Blockers: none after required gates pass, except the explicit integrator approval needed for `src/qual/cli.py`.

## Final Readiness Statement

This packet no longer asks review to treat post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` code/test changes as metadata-only. It includes the real branch-tip implementation/test scope, accounts for `src/qual/cli.py` as shared-by-approval and integrator-locked work, maps each numbered task to the canonical demo path, and ties gate results to the corrected final review tree.
