# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: final branch tip after this fixer pass for reviewer packet `20260428T233046Z`; implementation, tests, scope-check support, and packet metadata are reviewed together.
- Scope: CLI command-catalog contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: Milestone 3 CLI compatibility for the engine-first workflow loop, and `feat-commands` as the command-surface compatibility lane.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface.

## Reviewed Files

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`
- `scripts/scope-check.sh`
- `THREAD.md`
- `THREAD_PACKET.md`

## Shared / Approval Notes

- Lane-owned implementation edits: `src/qual/commands/catalog.py`, `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/diff_preview.py`.
- Approved shared-by-approval test edits: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`.
- Scope-check support edit: `scripts/scope-check.sh` updates branch ownership enforcement so the required gate can evaluate this lane and other active engine-first lanes.
- Metadata-only handoff files: `THREAD.md`, `THREAD_PACKET.md`.
- Integrator-locked edits: no.

## Current Fix Summary

- Added `_CANONICAL_CLI_COMMAND_SURFACE` so `_CLI_COMMAND_SURFACE` cannot drift by changing to a same-canonical alias while remaining self-consistent.
- Kept `_CLI_ENTRYPOINTS` frozen against the canonical accepted token tuple.
- Added regression coverage for declared-surface order drift and self-consistent declared-surface drift where the declared surface and entrypoints both substitute `bootstrap` with same-canonical alias `open`.
- Regenerated the packet from the actual branch tip and stopped classifying code-bearing command/test commits as metadata-only.

## Canonical Demo-Path Mapping

- Task 1 protects the `open project/document` step by keeping the `bootstrap` CLI entrypoint aligned with the canonical command catalog.
- Task 2 protects the `retrieve relevant material` and `promote or gather context into the basket` steps by keeping the `context-basket` CLI entrypoint deterministic.
- Task 3 protects the `preview and apply or reject a patch` step by preventing parser/catalog drift for the `diff-preview` and `diff` CLI surface.
- Task 4 protects reviewability of the same demo path by refreshing handoff metadata with the exact branch-tip review basis.
- Final demo-path statement: this handoff makes the open project/document, retrieve/context basket, patch preview, and continued CLI operation portions of the CLI-first MVP loop more real by preventing parser/catalog drift for `bootstrap`, `context-basket`, `diff-preview`, `diff`, and `terminal` while Textual remains disabled.

## Reviewer Packet `20260428T231936Z` Fix Satisfaction

1. Required fix 1, concrete canonical demo-path mapping: satisfied by mapping the command-catalog contract to open project/document (`bootstrap`), retrieve/context basket (`context-basket`), patch preview (`diff-preview` and `diff`), and continued CLI operation (`terminal`).
2. Required fix 2, command-surface scope: satisfied under the current full branch-tip accounting; this pass does not add CLI flags, Textual work, routing/provider changes, or non-command business logic.
3. Required fix 3, approved shared-test exception and complete changed-file list: satisfied by listing the real nine-file branch-tip range and distinguishing lane-owned command files, approved shared tests, scope-check support, and metadata files.

## Verification

- `python3 -m unittest tests.unit.test_commands_catalog -v`: PASS (55 tests)
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS
- Final verification pass: `2026-04-28T23:32:29Z`
