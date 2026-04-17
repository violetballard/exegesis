# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh commit: `HEAD (feature-fixer required-fix metadata refresh)`
- Packet refresh role: `feature-fixer reviewer-required-fix metadata refresh`

## Packet Traceability Note

- This packet is intentionally scoped to the reviewed implementation commit
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Later packet-refresh commits are metadata-only for re-review and do not expand
  the reviewed implementation surface.
- Re-review should keep the approval basis on the command-catalog slice below.
- Latest metadata refresh prepared at: `2026-04-17T14:17:16Z`

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any
  Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI command contract so `command_cli_contract()` stays
  deterministic, uses the canonical command order, and fails fast if the parser
  surface drifts from the catalog.

## Canonical Demo-Path Step Advanced

- This change hardens the CLI-facing portions of the canonical demo path while
  Textual remains disabled:
  `open project/document` via `bootstrap`,
  `retrieve relevant material` and `promote or gather context into the basket`
  via `context-basket`,
  `preview and apply or reject a patch` via `diff-preview`,
  and `continue working` / handoff persistence through `terminal`.
- Concrete blocker removed: the CLI parser surface can no longer silently drift
  away from the command catalog's canonical ordering and still present a
  seemingly valid contract to those MVP-loop entrypoints;
  `command_cli_contract()` now raises immediately when the CLI lookup table
  yields canonical command names that no longer match `command_names()`,
  instead of silently returning a reordered or truncated contract to the CLI
  compatibility layer.
- Scope-tightening note: this is command-surface hardening for the existing
  MVP-loop entrypoints only; it does not claim new workflow behavior beyond
  keeping the current CLI contract deterministic and smoke-testable.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it
  validates canonical command order against `command_names()`, raising
  `ValueError` if the CLI lookup table drifts from the catalog's canonical
  names.
- Kept the returned contract aligned with the canonical command order by
  reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py`
  for canonical-order alignment and canonical-name drift rejection.
- Refreshed the handoff packet so the review scope stays anchored to
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and explicitly states the
  CLI-facing canonical demo-path steps, blocker removed, and verified gate
  rerun status.
- Refreshed this packet again for the current fixer rerun so the branch tip has
  a dedicated metadata-only re-review commit without changing the reviewed
  implementation files.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute
  budget, and lane size limits. The implementation slice stays limited to one
  owned command file plus one focused approved shared test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`. It
  is the only non-owned implementation path in this handoff.

## Tasks Completed (Numbered)

1. Hardened `command_cli_contract()` to verify canonical-name consistency
   against `command_names()` and fail fast on canonical-name drift.
2. Preserved canonical command ordering in the CLI contract by returning the
   validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for
   canonical-order alignment and canonical-name drift rejection.
4. Regenerated the handoff packet so the review scope matches the reviewed
   implementation slice and explicitly names the CLI-facing canonical
   demo-path steps and blocker removed.
5. Re-ran the required local gates at the current branch tip and refreshed this
   packet for re-review with the current required-fix metadata timestamp.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD.md`
- `THREAD_PACKET.md`

## Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`
- Re-verification point: `2026-04-17T14:17:16Z` at the current branch tip

## Risks / Blockers

- Risk: `LOW`
- Remaining risk: none beyond normal merge sequencing for a narrow
  command-catalog change.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the
  package/layout migration lands by keeping the command surface deterministic
  and smoke-testable.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the
  engine-first MVP loop.
- Scope-tightening note: this packet only claims command-surface determinism for
  the current CLI compatibility layer covering `bootstrap`,
  `context-basket`, `diff-preview`, and `terminal` in the active MVP loop, not
  a broader workflow capability change.

### Vision capability affected

- Canonical engine contract - the CLI compatibility surface stays stable and
  smoke-testable while Textual remains disabled.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused
  command-catalog test coverage.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: the only non-owned implementation path is the approved
  shared test `tests/unit/test_commands_catalog.py`.
