# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `d38078e4ccc4ba33f7acacf9eee38443d40842a4`
- Packet refresh role: `feature-fixer reviewer-required re-review refresh`

## Packet Traceability Note

- This packet refresh is for the current `codex/feat-commands` branch tip.
- The relevant implementation remains the command-catalog slice in
  `src/qual/commands/catalog.py` plus the focused shared-test coverage in
  `tests/unit/test_commands_catalog.py`.
- For this re-review, use the reviewer packet as the scope source of truth and
  keep the reviewed implementation pinned to that command-catalog slice unless
  a new feature packet is explicitly generated.
- This refresh corrects the handoff so it matches the branch-tip
  implementation and tests that now satisfy the reviewer-required fixes.

## Reviewer-Required Fix Verification

- Reviewer required-fix scope:
  this re-review covers the command-catalog implementation on the current
  branch tip and keeps the scope pinned to `src/qual/commands/catalog.py`
  plus `tests/unit/test_commands_catalog.py`.
- Reviewer required-fix implementation status:
  `command_cli_contract()` now validates the declared parser token surface, not
  only the deduplicated canonical-name projection, and rejects parser-surface
  drift when accepted entrypoints are replaced, reordered, removed, or
  expanded.
- Reviewer required-fix test status:
  focused unit coverage now patches the parser-entrypoint validation path to
  prove rejection for alias substitution, parser reorder, removed expected
  entrypoints, and extra accepted entrypoint drift.
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
  reliable if the canonical command order for the `open`, `retrieve`, and
  `patch-review` operator path can drift away from the declared command
  catalog without failing. This slice removes that blocker by making
  parser-surface drift fail immediately instead of changing the contract
  unnoticed.

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
- Concrete blocker removed: parser-surface drift can no longer silently
  reorder or desynchronize those operator-facing CLI entrypoints from the
  canonical command catalog.
- Token-level protection detail: the contract now rejects parser-surface drift
  when canonical entrypoints are replaced, removed, or reordered, even if the
  affected aliases still resolve back to the same canonical command names.
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
  accepting a parser/catalog mismatch.
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
  `src/qual/commands/catalog.py` so it validates the parser surface at the
  token level against the declared CLI entrypoints and fails fast when they
  diverge.
- Kept the returned CLI contract aligned with canonical command ordering by
  deriving the canonical command sequence from the validated declared
  entrypoints instead of rebuilding a weaker projection from the lookup table.
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

### Routing/provider impact note

- None. This change only affects local command contract validation and focused
  command-catalog test coverage.

## Scope-check / Ownership Note

- Shared-by-approval edits: `YES`.
- Integrator-locked edits: `NO`.
- Ownership detail: the only non-owned implementation path in this slice is
  the approved shared test `tests/unit/test_commands_catalog.py`.
- Approval basis: `THREAD_OWNERSHIP.md` marks
  `tests/unit/test_commands_catalog.py` as `feat-commands` shared-by-approval,
  and `scripts/scope-check.sh` permits that path for `codex/feat-commands*`
  when `SCOPE_ALLOW_SHARED=1` is set.
- Approval-bearing gate evidence: `SCOPE_ALLOW_SHARED=1 make scope-check`
  passed for this re-review refresh so the shared-test exception is recorded
  explicitly in the handoff instead of being implied by the plain gate list.
