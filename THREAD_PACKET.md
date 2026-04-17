# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (reviewed implementation slice)
- Packet refresh role: `feature-fixer final reviewer-required gate rerun refresh`
- Packet refresh date: `2026-04-17`

## Packet Traceability Note

- This packet refresh is for the active `codex/feat-commands` branch state.
- The relevant implementation remains the command-catalog slice in
  `src/qual/commands/catalog.py` plus the focused shared-test coverage in
  `tests/unit/test_commands_catalog.py`.
- For this re-review, use the reviewer packet as the scope source of truth and
  keep the reviewed implementation pinned to that command-catalog slice unless
  a new feature packet is explicitly generated.
- This refresh records the final feature-fixer verification pass so the
  handoff matches the branch-tip implementation and tests that satisfy the
  reviewer-required fixes.
- The reviewed implementation commit remains pinned to
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; later metadata-only packet
  refreshes do not broaden the implementation scope under review.

## Reviewer-Required Fix Verification

- Reviewer required-fix scope:
  this re-review covers the command-catalog implementation on the current
  branch tip and keeps the scope pinned to `src/qual/commands/catalog.py`
  plus `tests/unit/test_commands_catalog.py`.
- Reviewer required-fix implementation status:
  `command_cli_contract()` now checks that the CLI parser surface resolves to
  the same canonical command order returned by `command_names()` and raises
  `ValueError` if that contract drifts.
- Reviewer required-fix test status:
  focused unit coverage proves canonical-order alignment and rejection of a
  catalog/parser drift mismatch for the CLI contract.
- Milestone 3 tie-back:
  this mapping stays concrete against the roadmap requirement that the CLI
  must still execute the MVP loop while Textual remains disabled.

## Feature-Fixer Validation

- Revalidated against the reviewer packet dated `2026-04-17`.
- Confirmed the required implementation fixes are present on the current
  branch tip.
- Confirmed the command-catalog scope remains limited to one owned command
  file plus one approved shared test file.
- Re-ran focused regression coverage and the required local gates on this
  branch tip:
  - `python -m unittest tests.unit.test_commands_catalog -q`: PASS
  - `make scope-check`: PASS
  - `./quality-format.sh --check`: PASS
  - `./quality-lint.sh`: PASS
  - `./quality-test.sh`: PASS
  - `./typecheck-test.sh`: PASS
  - `make ci`: PASS
- Final feature-fixer revalidation:
  reran the full required gate suite on the current branch tip immediately
  before this metadata refresh so the re-review packet records fresh evidence
  for the reviewer-required demo-path alignment fix.
- Final verification basis:
  the current branch tip already includes the parser-surface drift guard and
  focused alias-substitution regression coverage requested by the reviewer, so
  this refresh records the clean post-fix validation state without broadening
  the reviewed implementation scope.
- Final gate-rerun record:
  this packet refresh now captures the clean post-fix rerun on the current
  branch tip immediately before commit creation on `2026-04-17`.
- Final gate-rerun detail:
  repeated `python -m unittest tests.unit.test_commands_catalog -q`,
  `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`,
  `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed again
  on the branch tip used for this final fixer handoff refresh.
- Feature-fixer refresh note:
  this packet refresh is metadata-only and records that the current branch tip
  already contains the reviewer-required command-catalog contract fix plus the
  parser-surface drift regression coverage.

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
  deterministic, uses the canonical command order, and fails fast if the
  parser surface drifts from the catalog.
- Concrete blocker removal for the canonical demo path: while the CLI remains
  the active operator surface, the engine-first MVP loop cannot be considered
  reliable if the canonical command order can drift away from the declared
  command catalog without failing. This slice removes that blocker by making
  that mismatch fail immediately instead of changing the contract unnoticed.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane / owned paths: `src/qual/commands/**`
- Scope goal: harden the command-catalog contract so the accepted CLI parser
  surface cannot drift away from the canonical catalog without a fast failure,
  while keeping the slice limited to command-catalog validation plus focused
  regression coverage.
- Risk reason: this slice touches the operator-facing CLI command contract and
  an approved shared test file, so the handoff uses the high-risk template even
  though the implementation change stays narrow.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Tighten `command_cli_contract()` so the declared parser surface and
   canonical command order cannot silently diverge.
2. Keep the returned CLI contract deterministic and aligned with
   `command_names()`.
3. Add focused regression coverage for canonical-order alignment and
   parser-surface drift rejection.
4. Refresh the handoff packet so the review scope, shared-file approval basis,
   and canonical demo-path mapping are explicit.

### Early Review Triggers

- Before first edit to any shared-by-approval file.
- Before changing the public command contract asserted by
  `command_cli_contract()`.
- Before broadening scope beyond command-catalog validation and the approved
  shared test.

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence

- Plan complete: recorded by this high-risk kickoff section and the
  implementation scope remained limited to the command-catalog slice.
- First green tests: focused `python -m unittest tests.unit.test_commands_catalog -q`
  passed on the current branch tip before final handoff refresh.
- Before risky/shared file edit: the only shared-file edit in this slice is
  `tests/unit/test_commands_catalog.py`, and its approval basis plus
  `SCOPE_ALLOW_SHARED=1 make scope-check` evidence are recorded below.
- Ready for handoff: all required local gates passed on this branch tip and the
  packet now includes the reviewer-required demo-path mapping and complete
  high-risk kickoff fields.

## Canonical Demo-Path Step Advanced

- Reviewer-required one-line mapping:
  this strengthens the canonical `open project/document` step and the overall
  `continue working` CLI contract by keeping the command surface deterministic
  while Textual remains disabled.
- AGENTS-required explicit step statement: this change makes the canonical
  `open project/document` step and the overall `continue working` CLI contract
  more reliable by keeping the command surface deterministic while Textual
  remains disabled.
- Reviewer-required roadmap tie-back:
  this directly supports the Milestone 3 exit criterion that `CLI can still
  execute the MVP loop while Textual remains disabled` by keeping the command
  catalog aligned with the accepted CLI entrypoints.
- Concrete blocker removed: catalog/parser drift can no longer silently change
  the canonical CLI contract.
- Re-review scope note: this packet refresh exists to make that demo-path-step
  mapping explicit for AGENTS compliance; it does not claim any broader
  implementation change beyond the command-catalog slice already under review.

## Scope Boundary

- This slice stays in `feat-commands` Milestone 3 CLI compatibility contract
  hardening work.
- It only hardens command-catalog contract validation and focused regression
  coverage.
- It is not a broader workflow-surface expansion and it is not a UI-surface
  change.
- It does not add new engine business logic, new command flags, or new UI
  behavior.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Definition of Done for This Slice

- `command_cli_contract()` rejects parser-surface drift instead of silently
  accepting a catalog/parser mismatch.
- The returned CLI contract preserves the canonical command order declared by
  `command_names()`.
- Focused regression coverage proves both canonical-order alignment and
  drift rejection for this command-catalog slice.
- This handoff claims only command-catalog contract hardening for the active
  CLI `open`, `retrieve`, and `patch-review` path; it does not claim broader
  command-surface coverage beyond `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.

## Do Not Spend Time On

- Fancy CLI UX that does not support the MVP loop.
- New command flags that do not help open, retrieve, basket, revise, patch, or save.
- Embedding engine behavior directly in command handlers.

## Lane / Owned Paths

- `src/qual/commands/**`

## Scope Completed

- Hardened the default `command_cli_contract()` validation in
  `src/qual/commands/catalog.py` so it validates the canonical command order
  derived from the CLI parser surface against `command_names()` and fails fast
  when they diverge.
- Kept the returned CLI contract aligned with canonical command ordering by
  reusing the validated canonical names tuple returned by `command_names()`.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py`
  for canonical-order alignment and drift rejection in the CLI contract.
- Reissued the handoff packet so the re-review points at the current
  branch-tip implementation and the actual focused regression evidence.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute
  budget, and the lane size limits.
- The implementation slice stayed limited to one owned command file plus one
  approved shared test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- Approval provenance: this re-review relies on the explicit `Approved exception note`
  carried in the reviewed feature packet for the `feat-commands` command-catalog
  slice, with the branch-local enforcement reference recorded by
  `SCOPE_ALLOW_SHARED=1 make scope-check`.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency
   and parser-surface token alignment against the declared command catalog.
2. Preserved canonical command ordering in the CLI contract by reusing the
   validated canonical names tuple.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for
   canonical-order alignment and drift rejection.
4. Regenerated the handoff packet so the re-review reflects the current
   branch-tip implementation and test evidence without expanding scope.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD_PACKET.md`
- `THREAD.md`

## Commands Run and Outcomes

- `SCOPE_ALLOW_SHARED=1 make scope-check`: PASS
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / Blockers

- Risk: `LOW`
- Blockers: none

## Required Handoff Fields

### Canonical demo-path step advanced

- CLI-first operator path for `open project/document` ->
  `continue working`.
- This command-catalog hardening keeps that CLI contract deterministic and
  rejects catalog/parser drift before the active CLI MVP loop can change
  silently while Textual remains disabled.
- Reviewer-fix refresh note: this field is included explicitly so re-review
  does not have to infer the demo-path step from broader milestone language.

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the
  package/layout migration lands, and keep the engine-first MVP loop
  executable while Textual stays disabled, by keeping the command-catalog
  contract deterministic and drift-resistant.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the
  engine-first MVP loop.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the
  command-catalog surface rejects catalog/parser drift before it can silently
  change the operator contract for the active engine-first MVP loop.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused
  command-catalog test coverage.

### Proposed README.md patch text

- None.

## Scope-check / Ownership Note

- Shared-by-approval edits: `YES`.
- Integrator-locked edits: `NO`.
- Ownership detail: the only non-owned implementation path in this slice is
  the approved shared test `tests/unit/test_commands_catalog.py`.
- Approval reference: the reviewer packet supplied to this fixer run is the
  source of truth and explicitly includes `Approved exception note -
  Approved shared-test exception for tests/unit/test_commands_catalog.py`.
- Approval basis: `THREAD_OWNERSHIP.md` marks
  `tests/unit/test_commands_catalog.py` as `feat-commands` shared-by-approval,
  and `scripts/scope-check.sh` permits that path for `codex/feat-commands*`
  when `SCOPE_ALLOW_SHARED=1` is set.
- Approval-bearing gate evidence: `SCOPE_ALLOW_SHARED=1 make scope-check`
  passed for this re-review refresh so the shared-test exception is recorded
  explicitly in the handoff instead of being implied by the plain gate list.
