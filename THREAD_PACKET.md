# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: final branch tip after the `20260429T173336Z` fixer, including implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, implementation fixer commit `3f180d67ca82eebdce9da411fc2da5356064d46f`, and subsequent packet refresh commits.
- Merge target: `codex/feat-commands` branch tip as merged against `main`.
- Fixer correction: this refresh resolves reviewer packet `20260429T173336Z` by keeping one branch-truthful review basis, keeping `3f180d67ca82eebdce9da411fc2da5356064d46f` in scope as an implementation commit, explicitly accounting for `src/qual/cli.py` as shared-by-approval/integrator-locked implementation work, and reporting normal gate results from the actual branch tip.

## Required-Fix Resolution

1. `command_cli_contract()` now compares catalog-owned `command_cli_tokens()` to the live argparse subparser choices extracted from `src/qual/cli.py`, so parser-only added tokens, missing tokens, and alias renames fail fast.
2. `src/qual/cli.py` now builds top-level parsers from `command_cli_tokens()` and `_normalize_argv()` uses the same catalog-owned token set, removing the separate hardcoded command-token duplication.
3. `tests/unit/test_commands_catalog.py` now asserts the actual parser surface and includes focused parser-only added-token, missing-token, and alias-rename drift tests.
4. Ownership accounting is corrected below: this fixer intentionally keeps shared-by-approval/integrator-locked `src/qual/cli.py` in scope to satisfy the reviewer-required parser contract fix, plus the approved shared test file.
5. Gate results below are tied to the actual branch tip after the `20260429T173336Z` fixer commit; normal scope-check and normal CI both pass without `SCOPE_ALLOW_SHARED=1`.

## Implementation Summary

- `src/qual/commands/catalog.py` validates CLI canonical names against `command_names()` and validates catalog tokens against the live argparse parser surface.
- `src/qual/cli.py` builds top-level command parsers from `command_cli_tokens()` and validates the CLI contract before parsing.
- `tests/unit/test_commands_catalog.py` covers command order alignment, catalog drift, parser-only added-token drift, parser-only missing-token drift, and parser-only alias-rename drift.

## Canonical Demo-Path Mapping

Canonical demo-path sequence: `open project/document`, `retrieve relevant material`, `gather context into basket`, `plan/revise`, `apply/reject patch`, `persist state`, `continue working`.

This command-catalog work provides deterministic CLI command names for the CLI fallback surfaces used along that path. The narrow canonical demo-path step advanced by this fixer is `gather context into basket`: the `context-basket` retrieval command parser surface now fails fast when it diverges from catalog metadata. It also supports the adjacent `retrieve relevant material` CLI fallback contract by keeping retrieval command discovery deterministic.

1. `open project/document`: keeps open/document command surfaces discoverable through the catalog contract.
2. `retrieve relevant material`: directly advances this step by proving retrieval command names cannot silently drift between catalog metadata and CLI-facing command names.
3. `gather context into basket`: keeps context-basket command discovery tied to the same canonical command list.
4. `plan/revise`: keeps planning/revision command surfaces represented in the stable command catalog.
5. `apply/reject patch`: keeps patch preview/apply/reject-adjacent command surfaces discoverable through canonical metadata.
6. `persist state`: keeps terminal/export handoff command surfaces represented for persistence-oriented CLI fallback flows.
7. `continue working`: keeps follow-on command surfaces stable so resumed CLI workflows use the same command tokens.

The direct implementation effect is parser/catalog contract stability for CLI fallback, not new behavior for opening, retrieval, context storage, patch application, persistence, or resume flows.

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

Implementation fixer commit `3f180d67ca82eebdce9da411fc2da5356064d46f`:

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/cli.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

Packet-only refresh commits after `3f180d67ca82eebdce9da411fc2da5356064d46f`:

- `THREAD.md`
- `THREAD_PACKET.md`

This fixer refresh for reviewer packet `20260429T173336Z`:

- `THREAD.md`
- `THREAD_PACKET.md`

Complete branch-tip file list for `codex/feat-commands` as it would actually be merged against `main`:

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

- Lane-owned implementation file touched in reviewed implementation and this fixer: `src/qual/commands/catalog.py`.
- Earlier branch implementation files already present in the clean `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` basis: `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/diff_preview.py`, and `tests/unit/test_diff_preview.py`.
- Approved shared-by-approval test file touched in reviewed implementation and this fixer: `tests/unit/test_commands_catalog.py`.
- Shared-by-approval/integrator-locked implementation file touched in this fixer and retained in review scope: `src/qual/cli.py`.
- Shared/integrator-locked edits: YES. Explicit approval is required for `src/qual/cli.py`; the edit is limited to the reviewer-required parser/catalog contract fix and does not change provider or routing files.
- Shared test edit: `tests/unit/test_commands_catalog.py` is an approved test exception and is separate from the `src/qual/cli.py` shared implementation edit.
- Routing/provider impact: none.

## Commands Run

- `make scope-check`: PASS on the actual branch tip after the `20260429T173336Z` fixer. No `SCOPE_ALLOW_SHARED=1` override was required for this run.
- `SCOPE_ALLOW_SHARED=1 make scope-check`: not rerun for this fixer because the normal gate passed; earlier packet-refresh history recorded this override path as PASS when the shared `src/qual/cli.py` implementation edit first needed explicit scope approval.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `python -m unittest tests.unit.test_commands_catalog`: PASS, 46 tests.
- `./quality-test.sh`: PASS, smoke plus 128 unit tests.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS on the actual branch tip after the `20260429T173336Z` fixer, including normal scope-check, format, lint, compile, smoke, and 128 unit tests. No `SCOPE_ALLOW_SHARED=1` override was required for this run.
- `SCOPE_ALLOW_SHARED=1 make ci`: not rerun for this fixer because normal CI passed; earlier packet-refresh history recorded this override path as PASS.

## Risks And Blockers

- Risk: `src/qual/cli.py` is shared-by-approval/integrator-locked, but this edit is narrowly scoped to the reviewer-required parser/catalog validation path.
- Blocker: `src/qual/cli.py` remains a shared-by-approval/integrator-locked implementation edit and requires integrator approval. Normal scope-check and normal CI pass at the actual branch tip after this fixer.

## Final Readiness Statement

This handoff packet now explicitly names the narrow canonical demo-path step advanced by the command-catalog slice, separates the approved shared test edit from the shared `src/qual/cli.py` implementation edit, and accounts for the parser/catalog drift fix requested by reviewer packet `20260429T173336Z`.
