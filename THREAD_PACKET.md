# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` plus metadata-only packet refresh commits through the final fixer commit.
- Fixer correction: this refresh resolves reviewer packet `20260429T171312Z` by choosing the clean `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` review basis, restoring later implementation drift out of the branch tip, and keeping only metadata changes after the reviewed implementation target.

## Required-Fix Resolution

1. Review basis is clean and branch-matched: post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation drift in `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py` has been restored back to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`. The diff after that implementation target is packet metadata only.
2. The packet keeps every reviewed implementation file in scope for `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
3. The integrator-locked `src/qual/cli.py` edit was removed from the final review basis. No explicit integrator approval is needed because no `src/qual/cli.py` diff remains after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
4. Metadata file accounting is complete: post-target packet refresh changes include both `THREAD.md` and `THREAD_PACKET.md`.
5. Gate results below are tied to the final branch tip after the drift-removal commit.

## Implementation Summary

- `src/qual/commands/catalog.py` validates CLI canonical names against `command_names()` and returns the canonical command tuple.
- `tests/unit/test_commands_catalog.py` covers command order alignment and rejects command catalog drift.
- No implementation files remain changed after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this fixer restores later implementation drift and updates packet metadata.

## Canonical Demo-Path Mapping

Canonical demo-path sequence: `open project/document`, `retrieve relevant material`, `gather context into basket`, `plan/revise`, `apply/reject patch`, `persist state`, `continue working`.

This command-catalog work provides deterministic CLI command names for the CLI fallback surfaces used along that path:

1. `open project/document`: keeps open/document command surfaces discoverable through the catalog contract.
2. `retrieve relevant material`: directly advances this step by proving retrieval command names cannot silently drift between catalog metadata and CLI-facing command names.
3. `gather context into basket`: keeps context-basket command discovery tied to the same canonical command list.
4. `plan/revise`: keeps planning/revision command surfaces represented in the stable command catalog.
5. `apply/reject patch`: keeps patch preview/apply/reject-adjacent command surfaces discoverable through canonical metadata.
6. `persist state`: keeps terminal/export handoff command surfaces represented for persistence-oriented CLI fallback flows.
7. `continue working`: keeps follow-on command surfaces stable so resumed CLI workflows use the same command tokens.

The direct implementation effect is CLI contract stability, not new behavior for opening, retrieval, context storage, patch application, persistence, or resume flows.

## Files Changed In Review Target

Reviewed implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`:

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

Metadata refresh commit `a8b484ee9d8f9e8b5676faf1a0534eff23d6a19d`:

- `THREAD.md`
- `THREAD_PACKET.md`

Metadata refresh commit `7fd312d6d1c8aae5554bba05265b939c1163bdfa`:

- `THREAD.md`
- `THREAD_PACKET.md`

This fixer refresh for reviewer packet `20260429T170759Z`:

- `THREAD.md`
- `THREAD_PACKET.md`

This fixer refresh for reviewer packet `20260429T171312Z`:

- `THREAD.md`
- `THREAD_PACKET.md`
- Restores `src/qual/cli.py` to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Restores `src/qual/commands/__init__.py` to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Restores `src/qual/commands/catalog.py` to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Restores `tests/unit/test_commands_catalog.py` to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.

Branch-tip file list for this review basis as it would be merged after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`:

- `THREAD.md`
- `THREAD_PACKET.md`

Complete branch-tip file list for `codex/feat-commands` as it would actually be merged:

- `THREAD.md`
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

## Ownership And Scope

- Lane-owned implementation file touched in reviewed implementation: `src/qual/commands/catalog.py`.
- Earlier branch implementation files already present in the clean `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` basis: `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/diff_preview.py`, and `tests/unit/test_diff_preview.py`.
- Approved shared-by-approval test file touched in reviewed implementation: `tests/unit/test_commands_catalog.py`.
- Integrator-locked implementation files touched in reviewed implementation: none.
- Shared/integrator-locked edits: no integrator-locked implementation edits remain in the final review basis. The prior post-target `src/qual/cli.py` drift was removed by restoring it to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Shared test edit: `tests/unit/test_commands_catalog.py` is an approved test exception in the reviewed implementation target and is separate from the integrator-locked file list.
- Routing/provider impact: none.

## Commands Run

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS, smoke plus 125 unit tests.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS, including scope-check, format, lint, compile, smoke, and 125 unit tests.

## Risks And Blockers

- Risk: the final packet intentionally chooses the clean `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` review basis rather than the broader prior branch tip, so any later implementation work must be reviewed in a separate packet.
- Blockers: none known.

## Final Readiness Statement

This handoff packet now explicitly names the canonical demo-path steps advanced by the command-catalog slice, separates the approved shared test edit from integrator-locked implementation edits, removes the post-target `src/qual/cli.py` drift from the final review basis, and accounts for both metadata files changed after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
