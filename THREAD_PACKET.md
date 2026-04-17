# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `c99d67784cad542251317b5fd910837ff904d295`
- Packet refresh commit: `metadata-only packet refresh on the branch tip after this update`
- Packet refresh role: `feature-fixer required-fixes parser-surface coverage and packet retargeting`

## Packet Traceability Note

- The active review target is the branch-tip implementation at `c99d67784cad542251317b5fd910837ff904d295`, which keeps the CLI parser surface locked to the declared command catalog and adds regression coverage for parser-surface drift in `tests/unit/test_commands_catalog.py`.
- This packet refresh is metadata-only. It does not change the implementation under review; it only aligns the handoff text with the actual branch-tip runtime scope and the reviewer-fix status.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Keep the CLI-first MVP command surface deterministic and migration-safe by preserving canonical parser/catalog alignment while normalizing document-open bootstrap aliases back onto the existing `bootstrap` entrypoint.

## Canonical Demo-Path Step Advanced

- Exact canonical demo-path step advanced: `open project/document`.
- Concrete blocker removed: `document-open` / `open-document` now resolve back onto the canonical `bootstrap` parser entrypoint instead of drifting into an unrecognized or divergent document-open surface.
- Contract guard for that same step: parser-facing canonical command order and accepted CLI entrypoints remain locked to the declared catalog so parser/catalog drift fails fast instead of silently changing the active CLI open-command surface.
- Scope boundary: this slice stays in command-catalog compatibility, resolution, and regression coverage for the existing open-command surface. It does not add new commands, add new flags, widen the MVP loop, or embed engine behavior in handlers.

## Scope-Tightening Note

- This is not general CLI cleanup. It is a narrow CLI compatibility and command-catalog hardening slice for the existing MVP command loop.
- This remains Milestone 3 CLI compatibility work while Textual stays disabled.
- It does not add new commands, new handler logic, or new workflow steps. It only preserves and normalizes the existing operator-facing command surface.

## Ready for Handoff

- This work now makes the canonical Milestone 3 CLI path more real because the active `open project/document` aliases normalize back to the canonical bootstrap route and fail fast if the parser surface drifts from the declared catalog.
- Pre-handoff alignment statement: this is narrow CLI compatibility work for the `open project/document` step of the active MVP loop, not standalone infra cleanup.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Definition of Done for This Lane

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

- Normalized `document-open` and `open-document` back onto the canonical `bootstrap` command path in `src/qual/commands/catalog.py` so document-open compatibility stays routed through the existing project-open parser entrypoint.
- Kept the parser-facing CLI contract deterministic by validating declared entrypoints and canonical names against the command catalog instead of allowing silent parser/catalog drift.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for the document-open alias normalization and the stricter CLI contract drift checks, including token-level parser drift cases for reordered accepted entrypoints, missing expected aliases, and `diff` versus `diff_preview` substitution.
- Refreshed the handoff packet so the claimed review scope, demo-path mapping, and traceability note match the actual branch-tip implementation that satisfies the reviewer's numbered fixes.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap and remained limited to one lane-owned command file plus one approved shared test file.
- Runtime implementation stays within `src/qual/commands/**`; the only non-owned implementation path is the approved shared test.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Tasks Completed

1. `open project/document`: normalized `document-open` and `open-document` so those document-open compatibility aliases resolve through the canonical `bootstrap` entrypoint instead of creating a divergent command surface.
2. `open project/document`: kept the parser-facing CLI contract deterministic by validating declared entrypoints and canonical command ordering against the catalog so the active open-command surface cannot drift silently.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for alias normalization and CLI contract drift rejection at the actual branch tip, including reordered accepted entrypoints, missing expected alias tokens, and normalized alias substitution drift.
4. Refreshed the handoff packet and compatibility summary so the review scope explicitly matches the real implementation under review.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Handoff alignment files

- `THREAD.md`
- `THREAD_PACKET.md`

## Commands Run and Outcomes

- Final post-fix gate rerun completed during the feature-fixer pass against the current branch tip carrying the parser-surface fixes from `c99d67784cad542251317b5fd910837ff904d295`; the final HEAD SHA for this follow-up packet commit is reported separately after commit.
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / Blockers

- Residual risk: low. Future intentional CLI parser or alias changes still need matching catalog and regression-test updates or the contract checks will fail fast by design.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the existing CLI route for `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch` deterministic while Textual remains disabled.
- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the existing CLI route for `open project/document` deterministic while Textual remains disabled.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the current engine-first MVP loop, specifically by keeping document-open compatibility aliases routed through the canonical bootstrap command surface and by preventing the open-command parser/catalog contract from drifting silently.

### Vision capability affected

- Canonical engine contract - the operator-facing CLI contract for `open project/document` now keeps document-open compatibility aliases on the canonical bootstrap route and fails fast when parser drift would otherwise silently change that command surface.
- Auditable state and workflow - catalog/parser consistency and deterministic alias normalization make the active CLI contract explicit and traceable instead of depending on implicit ordering or untracked alias behavior.

### Routing/provider impact note

- None. This branch only affects local command-catalog validation, alias normalization, and focused regression coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: runtime edits stay in lane-owned `src/qual/commands/**`, and the only non-owned implementation path is the approved shared test `tests/unit/test_commands_catalog.py`.
