# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: full current branch tip, including parser-surface implementation, regression tests, and packet metadata. No commits are excluded from review.
- Scope: CLI command-catalog contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: Milestone 3 CLI compatibility for the engine-first workflow loop, and `feat-commands` as the command-surface compatibility lane.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface.

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

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

1. `command_cli_contract()` now validates the full expected CLI token tuple and lookup table, not just deduplicated canonical names.
2. Regression coverage now includes extra accepted alias, removed accepted alias, substituted accepted alias, and reordered parser-token drift while canonical names remain stable.
3. Packet metadata now uses the full current branch tip as the review basis instead of pinning review to an older implementation commit.
4. Roadmap/vision mapping stays limited to Milestone 3 CLI compatibility for the engine-first `continue working` loop.

## Required Gates

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS
