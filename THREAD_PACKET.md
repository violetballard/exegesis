# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: branch tip after fixer prompt `20260429T035558Z`
- Review basis: branch tip after this fixer commit, not `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` alone.
- Prior implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: reviewer-fix implementation and handoff correction

## Packet Traceability Note

- Fixer prompt `20260429T035558Z` requested reviewer-required fixes for exact parser-token validation, same-canonical drift coverage, complete metadata file accounting, and gate reruns.
- The reviewable branch-tip implementation is narrowed to the command-catalog slice:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- `scripts/scope-check.sh` had drifted after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this fixer restores it to the submitted baseline so it is no longer a branch-tip implementation change.
- `THREAD.md` and `THREAD_PACKET.md` are metadata-only handoff files.

## Branch-Tip Review Basis

- Review target: branch tip after fixer prompt `20260429T035558Z`.
- Prior implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Review range: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`.
- Matching `git diff --stat` scope:
  - `THREAD.md` - 50 changed lines
  - `THREAD_PACKET.md` - 199 changed lines
  - `src/qual/commands/catalog.py` - 135 changed lines
  - `tests/unit/test_commands_catalog.py` - 340 changed lines
  - Total: 4 files changed, 655 insertions(+), 69 deletions(-)
- Branch-tip implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Branch-tip metadata-only files:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser token surface drifts from the catalog.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Definition Of Done For This Lane

- Core engine actions are reachable through stable commands.
- Command behavior is deterministic and smoke-testable.
- Compatibility shims keep old command surfaces working where required.
- Command handlers stay thin and delegate real behavior to engine code.

## Do Not Spend Time On

- Fancy CLI UX that does not support the MVP loop.
- New command flags that do not help open, retrieve, basket, revise, patch, or save.
- Embedding engine behavior directly in command handlers.

## Lane / Owned Paths

- `src/qual/commands/**`

## Scope Completed

- Strengthened `command_cli_contract()` so it validates the full parser token surface, lookup table, grouped canonical surface, and canonical name order against the declared canonical CLI command surface.
- Added regression coverage for same-canonical drift, unexpected extra accepted aliases, removed expected tokens, token replacement, lookup-table substitution, and declared-surface drift.
- Narrowed the branch-tip implementation basis by restoring unrelated `scripts/scope-check.sh` drift to baseline.
- Regenerated `THREAD.md` and `THREAD_PACKET.md` so the review packet names the actual branch-tip basis and required-fix satisfaction.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap.
- Size stayed within limits: implementation remains one lane-owned command file plus one approved shared test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- No integrator-locked files are changed.

## Tasks Completed

1. Hardened the CLI contract against full parser-surface drift in `src/qual/commands/catalog.py`.
2. Added focused tests in `tests/unit/test_commands_catalog.py` for same-canonical drift, missing expected tokens, extra accepted aliases, and lookup-table/declared-surface drift.
3. Narrowed the branch-tip review basis by restoring unrelated `scripts/scope-check.sh` drift to baseline and documenting only the remaining command-catalog implementation files.
4. Regenerated the handoff packet with canonical demo-path mapping, complete metadata-only file accounting, and reran all required gates.

## Canonical Demo-Path Mapping

1. CLI parser-surface hardening advances `open project/document`, `retrieve`, `basket`, `revise`, `patch apply/reject`, and `save/export` by keeping the operator command entrypoints stable while Textual remains disabled.
2. Drift regression tests make the CLI smoke surface more reliable for the same demo-path steps, especially `open`, `retrieve/basket`, and `patch review`.
3. Branch narrowing keeps this lane focused on the command-surface compatibility step and avoids mixing scope-check policy work into the MVP demo path.
4. Packet regeneration makes the `feat-commands` handoff auditable for Milestone 3 CLI compatibility.

## Demo-Path Step Made More Real

- The CLI-first command surface for the engine loop is more real: the accepted parser tokens for project open, retrieval/basket, patch review, and export handoff now fail loudly if they drift from the canonical command catalog.

## Files Changed

### Reviewed Implementation Files

- `src/qual/commands/catalog.py` - lane-owned implementation file.
- `tests/unit/test_commands_catalog.py` - approved shared test file.

### Baseline Restoration

- `scripts/scope-check.sh` - restored to the submitted baseline so it is not part of the branch-tip implementation diff.

### Metadata-Only Handoff Files

- `THREAD.md`
- `THREAD_PACKET.md`

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/catalog.py`.
- Shared-by-approval implementation/test edits: `tests/unit/test_commands_catalog.py` under the approved shared-test exception.
- Integrator-locked edits: none.
- Metadata-only handoff edits: `THREAD.md`, `THREAD_PACKET.md`.
- Shared/integrator-locked edits: `YES` only because the approved shared-test exception touches `tests/unit/test_commands_catalog.py`; no integrator-locked files are edited.

## Required Fixes Addressed From Fixer Prompt `20260429T035558Z`

1. Validated the full accepted parser token surface against the canonical CLI command surface instead of only checking deduplicated canonical names.
2. Added focused tests for same-canonical parser drift, including extra aliases, removed expected tokens, token replacement, lookup-table drift, and declared-surface drift.
3. Regenerated the handoff packet so the files changed list includes the implementation files plus both metadata files: `THREAD.md` and `THREAD_PACKET.md`.
4. Reran all required gates after the parser-surface, test, and packet-accounting fixes.

## Commands Run + Outcomes

- `make scope-check`: PASS for branch `codex/feat-commands`.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS; ran smoke tests and 152 unit tests, including full command-catalog parser-surface drift coverage.
- `./typecheck-test.sh`: PASS; compiled Python sources in `src/`.
- `make ci`: PASS; ran scope-check, format, lint, compileall/typecheck, and full quality tests.

## Risks / Blockers

- Risk: `HIGH`.
- Blockers: none.

## Required Handoff Fields

### Branch Name

- `codex/feat-commands`

### Roadmap Item(s) Affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision Capability Affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract.
- Auditable state and workflow - the command surface fails loudly on catalog/parser drift, making the operator-facing contract explicit and traceable.

### Routing / Provider Impact Note

- None. This change only affects local command contract validation and focused command-catalog test coverage.
