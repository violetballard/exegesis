# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: final branch tip after the `2026-04-28T21:42:51Z` fixer pass; implementation, tests, and packet metadata are reviewed together.
- Scope: CLI command-catalog contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: Milestone 3 CLI compatibility for the engine-first workflow loop, and `feat-commands` as the command-surface compatibility lane.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface.

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`

## Shared / Approval Notes

- Shared-by-approval test edit: yes, `tests/unit/test_commands_catalog.py`, covered by the approved shared-test exception.
- Integrator-locked edits: no.
- Reviewed implementation file `src/qual/commands/catalog.py` is lane-owned under `src/qual/commands/**`.

## Implementation Basis

- Final branch tip after this `2026-04-28T21:42:51Z` fixer pass is the review basis.
- Previous stale review basis `8fdcfceb079925f646eebff014211105eb0ccf5e` was the pre-fix tip; the new fixer commit supersedes it for re-review.
- Code-bearing command-catalog/test commits are part of the implementation basis and are not classified as metadata-only.
- Metadata-only commits are limited to `THREAD.md` and `THREAD_PACKET.md` packet maintenance.

## Canonical Demo-Path Mapping

- Task 1 advances `continue working`: parser/catalog validation prevents follow-up CLI turns from continuing through a silently drifted command contract.
- Task 2 advances `continue working`: canonical command ordering stays deterministic across operator turns and command smoke checks.
- Task 3 advances `continue working`: regression tests lock accepted-token, declared-surface, lookup-table, and alias-level parser drift before handoff.
- Task 4 advances `continue working`: refreshed handoff metadata gives reviewer/integrator the exact branch-tip review basis.
- Final demo-path statement: this handoff makes `continue working` more real by keeping the CLI command contract deterministic while Textual remains disabled.

## Blocker Removed

Parser/catalog drift validation is needed now because the CLI is the active operator surface for the engine-side MVP loop. Without a fail-fast contract check, open/retrieve/basket/revise/patch/save follow-up turns could continue through a parser surface that no longer matches the canonical command catalog.

## Required Fix Satisfaction

1. Reviewer fix 1, regenerate packet against actual branch tip: final branch tip is the review basis, and code-bearing catalog/test commits are not called metadata-only.
2. Reviewer fix 2, full parser-surface validation: `command_cli_contract()` checks grouped parser projection, accepted token tuple, lookup table shape/order, and canonical names against the declared command-catalog projection.
3. Reviewer fix 3, drift regression tests: coverage includes extra accepted alias, removed accepted alias, substituted alias, parser-token reorder preserving canonical names, declared-surface alias drift, grouped token-to-canonical drift, lookup-table token-substitution drift, and lookup-table shape/order drift.
4. Reviewer fix 4, canonical demo-path mapping: every completed task maps to `continue working`, and this packet states that the CLI command contract makes that step more real while Textual remains disabled.
5. Reviewer fix 5, complete metadata-only accounting: packet refresh metadata files are `THREAD.md` and `THREAD_PACKET.md`; `tests/unit/test_commands_catalog.py` remains the approved shared-by-approval test edit, and there are no integrator-locked edits.

## Reviewer Packet `20260428T213854Z` Fix Satisfaction

1. Exact canonical demo-path step: this handoff advances `continue working`.
2. Concrete blocker removed: the fail-fast `command_cli_contract()` check prevents CLI follow-up turns for open/retrieve/basket/revise/patch/save from running against a parser surface that has drifted away from the canonical catalog.
3. Complete metadata-only file list: `THREAD.md` and `THREAD_PACKET.md`.
4. Implementation scope: unchanged; this pass updates handoff metadata only because the current implementation already validates full parser-surface drift and includes the required alias-drift regressions.

## Reviewer Packet `20260428T214128Z` Fix Satisfaction

1. Independent parser-surface projection: `command_cli_contract()` compares grouped parser projection, accepted tokens, lookup-table shape/order, and canonical names against `_CLI_COMMAND_SURFACE`.
2. Parser-surface drift tests: coverage includes removed accepted alias, added accepted alias, substituted alias, token reorder, lookup-table token substitution, and lookup-table shape/order drift while canonical names can remain stable.
3. Canonical demo-path mapping: every completed task maps to `continue working`, with the blocker removed stated above.
4. Ownership accounting: implementation changed `src/qual/commands/catalog.py`, tests used the approved shared-by-approval exception for `tests/unit/test_commands_catalog.py`, and no integrator-locked files were edited.

## Final Verification

- Required gates passed on branch `codex/feat-commands` at `2026-04-28T21:35:44Z`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- Required gates passed again on branch `codex/feat-commands` at `2026-04-28T21:40:36Z`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- Required gates passed again on branch `codex/feat-commands` at `2026-04-28T21:44:02Z`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
