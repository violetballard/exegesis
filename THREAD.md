# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: final branch tip after this `2026-04-28T22:12:47Z` fixer pass for reviewer packet `20260428T220957Z`; implementation, tests, and packet metadata are reviewed together.
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

- Final branch tip after this `2026-04-28T22:12:47Z` fixer pass is the review basis.
- Previous stale review basis `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` was incomplete because later commits changed `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; the corrected branch-tip basis supersedes it for re-review.
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
3. Reviewer fix 3, drift regression tests: coverage includes extra accepted alias, removed accepted alias, substituted alias to another known alias with the same canonical command, parser-token reorder preserving canonical names, declared-surface alias drift, grouped token-to-canonical drift, lookup-table token-substitution drift, and lookup-table shape/order drift.
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

## Reviewer Packet `20260428T214706Z` Fix Satisfaction

1. Full parser-surface validation: `command_cli_contract()` compares the grouped parser projection, accepted token tuple, lookup-table shape/order, and canonical names against `_CLI_COMMAND_SURFACE`.
2. Parser-surface drift tests: coverage includes alias substitution with the same canonical target, removed accepted alias, added accepted alias, reordered parser tokens, and lookup-table shape/order drift.
3. Actual branch-tip packet: this packet presents the final branch tip after the `2026-04-28T21:47:57Z` fixer pass as the review basis and does not label code/test commits as metadata-only.
4. Canonical demo-path mapping: every completed task maps to `continue working`, with the concrete blocker removed stated above.
5. Ownership accounting: `tests/unit/test_commands_catalog.py` is listed as the approved shared-by-approval test edit, and integrator-locked edits are explicitly `no`.

## Reviewer Packet `20260428T214934Z` Fix Satisfaction

1. Declared parser-surface projection: `command_cli_contract()` validates grouped parser projection, accepted token tuple, lookup-table shape/order, and canonical names against `_CLI_COMMAND_SURFACE`.
2. Parser-surface drift tests: coverage mutates `_CLI_ENTRYPOINTS`, `_CLI_COMMAND_SURFACE`, and `command_cli_lookup_table()` for added alias, removed alias, substituted alias, token reorder, lookup-table token substitution, and lookup-table order drift while canonical names can remain unchanged.
3. Canonical demo-path mapping: every completed task maps to `continue working`, and this packet states that the handoff makes that step more real while Textual remains disabled.
4. Ownership accounting: implementation touched `src/qual/commands/catalog.py`, the approved shared-by-approval test path is `tests/unit/test_commands_catalog.py`, and no integrator-locked files were edited.

## Reviewer Packet `20260428T214935Z` Fix Satisfaction

1. Token-level parser-surface validation: already satisfied at branch tip by `command_cli_contract()` comparing grouped parser projection, accepted token tuple, lookup-table shape/order, and canonical names against `_CLI_COMMAND_SURFACE`.
2. Parser-surface drift tests: already satisfied at branch tip by focused regressions for added alias, removed alias, substituted alias, token reorder, declared-surface alias drift, lookup-table token substitution, grouped parser drift, and lookup-table shape/order drift.
3. Canonical demo-path mapping: satisfied by the per-task `continue working` mappings above and the final statement that this handoff makes that step more real while Textual remains disabled.
4. Ownership accounting: satisfied by listing `src/qual/commands/catalog.py` as lane-owned implementation, `tests/unit/test_commands_catalog.py` as the approved shared-by-approval test edit, and integrator-locked edits as `no`.

## Reviewer Packet `20260428T215506Z` Fix Satisfaction

1. Token-level parser-surface validation: satisfied at branch tip by `command_cli_contract()` validating grouped parser projection, accepted token tuple, lookup-table shape/order, and canonical names against `_CLI_COMMAND_SURFACE`.
2. Parser-surface drift tests: satisfied by focused regressions covering added known alias, removed accepted alias, substituted accepted token for the same canonical command, same-canonical token reorder, declared-surface alias drift, and lookup-table drift.
3. Canonical demo-path mapping: satisfied by the per-task `continue working` mapping above and the final statement that the stable CLI contract keeps follow-up operator turns from continuing through a drifted parser surface.
4. Ownership accounting: satisfied by listing `tests/unit/test_commands_catalog.py` as the approved shared-by-approval edit and confirming integrator-locked edits are `no`.

## Reviewer Packet `20260428T215757Z` Fix Satisfaction

1. Complete branch-tip metadata accounting: satisfied by listing `THREAD.md` and `THREAD_PACKET.md` as metadata-only packet files and keeping `tests/unit/test_commands_catalog.py` recorded as the approved shared-by-approval test edit.
2. Implementation review basis: unchanged; this pass makes no code edits to `src/qual/commands/catalog.py` or `tests/unit/test_commands_catalog.py`.
3. Gate restatement after metadata correction: required gates passed again at `2026-04-28T22:00:00Z`.

## Reviewer Packet `20260428T220047Z` Fix Satisfaction

1. Actual branch-tip packet: this packet presents the final branch tip after the `2026-04-28T22:01:42Z` fixer pass as the review basis, and it does not classify code-bearing `src/qual/commands/catalog.py` or `tests/unit/test_commands_catalog.py` commits as metadata-only.
2. Full parser-surface validation: already satisfied at branch tip by `command_cli_contract()` comparing grouped parser projection, accepted token tuple, lookup-table shape/order, and canonical names against `_CLI_COMMAND_SURFACE`.
3. Parser-surface drift tests: already satisfied by focused regressions for alias substitution, added accepted alias, removed accepted alias, parser-token reordering, declared-surface alias drift, grouped parser drift, lookup-table token substitution, and lookup-table shape/order drift.
4. Canonical demo-path mapping: satisfied by the per-task `continue working` mappings above and the final statement that the stable CLI contract keeps follow-up operator turns from continuing through a drifted parser surface.
5. Ownership accounting: satisfied by listing `tests/unit/test_commands_catalog.py` as the approved shared-by-approval test edit and confirming integrator-locked edits are `no`.
6. Final verification: focused catalog regressions and all required gates passed at `2026-04-28T22:02:44Z`.

## Reviewer Packet `20260428T220257Z` Fix Satisfaction

1. Reviewer verdict: `APPROVED`.
2. Required fixes before re-review: none.
3. Fixer action: no code changes were needed; this pass records the approval and reruns all required gates on the final tree.
4. Final verification: required gates passed again at `2026-04-28T22:04:00Z`.

## Reviewer Packet `20260428T220712Z` Fix Satisfaction

1. Actual branch-tip packet: this packet presents the final branch tip after the `2026-04-28T22:10:40Z` fixer pass as the review basis and keeps code-bearing catalog/test commits in the implementation basis.
2. Full parser-surface validation: already satisfied at branch tip by `command_cli_contract()` comparing grouped parser projection, accepted token tuple, lookup-table shape/order, and canonical names against `_CLI_COMMAND_SURFACE`.
3. Parser-surface drift tests: coverage now includes accepted-token substitution to another known alias with the same canonical command, plus added alias, removed alias, token reorder, declared-surface alias drift, grouped parser drift, lookup-table token substitution, and lookup-table shape/order drift.
4. Canonical demo-path mapping: every completed task maps to `continue working`, with the concrete blocker removed stated above.
5. Final verification: focused catalog regressions and all required gates passed at `2026-04-28T22:10:40Z`.

## Reviewer Packet `20260428T220957Z` Fix Satisfaction

1. Actual branch-tip packet: this packet presents the final branch tip after the `2026-04-28T22:12:47Z` fixer pass as the review basis and keeps all code-bearing catalog/test changes in the implementation basis.
2. Canonical demo-path mapping: every completed task maps to `continue working`, with the concrete blocker removed stated above.
3. Precise ownership accounting: `src/qual/commands/catalog.py` is lane-owned, `tests/unit/test_commands_catalog.py` is approved shared-by-approval, and integrator-locked edits are `no`.
4. Final verification: all required gates passed at `2026-04-28T22:12:47Z`.

## Final Verification

- Required gates passed on branch `codex/feat-commands` at `2026-04-28T21:35:44Z`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- Required gates passed again on branch `codex/feat-commands` at `2026-04-28T21:40:36Z`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- Required gates passed again on branch `codex/feat-commands` at `2026-04-28T21:44:02Z`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- Approved reviewer packet `20260428T214345Z` required no code fixes; required gates passed again at `2026-04-28T21:45:26Z`.
- Reviewer packet `20260428T214706Z` requested packet-basis correction plus parser-surface fixes already present at branch tip; required gates passed again at `2026-04-28T21:50:01Z`.
- Reviewer packet `20260428T214934Z` requested explicit parser-surface validation, parser-surface drift tests, canonical demo-path mapping, and ownership accounting; required gates passed again at `2026-04-28T21:51:29Z`.
- Reviewer packet `20260428T214935Z` repeated those required fixes; required gates passed again at `2026-04-28T21:52:01Z`.
- Approved reviewer packet `20260428T215233Z` required no code fixes; this pass records the approval and required gates passed again at `2026-04-28T21:54:07Z`.
- Focused catalog regression check passed at `2026-04-28T21:55:56Z`: `python -m unittest tests.unit.test_commands_catalog`.
- Reviewer packet `20260428T215506Z` required fixes were verified at branch tip; required gates passed again at `2026-04-28T21:56:45Z`.
- Reviewer packet `20260428T215757Z` requested complete branch-tip metadata accounting and no code changes; required gates passed again at `2026-04-28T22:00:00Z`.
- Reviewer packet `20260428T220047Z` requested branch-tip review-basis correction, parser-surface validation confirmation, drift-test citation, demo-path mapping, and ownership accounting; focused catalog regressions and required gates passed at `2026-04-28T22:02:44Z`.
- Approved reviewer packet `20260428T220257Z` required no code fixes; required gates passed again at `2026-04-28T22:04:00Z`.
- Reviewer packet `20260428T220712Z` requested branch-tip review-basis correction, parser-surface validation, same-canonical accepted-token substitution coverage, canonical demo-path mapping, and gate rerun; focused catalog regressions and all required gates passed at `2026-04-28T22:10:40Z`.
- Reviewer packet `20260428T220957Z` requested actual branch-tip review basis, per-task canonical demo-path mapping, precise ownership accounting, and gate rerun; all required gates passed at `2026-04-28T22:12:47Z`.
