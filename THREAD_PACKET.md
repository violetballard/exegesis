# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: branch tip after fixer prompt `20260429T041242Z`
- Review basis: branch tip after this fixer commit, not `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` alone.
- Prior implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: reviewer-fix handoff correction after prompt `20260429T041242Z`

## Packet Traceability Note

- Fixer prompt `20260429T035831Z` requested reviewer-required fixes for exact parser-token validation, same-canonical drift coverage, canonical demo-path handoff mapping, and gate reruns.
- Fixer prompt `20260429T040101Z` requested a metadata-only handoff refresh so every completed task names the canonical demo-path step it supports and states the concrete blocker removed by the command-catalog work.
- Fixer prompt `20260429T040347Z` requested the same reviewer-required fixes against the actual branch tip, including current review-basis accounting, exact parser-surface validation, same-canonical drift coverage, demo-path mapping, gate reruns, and a new commit.
- Fixer prompt `20260429T040701Z` requested the reviewer-required fixes again with emphasis on full parser-surface drift rejection, regression coverage for extra/missing/substituted/ordered same-canonical drift, exact review-basis accounting, and complete metadata file listing.
- Fixer prompt `20260429T040923Z` requested the same reviewer-required fixes against the current branch tip and requires a new commit with refreshed gate evidence.
- Fixer prompt `20260429T041242Z` requested the same reviewer-required fixes against the current branch tip and requires a new commit with refreshed gate evidence.
- The reviewable branch-tip implementation is narrowed to the command-catalog slice:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- `scripts/scope-check.sh` had drifted after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this fixer restores it to the submitted baseline so it is no longer a branch-tip implementation change.
- `THREAD.md` and `THREAD_PACKET.md` are metadata-only handoff files.

## Branch-Tip Review Basis

- Review target: branch tip after fixer prompt `20260429T041242Z`.
- Prior implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Review range: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`.
- Matching changed-file scope:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
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
- Added regression coverage for same-canonical drift, unexpected extra accepted aliases, removed expected tokens, token replacement, lookup-table substitution including same-name-set mapping drift, lookup-table ordering drift, and declared-surface drift.
- Narrowed the branch-tip implementation basis by restoring unrelated `scripts/scope-check.sh` drift to baseline.
- Regenerated `THREAD.md` and `THREAD_PACKET.md` so the review packet names the actual branch-tip basis and required-fix satisfaction.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap.
- Size stayed within limits: implementation remains one lane-owned command file plus one approved shared test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- No integrator-locked files are changed.

## Tasks Completed

1. Hardened the CLI contract against full parser-surface drift in `src/qual/commands/catalog.py`; demo-path step supported: stable CLI entrypoints for `open project/document`, `retrieve relevant material`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `persist/export the updated state`.
2. Added focused tests in `tests/unit/test_commands_catalog.py` for same-canonical drift, missing expected tokens, extra accepted aliases, lookup-table ordering drift, lookup-table substitutions that preserve the canonical-name set, and declared-surface drift; demo-path step supported: repeatable CLI smoke coverage for the same open, retrieve/basket, patch-review, and export command surfaces.
3. Narrowed the branch-tip review basis by restoring unrelated `scripts/scope-check.sh` drift to baseline and documenting only the remaining command-catalog implementation files; demo-path step supported: keeping the `feat-commands` lane focused on command-surface compatibility instead of unrelated scope policy work.
4. Regenerated the handoff packet with canonical demo-path mapping, complete metadata-only file accounting, and reran all required gates; demo-path step supported: auditable Milestone 3 CLI compatibility for the engine-first workflow loop.

## Canonical Demo-Path Mapping

1. CLI parser-surface hardening advances `open project/document`, `retrieve`, `basket`, `revise`, `patch apply/reject`, and `save/export` by keeping the operator command entrypoints stable while Textual remains disabled.
2. Drift regression tests make the CLI smoke surface more reliable for the same demo-path steps, especially `open`, `retrieve/basket`, and `patch review`.
3. Branch narrowing keeps this lane focused on the command-surface compatibility step and avoids mixing scope-check policy work into the MVP demo path.
4. Packet regeneration makes the `feat-commands` handoff auditable for Milestone 3 CLI compatibility.

## Demo-Path Step Made More Real

- The CLI-first command surface for the engine loop is more real: the accepted parser tokens for project open, retrieval/basket, patch review, and export handoff now fail loudly if they drift from the canonical command catalog.

## Concrete Blocker Removed

- This removes the blocker where parser drift could silently change the CLI operator surface before Textual is enabled, which would make the Milestone 3 demo path unreliable to smoke-test through commands.

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

## Required Fixes Addressed From Fixer Prompt `20260429T035831Z`

1. Validated the full accepted parser token surface against the canonical CLI command surface instead of only checking deduplicated canonical names.
2. Added focused tests for same-canonical parser drift, including removed `diff`, added `open`, `diff_preview` replacement, lookup-table mapping drift that preserves the canonical-name set, and declared-surface drift.
3. Regenerated the handoff packet with explicit canonical demo-path mapping for each completed task and a direct statement of which demo-path step is more real.
4. Reran all required gates after the parser-surface, test, and handoff-packet fixes.

## Required Fixes Addressed From Fixer Prompt `20260429T040101Z`

1. Refreshed the handoff packet to name the exact canonical demo-path steps advanced by the command-catalog contract work.
2. Updated each completed task line to include the demo-path step it supports.
3. Added a concise concrete-blocker statement explaining why this is not speculative second-order hardening.
4. This is a metadata-only handoff refresh after prompt `20260429T040101Z`; no implementation files changed after the already-reviewed command-catalog slice, and the required gates were rerun below.

## Required Fixes Addressed From Fixer Prompt `20260429T040347Z`

1. Regenerated this handoff packet against the actual intended branch-tip review target after prompt `20260429T040347Z`.
2. Listed all implementation/test/metadata files changed since `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, with `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` as the reviewable implementation/test slice.
3. Preserved the hardened `command_cli_contract()` behavior that validates exact accepted parser tokens, lookup table, grouped canonical surface, declared surface, and canonical command order.
4. Preserved regression coverage for same-canonical parser drift: removed accepted token, added same-canonical alias, replacement alias such as `diff_preview`, lookup-table substitution with the same canonical-name set, and declared-surface drift.
5. Retained the canonical demo-path mapping and explicit statement that the CLI-first command surface for project open, retrieval/basket, patch review, and export handoff is now more reliable to smoke-test.
6. Reran all required gates after this packet refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T040701Z`

1. Confirmed `command_cli_contract()` validates exact accepted parser tokens, lookup table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
2. Confirmed regression coverage includes extra known alias drift, missing alias/token drift, substituted same-canonical aliases, parser token ordering drift, lookup-table ordering drift, and declared-surface ordering drift.
3. Regenerated this handoff packet against the current branch-tip review target after prompt `20260429T040701Z`, with `THREAD.md` and `THREAD_PACKET.md` listed as metadata-only files.
4. Kept scope narrowed to `src/qual/commands/**` plus the approved shared test file `tests/unit/test_commands_catalog.py`; no additional shared-path exception is needed.

## Required Fixes Addressed From Fixer Prompt `20260429T040923Z`

1. Confirmed the branch-tip `command_cli_contract()` validates the exact parser surface, including accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
2. Confirmed focused regression coverage remains in `tests/unit/test_commands_catalog.py` for added known aliases, removed tokens, replacement aliases, lookup-table substitutions that preserve the canonical-name set, parser token ordering drift, and declared-surface drift.
3. Refreshed `THREAD.md` and this packet so the reviewer can evaluate the current branch tip after prompt `20260429T040923Z` instead of the earlier implementation anchor alone.
4. Retained the canonical demo-path mapping and concrete-blocker statement: the CLI-first parser surface for project open, retrieval/basket, patch review, and export handoff now fails loudly if it drifts before Textual is enabled.
5. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T041242Z`

1. Confirmed the branch-tip `command_cli_contract()` validates accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
2. Added an explicitly named regression for declared missing accepted-alias drift and preserved coverage for extra known aliases, removed tokens, substituted aliases, parser token ordering drift, lookup-table ordering drift, and declared-surface drift.
3. Refreshed `THREAD.md` and this packet so the reviewer can evaluate the current branch tip after prompt `20260429T041242Z`.
4. Retained complete branch-tip accounting: implementation files are `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; metadata-only files are `THREAD.md` and `THREAD_PACKET.md`.
5. Retained the canonical demo-path mapping and concrete-blocker statement: the CLI-first parser surface for project open, retrieval/basket, patch review, and export handoff now fails loudly if it drifts before Textual is enabled.
6. Reran all required gates after this refresh and recorded the outcomes below.

## Commands Run + Outcomes

- `python -m pytest tests/unit/test_commands_catalog.py`: NOT RUN; `pytest` is not installed in this environment.
- `python -m unittest tests.unit.test_commands_catalog`: PASS; ran 72 command-catalog tests.
- `make scope-check`: PASS for branch `codex/feat-commands`.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS; ran smoke tests and 154 unit tests, including full command-catalog parser-surface drift coverage.
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
