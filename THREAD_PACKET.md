# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `feature-fixer reviewer-required re-review refresh`

## Packet Traceability Note

- The current branch tip is a metadata-only fixer refresh commit on top of
  later lane work already present on `codex/feat-commands`.
- Review the command-catalog implementation at
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- For this re-review, use the reviewer packet as the scope source of truth and
  keep the reviewed implementation pinned to that command-catalog slice unless
  a new feature packet is explicitly generated.
- This packet refresh corrects the handoff metadata only; it does not expand
  the requested re-review scope beyond the command-catalog slice above.

## Reviewer-Required Fix Verification

- Reviewer required-fix scope:
  this re-review refresh is limited to the handoff metadata fix requested in
  the reviewer packet, and it keeps the reviewed implementation scope pinned
  to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` without any feature-scope
  expansion.
- Reviewer required-fix satisfied in handoff metadata:
  this packet now states exactly which canonical demo-path steps the reviewed
  command-catalog slice makes more reliable.
- Milestone 3 tie-back:
  this mapping is stated concretely against the roadmap requirement that the
  CLI must still execute the MVP loop while Textual remains disabled.

## Feature-Fixer Validation

- Revalidated against the reviewer packet dated `2026-04-17`.
- Confirmed the reviewed implementation scope remains pinned to
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Confirmed the reviewer-required implementation fixes are already present on
  this branch and that this commit only refreshes the handoff contract for
  re-review.
- Re-ran the required local gates on this metadata-refresh branch tip:
  - `make scope-check`: PASS
  - `./quality-format.sh --check`: PASS
  - `./quality-lint.sh`: PASS
  - `./quality-test.sh`: PASS
  - `./typecheck-test.sh`: PASS
  - `make ci`: PASS

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
  reliable if `open`, `retrieve`, or `patch-review` entrypoints can silently
  drift away from the declared command catalog. This slice removes that
  blocker by making parser/catalog drift fail immediately instead of changing
  the operator contract unnoticed.

## Canonical Demo-Path Step Advanced

- AGENTS-required explicit step statement: this change makes the canonical
  CLI demo-path steps `open project/document`, `retrieve relevant material`,
  and `preview and apply or reject a patch` more reliable, and it directly
  protects the ongoing CLI operator path that must remain executable while
  Textual stays disabled, by keeping the parser-facing command surface
  deterministic and drift-resistant.
- Reviewer-required roadmap tie-back:
  this directly supports the Milestone 3 exit criterion that `CLI can still
  execute the MVP loop while Textual remains disabled` by keeping the command
  catalog aligned with the accepted CLI entrypoints for those operator-facing
  steps.
- Concrete step protection:
  `bootstrap` protects the `open project/document` entrypoint,
  `context-basket` protects the `retrieve relevant material` entrypoint, and
  `diff-preview` protects the `preview and apply or reject a patch`
  entrypoint.
- Concrete blocker removed: parser/catalog drift can no longer silently
  reorder or desynchronize those operator-facing CLI entrypoints from the
  canonical command catalog.
- Re-review scope note: this packet refresh exists to make that demo-path-step
  mapping explicit for AGENTS compliance; it does not claim any broader
  implementation change beyond the command-catalog slice already under review.

## Scope Boundary

- This slice stays in `feat-commands` Milestone 3 CLI compatibility work.
- It only hardens command-catalog contract validation and focused regression
  coverage.
- It does not add new engine business logic, new command flags, or new UI
  behavior.

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

- Hardened the default `command_cli_contract()` validation in
  `src/qual/commands/catalog.py` so it rejects parser-surface drift against the
  declared command catalog, not just canonical-name mismatch.
- Kept the returned CLI contract aligned with canonical command ordering while
  also rejecting alias substitution, reordered accepted entrypoints, removed
  primary tokens, and extra accepted entrypoints in the default parser surface.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py`
  for parser-surface drift cases that preserve canonical command order but must
  still fail fast.
- Reissued the handoff packet as a command-catalog-only slice so the review
  scope matches the claimed implementation files and approval basis.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute
  budget, and the lane size limits.
- The implementation slice stayed limited to one owned command file plus one
  approved shared test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency
   and reject default parser-surface drift against the declared command
   catalog.
2. Preserved canonical command ordering in the CLI contract while rejecting
   alias substitution, primary-token loss, entrypoint reordering, and extra
   accepted entrypoints.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for
   parser-surface drift that still preserves canonical command order.
4. Regenerated the handoff packet so the branch metadata stays scoped to the
   command-catalog slice and uses the current roadmap and vision labels.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD_PACKET.md`
- `THREAD.md`

## Commands Run and Outcomes

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

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the
  package/layout migration lands, and keep the engine-first MVP loop
  executable while Textual stays disabled, by keeping the command-catalog
  contract deterministic and drift-resistant.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the
  engine-first MVP loop, specifically the operator-facing `open`,
  `retrieve`, and `patch-review` command path.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the
  command-catalog surface rejects parser-surface drift before it can silently
  change the operator contract for the active engine-first MVP loop.
- Auditable state and workflow - the command surface now fails loudly on
  catalog/parser drift, making the operator-facing contract explicit and
  traceable while the CLI remains the active surface.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused
  command-catalog test coverage.

## Scope-check / Ownership Note

- Shared-by-approval edits: `YES`.
- Integrator-locked edits: `NO`.
- Ownership detail: the only non-owned implementation path in this slice is
  the approved shared test `tests/unit/test_commands_catalog.py`.
