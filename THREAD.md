# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Implementation review target: branch tip after fixer prompt `20260429T035831Z`
- Prior implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Scope: command-catalog contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: Milestone 3 CLI compatibility for the engine-first workflow loop, and `feat-commands` as the command-surface compatibility lane.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface.

## Reviewed Implementation Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Baseline Restoration

- `scripts/scope-check.sh` is restored to the submitted baseline and is not part of the branch-tip implementation diff.

## Metadata-Only Handoff Files

- `THREAD.md`
- `THREAD_PACKET.md`

## Branch-Tip Review Basis

- Review range: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`
- Matching changed-file scope:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/catalog.py`.
- Shared-by-approval implementation/test edits: `tests/unit/test_commands_catalog.py` under the approved shared-test exception.
- Integrator-locked edits: none.
- Metadata-only handoff edits: `THREAD.md`, `THREAD_PACKET.md`.

## Fixer Prompt `20260429T035831Z` Fix Satisfaction

1. `command_cli_contract()` validates the exact accepted parser-token surface, grouped canonical surface, lookup table, and canonical command order.
2. Regression coverage includes removed tokens, added same-canonical aliases, replacement aliases, lookup-table substitutions, and declared-surface drift.
3. `THREAD_PACKET.md` is regenerated with explicit canonical demo-path mapping for each completed task.
4. The demo-path step made more real is stated explicitly in `THREAD_PACKET.md`.
5. Required gates are rerun and recorded in `THREAD_PACKET.md`.
