# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `ea00422c0b9c21e4bb0a3774abbad8a06facec62`
- Packet refresh commit: `ea00422c0b9c21e4bb0a3774abbad8a06facec62` (implementation tip before this final feature-fixer handoff refresh)
- Packet refresh role: `feature-fixer reviewer-required final gate-verified handoff refresh`

## Packet Traceability Note

- The original reviewer packet pointed at
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, but this branch now contains the
  required command-catalog fixes through implementation tip
  `ea00422c0b9c21e4bb0a3774abbad8a06facec62`. Treat this feature-fixer refresh
  as the current handoff authority for that implementation slice plus the final
  in-worktree command-surface alignment captured in this commit.
- Final reviewer-fix metadata refresh on `2026-04-17`: this handoff reasserts
  the AGENTS-required canonical demo-path mapping requested by review and keeps
  the claimed scope narrowed to Milestone 3 CLI-contract hardening only.

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
  deterministic for the current CLI-first MVP path only and fails fast if the
  accepted CLI surface drifts from the catalog-backed command specs.

## Canonical Demo-Path Step Advanced

- Explicit AGENTS.md handoff field: this packet states exactly which canonical
  demo-path steps this slice advances before handoff.
- This work explicitly advances the canonical demo path by making the CLI-first
  `project-open`, `retrieval`, `patch-review`, and `export-handoff` steps more
  real and smoke-testable.
- `project-open`: this slice keeps the `bootstrap` CLI entrypoint callable and
  smoke-testable while Textual remains disabled.
- `retrieval`: this slice keeps the `context-basket` CLI entrypoint pinned to
  the catalog-backed parser surface so retrieval-facing smoke routes cannot
  drift silently.
- `patch-review`: this slice keeps the `diff-preview` and `diff` CLI
  entrypoints pinned to the catalog-backed parser surface so patch-review
  routing stays deterministic.
- `export-handoff`: this slice keeps the `terminal` CLI entrypoint pinned to
  the catalog-backed parser surface so the current export handoff route stays
  deterministic.
- AGENTS.md canonical demo-path statement: this work makes the CLI-first
  `project-open`, `retrieval`, `patch-review`, and `export-handoff` steps more
  real by locking the accepted parser surface to the command catalog that
  defines the current MVP contract.
- Concrete blocker removed: before this contract hardening, parser/catalog
  drift could silently reorder, replace, or drop accepted CLI entrypoints
  across the current demo-path command surface, which would destabilize the
  engine-side demo loop without a fast failure; `command_cli_contract()` now
  rejects that drift before the MVP operator contract can change unnoticed.

## Scope Boundary

- This remains command-catalog contract hardening for the CLI-first MVP path
  only. It does not add new commands, new flags, handler logic, or alternate
  workflow paths.
- This does not broaden the command surface beyond the current CLI-first MVP
  contract and should not be read as general command-platform work.

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

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it
  validates the full parser surface against the declared per-command CLI
  entrypoints, not just the deduplicated canonical-name projection, and raises
  `ValueError` when the accepted CLI surface drifts.
- Kept the returned CLI contract deterministic by preserving canonical command
  order for CLI-exposed specs while also enforcing the declared entrypoint
  order and lookup table shape for the default parser surface.
- Kept the demo-path preferred surface aligned with declared preferred tokens
  by including `export-handoff` in the terminal preferred-surface set and by
  generating preferred-surface invocations directly from the declared token
  order instead of filtering parser-surface order.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py`
  for parser-surface drift cases, including missing primary tokens, alias
  substitution, removed expected aliases, reordered entrypoints, and extra
  accepted entrypoints.
- Added regression coverage for the `export-handoff` preferred-surface token
  and invocation order so the demo-path contract matches the declared command
  surface.

## Metadata-Only Handoff Maintenance

- Refreshed the handoff packet so the review scope points at the current
  command-catalog implementation commit, the actual parser-surface invariant
  enforced in this branch, and this final reviewer-fix verification pass.
- Recorded that this final gate-verified refresh was run on `2026-04-17` after a
  fresh full-gate pass against implementation tip
  `ea00422c0b9c21e4bb0a3774abbad8a06facec62`.
- This final fixer commit refreshes `THREAD_PACKET.md` and `THREAD.md` and
  also includes the in-worktree command-catalog/test alignment already present
  in this lane worktree before the gate rerun.
- Verified in this final fixer pass that branch tip
  `ea00422c0b9c21e4bb0a3774abbad8a06facec62` already contains the reviewer-
  required parser-surface contract fix, and this final commit preserves that
  runtime/test behavior while refreshing the handoff authority.
- Verified again in this final fixer pass that the reviewer-requested demo-path mapping
  stays narrowed to the CLI-first `project-open`, `retrieval`, `patch-review`,
  and `export-handoff` steps and that the scope statement remains limited to
  command-catalog contract hardening only.
- Recorded in this refresh that the reviewer's REQUIRED FIXES are satisfied by
  an explicit `Canonical Demo-Path Step Advanced` section plus a Milestone 3
  scope boundary that stays tied to the engine-first CLI loop rather than
  broader command-surface or UX work.
- Re-ran the required lane gates in this final feature-fixer pass and
  confirmed `make scope-check`, `./quality-format.sh --check`,
  `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and
  `make ci` all still pass for this final reviewer-fix refresh before the
  handoff commit.
- Re-review alignment confirmation for this fixer turn: the packet already
  satisfied the reviewer-requested canonical demo-path mapping, so this refresh
  records a new verified handoff commit without changing the reviewed runtime
  implementation scope.
- Final verifier note for this commit: reran `make scope-check`,
  `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`,
  `./typecheck-test.sh`, and `make ci` on `2026-04-17` against implementation
  tip `ea00422c0b9c21e4bb0a3774abbad8a06facec62` plus the final in-worktree
  command-catalog/test alignment before creating this handoff refresh commit.

## Kickoff Budget / Limits Compliance

- Shared-test-exception handoff: stayed within the 4-task cap, 30-minute
  budget, and the lane size limits.
- The implementation slice stayed limited to one lane-owned command file plus
  one approved shared test file, so the handoff remains narrow and reviewable
  rather than a broader shared/runtime change.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- Approval artifact: the reviewer packet supplied to this fixer pass is the
  source of truth for the exception and explicitly records `Approved shared-test
  exception for tests/unit/test_commands_catalog.py` for this command-catalog
  slice.
- Approval basis: `scripts/scope-check.sh` is the active branch enforcement in
  this worktree, and its `codex/feat-commands*` allowlist explicitly permits
  `tests/unit/test_commands_catalog.py` as the one approved shared test path.
  This handoff uses only that allowlisted shared test and claims no other
  non-owned implementation files.

## Tasks Completed

1. Hardened `command_cli_contract()` so the CLI operator surface fails fast when accepted parser tokens drift from the command catalog.
2. Preserved deterministic CLI contract ordering by keeping canonical command order and declared per-command entrypoint order aligned with the catalog-backed parser surface.
3. Kept the demo-path preferred-surface contract aligned with declared terminal tokens by adding `export-handoff` to the preferred surface and generating preferred invocations from declared token order.
4. Added regression coverage in `tests/unit/test_commands_catalog.py` for parser-surface drift and preferred-surface invocation order.

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
- Risk justification: narrow lane-owned command-catalog contract hardening in
  `src/qual/commands/catalog.py` plus one approved shared test
  (`tests/unit/test_commands_catalog.py`), with no routing/provider changes
  and all required gates passing in this fixer pass.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the
  package/layout migration lands by keeping the command-catalog contract
  deterministic and drift-resistant across the current CLI-first `project-open`,
  `retrieval`, `patch-review`, and `export-handoff` entrypoints that make the
  current MVP loop callable and smoke-testable.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the
  engine-first MVP loop. This slice is a concrete unblocker, not second-order
  cleanup, because the loop cannot run reliably if the accepted parser surface
  for those current command routes can drift without the contract failing.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the
  command-catalog surface rejects parser drift before it can silently change
  the CLI operator contract for the current engine-first MVP loop. That keeps
  the operator-facing `project-open`, `retrieval`, `patch-review`, and
  `export-handoff` contract deterministic enough to smoke-test and rely on
  while Textual stays disabled.
- Scope limit note: this slice does not claim workflow, persisted-state,
  auditability, or additional product-vision capability changes. It is limited
  to deterministic CLI compatibility for the active engine-first operator
  surface while Textual remains disabled.

### Explicit canonical demo-path step advanced

- Required by `AGENTS.md`: this handoff explicitly advances the CLI-first
  `project-open`, `retrieval`, `patch-review`, and `export-handoff` steps by
  keeping their accepted command entrypoints deterministic and smoke-testable.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused
  command-catalog test coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES` via one approved shared test only
- Ownership detail: runtime edits stay in lane-owned `src/qual/commands/**`,
  and the only non-owned implementation path is the approved shared test
  `tests/unit/test_commands_catalog.py`.
- Approval basis detail: the shared-file exception is limited to that one test
  path recorded in the reviewer packet supplied to this fixer pass and
  allowlisted under `codex/feat-commands*` in `scripts/scope-check.sh`. No
  integrator-locked runtime files are part of this reviewed implementation
  slice.
