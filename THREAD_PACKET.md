# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: final branch tip after the `20260429T183248Z` fixer, including implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, implementation fixer commit `3f180d67ca82eebdce9da411fc2da5356064d46f`, smoke-plan implementation commit `c320dafa67733469fac8c60aa1ec3b54d2ef6c97`, packet/test correction commit `153c1271575ee1ea4256378f560c255254fef2c6a`, and this required-fix commit.
- Merge target: `codex/feat-commands` branch tip as merged against `main`.
- Fixer correction: this refresh resolves reviewer packet `20260429T183248Z` by keeping one branch-truthful review basis at the actual merge scope, keeping `3f180d67ca82eebdce9da411fc2da5356064d46f`, `c320dafa67733469fac8c60aa1ec3b54d2ef6c97`, and `153c1271575ee1ea4256378f560c255254fef2c6a` in scope as implementation/test commits, explicitly accounting for `src/qual/cli.py` as shared-by-approval/integrator-locked implementation work, documenting the MVP command smoke-plan behavior, and reporting required gate results from the same branch tip.

## Required Handoff Fields

- Branch name: `codex/feat-commands`
- Scope completed: command catalog metadata now has a live argparse parser-surface contract, deterministic CLI token lookup, route/flow metadata for MVP command discovery, an exported MVP command smoke plan, and regression tests for parser/catalog drift plus smoke-plan argv consistency.
- Roadmap item(s) affected: `Milestone 1: Bootstrap Flow Stabilization`, `Milestone 2: Test Hardening`, and MVP active implementation emphasis for `feat-commands`.
- Vision capability affected: `Operator-first control surface`, because CLI remains a first-class reliable surface, and `Retrieval-first context handling`, because retrieval/context-basket command parsing is kept deterministic for CLI fallback flows.
- Routing/provider impact note: no model routing or provider configuration touched.
- Proposed README.md patch text: none.

## Required-Fix Resolution

1. `command_cli_contract()` now compares catalog-owned `command_cli_tokens()` to the live argparse subparser choices extracted from `src/qual/cli.py`, so parser-only added tokens, missing tokens, and alias renames fail fast.
2. `src/qual/cli.py` now builds top-level parsers from `command_cli_tokens()` and `_normalize_argv()` uses the same catalog-owned token set, removing the separate hardcoded command-token duplication.
3. `tests/unit/test_commands_catalog.py` now asserts the actual parser surface and includes focused parser-only added-token, missing-token, and alias-rename drift tests that mutate real argparse parser choices before `command_cli_contract()` reads the live parser surface.
4. `c320dafa67733469fac8c60aa1ec3b54d2ef6c97` is explicitly included as implementation scope: it exports `CommandSmokePlan`, `CommandSmokeStep`, `command_smoke_plan()`, `command_demo_smoke_plan()`, and `command_mvp_smoke_plan()`, with deterministic argv for `bootstrap`, `context-basket list`, `diff-preview --original before --proposed after`, and terminal handoff smoke commands.
5. `tests/unit/test_commands_catalog.py` now covers the exported smoke-plan API and rejects configured smoke argv that does not match the route's CLI tokens.
6. Ownership accounting is corrected below: this fixer intentionally keeps shared-by-approval/integrator-locked `src/qual/cli.py` in scope to satisfy the reviewer-required parser contract fix, plus the approved shared test file and lane-owned command smoke-plan files.
7. `153c1271575ee1ea4256378f560c255254fef2c6a` is explicitly classified as a test plus packet correction commit, not metadata-only, because it modifies `tests/unit/test_commands_catalog.py` in addition to `THREAD.md` and `THREAD_PACKET.md`.
8. Gate results below are tied to the actual branch tip after this `20260429T183248Z` fixer commit; normal scope-check and normal CI both pass without `SCOPE_ALLOW_SHARED=1`.

## Implementation Summary

- `src/qual/commands/catalog.py` validates CLI canonical names against `command_names()` and validates catalog tokens against the live argparse parser surface.
- `src/qual/commands/catalog.py` exposes a command smoke plan that maps each MVP demo flow step to executable CLI argv for the smoke route.
- `src/qual/commands/__init__.py` exports the smoke-plan dataclasses and helper functions as part of the command catalog API.
- `src/qual/cli.py` builds top-level command parsers from `command_cli_tokens()` and validates the CLI contract before parsing.
- `tests/unit/test_commands_catalog.py` covers command order alignment, catalog drift, parser-only added-token drift, parser-only missing-token drift, parser-only alias-rename drift, exported smoke-plan argv, and smoke-plan config consistency.

## Canonical Demo-Path Mapping

Canonical demo-path sequence: `open project/document`, `retrieve relevant material`, `gather context into basket`, `plan/revise`, `apply/reject patch`, `persist state`, `continue working`.

This command-catalog work provides deterministic CLI command names for the CLI fallback surfaces used along that path. The narrow canonical demo-path step advanced by this fixer is `gather context into basket`: the `context-basket` retrieval command parser surface now fails fast when it diverges from catalog metadata. It also supports the adjacent `retrieve relevant material` CLI fallback contract by keeping retrieval command discovery deterministic.

1. Parser/catalog contract task advances `retrieve relevant material` by proving retrieval command names cannot silently drift between catalog metadata and CLI-facing command names.
2. CLI token unification task advances `gather context into basket` by making `context-basket` parser dispatch use the same canonical command-token source as catalog discovery.
3. Parser drift regression task advances `continue working` by failing fast when resumed CLI workflows would see added, missing, or renamed command tokens.
4. Smoke-plan implementation task advances `open project/document`, `retrieve relevant material`, `apply/reject patch`, and `persist state` by publishing executable smoke argv for `bootstrap`, `context-basket list`, `diff-preview`, and terminal handoff.
5. Smoke-plan export task advances `continue working` by making the smoke route available from `src.qual.commands` without callers reaching into catalog internals.
6. Handoff traceability task advances `plan/revise` by making review scope, risks, and command behavior explicit for the next reviewer/integrator pass.

Explicit canonical demo-path step advanced: this slice makes `retrieve relevant material` and `gather context into basket` more real by keeping retrieval and `context-basket` command parsing stable against parser/catalog drift, and it makes `open project/document`, `apply/reject patch`, and `persist state` more concrete by publishing executable smoke argv for their MVP CLI route.

The direct implementation effect is parser/catalog contract stability and a catalog-owned smoke plan for CLI fallback; it does not add new command execution behavior beyond exposing smoke argv metadata.

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

Historical fixer refresh for reviewer packet `20260429T171312Z`:

- `THREAD.md`
- `THREAD_PACKET.md`

This historical packet refresh was superseded by the later branch-tip implementation fixer below; it is not a request to exclude later implementation commits from review scope.

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

This fixer refresh for reviewer packet `20260429T174006Z`:

- `THREAD.md`
- `THREAD_PACKET.md`

This fixer refresh for reviewer packet `20260429T175200Z`:

- `THREAD.md`
- `THREAD_PACKET.md`

This fixer refresh for reviewer packet `20260429T175932Z`:

- `THREAD.md`
- `THREAD_PACKET.md`

Smoke-plan implementation commit `c320dafa67733469fac8c60aa1ec3b54d2ef6c97`:

- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`

Required-fix implementation and packet refresh commit `153c1271575ee1ea4256378f560c255254fef2c6a` for reviewer packet `20260429T182404Z`:

- `THREAD.md`
- `THREAD_PACKET.md`
- `tests/unit/test_commands_catalog.py`

This required-fix implementation and packet refresh for reviewer packet `20260429T183248Z`:

- `THREAD.md`
- `THREAD_PACKET.md`
- `tests/unit/test_commands_catalog.py`

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

- Lane-owned implementation files touched in reviewed implementation and this fixer: `src/qual/commands/__init__.py` and `src/qual/commands/catalog.py`.
- Earlier branch implementation files already present in the clean `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` basis: `src/qual/commands/canonical.py`, `src/qual/commands/diff_preview.py`, and `tests/unit/test_diff_preview.py`.
- Approved shared-by-approval test file touched in reviewed implementation and this fixer: `tests/unit/test_commands_catalog.py`.
- Shared-by-approval/integrator-locked implementation file touched in this fixer and retained in review scope: `src/qual/cli.py`.
- Shared/integrator-locked edits: YES. Explicit approval is required for `src/qual/cli.py`; the edit is limited to the reviewer-required parser/catalog contract fix and does not change provider or routing files.
- Shared test edit: `tests/unit/test_commands_catalog.py` is an approved test exception and is separate from the `src/qual/cli.py` shared implementation edit.
- Routing/provider impact: none.

## Commands Run

- `make scope-check`: PASS on the actual branch tip after the `20260429T183248Z` fixer. No `SCOPE_ALLOW_SHARED=1` override was required for this run.
- `SCOPE_ALLOW_SHARED=1 make scope-check`: not rerun for this fixer because the normal gate passed; earlier packet-refresh history recorded this override path as PASS when the shared `src/qual/cli.py` implementation edit first needed explicit scope approval.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `python -m unittest tests.unit.test_commands_catalog`: PASS, 48 tests, including real-argparse parser-only added-token, missing-token, alias-rename drift coverage, exported smoke-plan argv, and smoke-plan config consistency.
- `./quality-test.sh`: PASS, smoke plus 130 unit tests, including real-argparse parser-only added-token, missing-token, alias-rename drift coverage, exported smoke-plan argv, and smoke-plan config consistency.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS on the actual branch tip after the `20260429T183248Z` fixer, including normal scope-check, format, lint, compile, smoke, and 130 unit tests. No `SCOPE_ALLOW_SHARED=1` override was required for this run.
- `SCOPE_ALLOW_SHARED=1 make ci`: not rerun for this fixer because normal CI passed; earlier packet-refresh history recorded this override path as PASS.

## Risks And Blockers

- Risk: `src/qual/cli.py` is shared-by-approval/integrator-locked, but this edit is narrowly scoped to the reviewer-required parser/catalog validation path.
- Blocker: `src/qual/cli.py` remains a shared-by-approval/integrator-locked implementation edit and requires integrator approval. Normal scope-check and normal CI pass at the actual branch tip after the `20260429T183248Z` fixer.

## Final Readiness Statement

This handoff packet now explicitly includes `c320dafa67733469fac8c60aa1ec3b54d2ef6c97` as implementation scope and `153c1271575ee1ea4256378f560c255254fef2c6a` as test plus packet scope, names the canonical demo-path step advanced by each numbered task, separates the approved shared test edit from the shared `src/qual/cli.py` implementation edit, documents the command smoke-plan behavior, and accounts for the parser/catalog drift fix requested by reviewer packets through `20260429T183248Z`.
