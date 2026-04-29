# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: final branch tip after this fixer pass for reviewer packet `20260429T000428Z`; implementation, tests, scope-check support, and packet metadata are reviewed together.
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

- Added `_CANONICAL_CLI_COMMAND_SURFACE` and explicit canonical token/lookup projections so `_CLI_COMMAND_SURFACE`, `_CLI_ENTRYPOINTS`, and `command_cli_lookup_table()` cannot drift by changing to a same-canonical alias while remaining self-consistent.
- Kept `_CLI_ENTRYPOINTS` frozen against the canonical accepted token tuple.
- Added regression coverage for declared-surface order drift and self-consistent declared-surface drift where the declared surface and entrypoints both substitute `bootstrap` with same-canonical alias `open`.
- Added regression coverage for lookup-table added same-canonical alias drift where `open` appears as an accepted `bootstrap` parser row without being part of the canonical CLI surface.
- Added regression coverage for same-canonical alias order drift where `diff` and `diff-preview` are reordered within the accepted parser tokens or the declared `diff-preview` parser group.
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

## Reviewer Packet `20260428T233637Z` Fix Satisfaction

1. Strengthen `command_cli_contract()` parser-token drift validation: satisfied by validating the accepted CLI token tuple, declared canonical CLI surface, grouped parser projection, lookup-table shape/order, and canonical command order against `_CANONICAL_CLI_COMMAND_SURFACE`.
2. Add same-canonical alias substitution regression coverage: satisfied by tests that reject replacing accepted tokens with same-canonical aliases such as `diff_preview` and adding `open` as an accepted `bootstrap` parser row.
3. State concrete canonical demo-path step: satisfied by mapping the contract to open project/document, retrieve/context basket, patch preview, and continued CLI operation.
4. Correct ownership accounting: satisfied by listing `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` as approved shared-by-approval tests and `Integrator-locked edits: no`.

## Reviewer Packet `20260428T234152Z` Fix Satisfaction

1. Regenerate packet from actual merge candidate: satisfied by anchoring review to the final `codex/feat-commands` branch tip after this fixer pass; the branch-tip implementation, tests, `scripts/scope-check.sh`, `THREAD.md`, and `THREAD_PACKET.md` are submitted together.
2. Strengthen `command_cli_contract()` parser-surface drift rejection: already satisfied in the branch-tip implementation by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`.
3. Add focused parser-surface drift coverage: already satisfied by regression coverage for added aliases, removed aliases, same-canonical substitutions, token reorder, declared-surface drift, lookup-table token substitution, and lookup-table shape/order drift.
4. Reconcile ownership accounting: satisfied by listing command files as lane-owned, tests as approved shared-by-approval, `scripts/scope-check.sh` as shared gate support, metadata files as metadata-only, and integrator-locked edits as `no`.
5. Rerun required gates against final reviewed tip: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Reviewer Packet `20260428T234728Z` Fix Satisfaction

1. Actual merge-candidate packet: satisfied by anchoring review to the final branch tip after this fixer pass and reviewing implementation, tests, scope-check support, and metadata together.
2. Metadata classification: satisfied by stating that no command-catalog implementation or test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are metadata-only.
3. Parser-surface drift rejection: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Parser-surface drift regression tests: satisfied by coverage for added aliases, removed aliases, same-canonical substitutions, same-canonical order drift, token reorder, declared-surface drift, lookup-table token substitution, and lookup-table shape/order drift.
5. Handoff accounting: satisfied by mapping the canonical demo path and distinguishing lane-owned command files, approved shared-by-approval tests, shared scope-check support, metadata-only files, and integrator-locked edits as `no`.
6. Gate rerun: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Reviewer Packet `20260428T234820Z` Fix Satisfaction

1. Actual merge-candidate packet: satisfied by anchoring review to the final branch tip after this fixer pass and reviewing implementation, tests, scope-check support, and metadata together.
2. Metadata classification: satisfied by stating that no command-catalog implementation or test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are metadata-only.
3. Parser-surface drift rejection: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Parser-surface drift regression tests: satisfied by coverage for added aliases, removed aliases, same-canonical substitutions, token reorder, declared-surface drift, lookup-table token substitution, and lookup-table shape/order drift.
5. Handoff accounting: satisfied by mapping the canonical demo path and distinguishing lane-owned command files, approved shared-by-approval tests, shared scope-check support, metadata-only files, and integrator-locked edits as `no`.
6. Gate rerun: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Reviewer Packet `20260428T235008Z` Fix Satisfaction

1. Actual merge-candidate packet: satisfied by anchoring review to the final branch tip after this fixer pass and reviewing implementation, tests, scope-check support, and metadata together.
2. Metadata classification: satisfied by stating that no command-catalog implementation or test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are metadata-only.
3. Parser-surface drift rejection: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Parser-surface drift regression tests: satisfied by coverage for added aliases, removed aliases, same-canonical substitutions, token reorder, declared-surface drift, lookup-table token substitution, and lookup-table shape/order drift.
5. Handoff accounting: satisfied by mapping the canonical demo path and distinguishing lane-owned command files, approved shared-by-approval tests, shared scope-check support, metadata-only files, and integrator-locked edits as `no`.
6. Gate rerun: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Reviewer Packet `20260428T235333Z` Fix Satisfaction

1. Full parser-surface validation: satisfied by `command_cli_contract()` validating accepted parser tokens, declared canonical surface, grouped parser projection, lookup-table order/shape, and canonical command order against `_CANONICAL_CLI_COMMAND_SURFACE`.
2. Drift regressions: satisfied by focused tests for alias substitution that resolves to the same canonical command, same-canonical alias order drift, added aliases, removed aliases, parser-token reorder, and lookup-table drift.
3. Canonical demo-path step: satisfied by mapping the work to open project/document, retrieve/context basket, patch preview, and continued CLI operation.
4. Ownership accounting: satisfied by listing command files as lane-owned, tests as approved shared-by-approval, `scripts/scope-check.sh` as shared gate support, metadata files as metadata-only, and integrator-locked edits as `no`.

## Reviewer Packet `20260428T235908Z` Fix Satisfaction

1. Actual merge-candidate packet: satisfied by anchoring this packet to the final `codex/feat-commands` branch tip after this fixer pass rather than stale commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Metadata classification: satisfied by stating that no command-catalog implementation or test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are metadata-only.
3. Full parser-surface drift rejection: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Parser-surface drift regressions: satisfied by focused tests for added same-canonical aliases, removed accepted tokens, same-canonical substitutions, token reorder, and lookup-table shape/order drift.
5. Canonical demo-path mapping: satisfied in the task list and mapping section by naming open project/document, retrieve/context basket, patch preview, and continued CLI operation.
6. Required gates: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Reviewer Packet `20260429T000428Z` Fix Satisfaction

1. Actual merge-candidate packet: satisfied by anchoring this packet to the final `codex/feat-commands` branch tip after this fixer pass rather than stale commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Metadata classification: satisfied by stating that no command-catalog implementation or test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are metadata-only.
3. Full parser-surface drift rejection: satisfied by `command_cli_contract()` validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, canonical names, and explicit canonical token/lookup projections against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Parser-surface drift regressions: satisfied by focused tests for added aliases, removed aliases, same-canonical substitutions, token reorder, declared-surface drift, grouped parser drift, lookup-table token substitution, lookup-table shape/order drift, and canonical token/lookup projection alignment.
5. Canonical demo-path mapping and ownership accounting: satisfied by naming open project/document, retrieve/context basket, patch preview, continued CLI operation, lane-owned command files, approved shared-by-approval tests, shared scope-check support, and `Integrator-locked edits: no`.
6. Required gates: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Verification

- `python3 -m unittest tests.unit.test_commands_catalog -v`: PASS (58 tests)
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS
- Final verification pass: `2026-04-29T00:06:01Z`
