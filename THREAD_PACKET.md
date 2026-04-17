# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh commit: `HEAD (this metadata-only fixer commit)`
- Packet refresh role: `feature-fixer reviewer-fix verification refresh`

## Packet Traceability Note

- This packet is intentionally scoped to the reviewed implementation commit
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Later packet-refresh commits are metadata-only for re-review and do not expand
  the reviewed implementation surface.
- Re-review should keep the approval basis on the command-catalog slice below.

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

- This change makes the `open project/document` portion of the canonical demo
  path more real by keeping the CLI command contract deterministic,
  smoke-testable, and drift-resistant for the existing `bootstrap` entrypoint
  while Textual remains disabled.
- Concrete blocker removed: the CLI parser surface can no longer silently drift
  away from the command catalog for `bootstrap` and still present a seemingly
  valid contract; `command_cli_contract()` now raises immediately when the
  parser-exposed token surface diverges from the declared catalog-backed CLI
  entrypoints, including alias-only substitutions that would otherwise preserve
  the same canonical command names.
- Reviewer-fix note: this sentence is the explicit AGENTS plan-alignment
  statement required for re-review.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it
  validates both canonical command order and the declared CLI token surface,
  raising `ValueError` if parser entrypoints drift from the catalog.
- Kept the returned contract aligned with the canonical command order by
  reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py`
  for canonical-order alignment, alias-only token drift rejection, and parser
  surface drift rejection.
- Refreshed the handoff packet so the review scope stays anchored to
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and explicitly states the
  canonical demo-path step, blocker removed, and verified gate rerun status.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute
  budget, and lane size limits. The implementation slice stays limited to one
  owned command file plus one focused approved shared test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`. It
  is the only non-owned implementation path in this handoff.

## Tasks Completed (Numbered)

1. Hardened `command_cli_contract()` to verify canonical-name consistency
   against `command_names()` and fail fast on parser-token drift.
2. Preserved canonical command ordering in the CLI contract by returning the
   validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for
   canonical-order alignment and alias-only parser-surface drift rejection.
4. Regenerated the handoff packet so the review scope matches the reviewed
   implementation slice and explicitly names the canonical demo-path step and
   blocker removed.
5. Re-ran the required local gates at the current branch tip and refreshed this
   packet for re-review.

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
  the current CLI compatibility layer for the `open project/document` demo-path
  step, not a broader workflow capability change.

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
