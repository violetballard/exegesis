# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `4d451643`
- Packet refresh commit: `metadata-only handoff refresh after 2026-04-17T05:17:00Z verification`
- Packet refresh role: `feature-lane handoff refresh for current branch HEAD`

## Packet Traceability Note

- The command-catalog implementation under review is `4d451643`.
- This packet refresh records the latest required gate rerun for the current
  branch head and aligns the handoff fields to the terminal argv
  normalization change now on the branch.

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

- Keep the terminal-side command surface deterministic for the Milestone 3 demo
  loop by preserving parser-ready argv ordering when callers override default
  terminal operation options.

## Canonical Demo-Path Step Advanced

- Exact canonical demo-path step advanced: `persist and continue / export handoff`.
- Concrete blocker removed: the canonical `terminal` route and its shims now
  keep `--operation-kind` in a stable parser-ready slot when callers override
  defaults, so the persist/export handoff path normalizes to one deterministic
  argv shape instead of reordering options.
- Scope boundary: this slice remains command-catalog normalization work for the
  existing CLI contract. It does not add new commands, new flags, handler
  logic, or alternate workflow paths.

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

- Refactored command shim argv handling in `src/qual/commands/catalog.py` to
  segment explicit args and replace overridden options in-place instead of
  dropping the original slot and appending the override later.
- Preserved positional tail args while still deduplicating repeated explicit
  options down to the last occurrence.
- Kept pinned shim options authoritative for alias-backed commands while making
  the raw `terminal` command normalize to a stable parser-ready option order.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py`
  for `command_cli_entry_argv()`, `command_resolve_argv()`, and
  `command_smoke_argv()` on the raw `terminal` route.
- Refreshed the handoff packet for the current branch head after the full
  required gate sequence passed.

## Kickoff Budget / Limits Compliance

- Low-risk lane-owned implementation stayed within the 8-task cap, 45-minute
  budget, and the lane size limits.
- The implementation slice stayed limited to one owned command file plus one
  focused non-owned test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- Approval trace: carried forward from the prior feature packet and reviewer
  packet for this lane, which explicitly states `Approved shared-test
  exception for tests/unit/test_commands_catalog.py` for the command-catalog
  slice under review.

## Tasks Completed

1. Refactored shim argv parsing so explicit command options are segmented and deduplicated deterministically.
2. Changed shim argv merging to replace overridden options in their original template slots instead of appending them at the end.
3. Preserved positional tail args and pinned-option behavior across alias-backed command shims.
4. Added regression coverage for raw `terminal` argv normalization in parser-entry, resolve, and smoke helpers.
5. Refreshed the handoff packet for the current branch head after rerunning the required gates.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD.md`
- `THREAD_PACKET.md`

## Commands Run and Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS
- Verification timestamp: `2026-04-17T05:17:00Z`

## Risks / Blockers

- Risk: low. Future command-template changes still need matching regression
  coverage where option-order stability matters for parser-facing smoke paths.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Product readiness / lock user-facing output contracts by keeping
  the CLI command surface deterministic for parser-facing terminal routes.
- `feat-commands` - stable CLI-first MVP loop for patch review, apply/reject,
  and export handoff flows.

### Vision capability affected

- Operator-first control surface - CLI parser-facing commands stay stable and
  smoke-testable for the persist/export handoff path.
- Agent-to-UI protocol (`A2UI`) with CLI fallback - stable command argv shapes
  keep the CLI fallback surface predictable for future shared contract
  consumers.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused
  command-catalog test coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: runtime edits stay in lane-owned `src/qual/commands/**`,
  and the only non-owned implementation path is the approved shared test
  `tests/unit/test_commands_catalog.py`.
- Shared-file approval source: the review packet supplied to this fixer pass is
  the source of truth and records the approved shared-test exception for
  `tests/unit/test_commands_catalog.py`.
