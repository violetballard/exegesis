# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` plus metadata refresh commits `a8b484ee9d8f9e8b5676faf1a0534eff23d6a19d` and `7fd312d6d1c8aae5554bba05265b939c1163bdfa`.
- Fixer correction: this metadata-only refresh resolves reviewer packet `20260429T170759Z`; it does not change the reviewed implementation.

## Required-Fix Resolution

1. The canonical demo-path mapping is explicit below. This command-catalog slice advances CLI contract stability for the existing `open project/document`, `retrieve relevant material`, `gather context into basket`, `plan/revise`, `apply/reject patch`, `persist state`, and `continue working` command surfaces. It makes `retrieve relevant material` more real directly by preventing parser/catalog drift for retrieval command discovery and parsing.
2. Ownership wording is corrected: the reviewed implementation target contains one lane-owned command file and one approved shared-by-approval test file. There were no integrator-locked implementation edits in commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
3. Re-review should stay pinned to implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and metadata refresh commits `a8b484ee9d8f9e8b5676faf1a0534eff23d6a19d` and `7fd312d6d1c8aae5554bba05265b939c1163bdfa`.

## Implementation Summary

- `src/qual/commands/catalog.py` validates CLI canonical names against `command_names()` and returns the canonical command tuple.
- `tests/unit/test_commands_catalog.py` covers command order alignment and rejects command catalog drift.
- No implementation files are changed by this fixer refresh.

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

Implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`:

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

## Ownership And Scope

- Lane-owned implementation file touched in reviewed implementation: `src/qual/commands/catalog.py`.
- Approved shared-by-approval test file touched in reviewed implementation: `tests/unit/test_commands_catalog.py`.
- Integrator-locked implementation files touched in reviewed implementation: none.
- Shared/integrator-locked edits: no integrator-locked implementation edits. The shared test edit is an approved test exception and is separate from the integrator-locked file list.
- Routing/provider impact: none.

## Commands Run

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS, 136 unit tests plus smoke.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS, including scope-check, format, lint, compile, smoke, and 136 unit tests.

## Risks And Blockers

- Risk: metadata-only correction depends on the reviewer accepting the narrowed re-review target exactly as requested: implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` plus metadata refresh commits `a8b484ee9d8f9e8b5676faf1a0534eff23d6a19d` and `7fd312d6d1c8aae5554bba05265b939c1163bdfa`.
- Blockers: none known.

## Final Readiness Statement

This handoff packet now explicitly names the canonical demo-path steps advanced by the command-catalog slice and separates the approved shared test edit from integrator-locked implementation edits. Re-review should remain pinned to implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and metadata refresh commits `a8b484ee9d8f9e8b5676faf1a0534eff23d6a19d` and `7fd312d6d1c8aae5554bba05265b939c1163bdfa`.
