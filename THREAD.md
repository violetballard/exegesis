# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: final branch tip after this fixer pass; implementation and packet metadata are reviewed together.
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

## Canonical Demo-Path Mapping

- Task 1 advances `continue working`: parser/catalog validation prevents follow-up CLI turns from continuing through a silently drifted command contract.
- Task 2 advances `continue working`: returning the canonical command-name tuple preserves deterministic command ordering across operator turns.
- Task 3 advances `continue working`: regression tests lock the command-catalog contract so later CLI drift is caught before handoff.
- Task 4 advances `continue working`: refreshed handoff metadata gives reviewer/integrator the exact narrow review basis.
- Final demo-path statement: this handoff makes `continue working` more real by keeping the CLI command contract deterministic while Textual remains disabled.

## Blocker Removed

Parser/catalog drift validation is needed now because the CLI is the active operator surface for the engine-side MVP loop. Without a fail-fast contract check, open/retrieve/basket/revise/patch/save follow-up turns could continue through a parser surface that no longer matches the canonical command catalog.

## Required Fix Satisfaction

1. `command_cli_contract()` validates the full declared parser surface: grouped parser projection, CLI token tuple, lookup table, and canonical command order.
2. Regression coverage patches `_CLI_ENTRYPOINTS` for added valid alias, removed accepted token, substituted valid token, and parser-token reorder drift.
3. Handoff mapping names the canonical demo-path step advanced by each completed task and states the final demo-path step made more real.
4. The required gates were rerun after the parser-surface validation, regression tests, and handoff mapping were aligned.
5. The only approved non-owned path remains `tests/unit/test_commands_catalog.py`; there are no integrator-locked edits in the final review tree.

## Required Gates

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

Latest fixer pass: `fixer__feat-commands__20260428T205430Z` requested full parser-surface drift validation, matching regression tests for added/removed/substituted/reordered parser tokens, canonical demo-path mapping in the handoff, and a full gate rerun. This pass keeps the implementation narrow and aligns the packet claims with the final tree.
