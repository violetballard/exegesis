# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `current branch tip on codex/feat-commands (includes fb8f9515f7c4156c3a9038e85d1c0f7c73757658 plus this feature-fixer commit)`
- Packet refresh commit: `current feature-fixer implementation-and-packet refresh commit on codex/feat-commands`
- Packet refresh role: `feature-fixer required-fixes coverage and packet retargeting`

## Packet Traceability Note

- The active review target is the actual branch-tip implementation rooted at `fb8f9515f7c4156c3a9038e85d1c0f7c73757658`, which adds normalized `document-open` / `open-document` bootstrap compatibility in `src/qual/commands/catalog.py`.
- This follow-up fixer commit keeps that runtime behavior in scope, adds focused regression coverage for it in `tests/unit/test_commands_catalog.py`, and retargets the handoff text so the review basis matches the real branch tip.
- No docs-only traceability claim is being made for `fb8f9515f7c4156c3a9038e85d1c0f7c73757658`; it is implementation scope.

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

- Exact CLI-first MVP steps strengthened:
  - `open project/document`
  - `retrieve relevant material`
  - `preview and apply or reject a patch`
- Primary step advanced by the branch-tip alias work: `open project/document`.
- Supporting contract steps kept deterministic by the existing command-catalog checks: `retrieve relevant material` and `preview and apply or reject a patch`.
- Concrete blockers removed:
  - `document-open` / `open-document` now resolve back onto the canonical `bootstrap` parser entrypoint instead of drifting into an unrecognized or divergent document-open surface.
  - Parser-facing canonical command order and accepted CLI entrypoints remain locked to the declared catalog so parser/catalog drift fails fast instead of silently changing the operator contract.
- Scope boundary: this slice stays in command-catalog compatibility, resolution, and regression coverage. It does not add new commands, add new flags, widen the MVP loop, or embed engine behavior in handlers.

## Scope-Tightening Note

- This is not general CLI cleanup. It is a narrow CLI compatibility and command-catalog hardening slice for the existing MVP command loop.
- This remains Milestone 3 CLI compatibility work while Textual stays disabled.
- It does not add new commands, new handler logic, or new workflow steps. It only preserves and normalizes the existing operator-facing command surface.

## Ready for Handoff

- This work now makes the canonical Milestone 3 CLI path more real because the active `open project/document` command aliases normalize back to the canonical bootstrap route, while the parser-facing command contract still rejects catalog drift before it can silently alter retrieval or patch-review routing.
- Pre-handoff alignment statement: this is CLI compatibility and demo-path contract work for the active MVP loop, not standalone infra cleanup.

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
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for the document-open alias normalization and the stricter CLI contract drift checks.
- Retargeted the handoff packet so the claimed review scope, demo-path mapping, and traceability note match the actual branch tip.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap and remained limited to one lane-owned command file plus one approved shared test file.
- Runtime implementation stays within `src/qual/commands/**`; the only non-owned implementation path is the approved shared test.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Tasks Completed

1. `open project/document`: normalized `document-open` and `open-document` so those document-open compatibility aliases resolve through the canonical `bootstrap` entrypoint instead of creating a divergent command surface.
2. `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch`: kept the parser-facing CLI contract deterministic by validating declared entrypoints and canonical command ordering against the catalog.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for alias normalization and CLI contract drift rejection at the actual branch tip.
4. Refreshed the handoff packet and compatibility summary so the review scope explicitly matches the real implementation under review.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Handoff alignment files

- `THREAD.md`
- `THREAD_PACKET.md`

## Commands Run and Outcomes

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
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the current engine-first MVP loop, specifically by preventing parser/catalog drift and by keeping document-open compatibility aliases routed through the canonical bootstrap command surface.

### Vision capability affected

- Canonical engine contract - the operator-facing CLI contract for `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch` now keeps document-open compatibility aliases on the canonical bootstrap route and fails fast when parser drift would otherwise silently change the command surface.
- Auditable state and workflow - catalog/parser consistency and deterministic alias normalization make the active CLI contract explicit and traceable instead of depending on implicit ordering or untracked alias behavior.

### Routing/provider impact note

- None. This branch only affects local command-catalog validation, alias normalization, and focused regression coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: runtime edits stay in lane-owned `src/qual/commands/**`, and the only non-owned implementation path is the approved shared test `tests/unit/test_commands_catalog.py`.
