# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: tighten the handoff packet so it matches the reviewer-approved command-catalog slice and explicitly maps this deterministic CLI-contract hardening to the canonical engine-first CLI loop it strengthens.
- Risk reason: this fixer edits shared handoff metadata and must keep the review scope narrow instead of re-expanding it to broader branch history.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the handoff packet to the reviewer-approved command-catalog implementation slice.
2. Add the missing AGENTS-required canonical demo-path mapping.
3. Keep the scope statement narrow and limited to command-contract hardening.
4. Re-run `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Early Review Triggers

- Before first edit to any shared/integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing/config behavior.

### Stop Triggers

- Unresolved test/lint/typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: fix only the shared handoff metadata required by the reviewer packet.
- First green tests: recorded after the full required gate suite on `2026-04-18`.
- Before risky/shared file edit: this fixer pass only edits `THREAD.md` and `THREAD_PACKET.md`.
- Ready for handoff: the packet now names the canonical engine-first CLI loop mapping and keeps scope limited to command-contract hardening.

## Packet Traceability Note

- Review basis remains the command-catalog implementation at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Packet refresh commit `33ca8b43c08492bcb201b6fe0c6c6fef70175347` is metadata-only.
- This fixer adds one more metadata-only handoff refresh on top of that slice.
- Approval basis for re-review stays anchored to implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this packet refresh does not broaden the implementation claim.

## Reviewer Required Fixes Satisfied

1. The handoff packet now explicitly names one canonical demo-path step advanced by this slice: `project-open` (`open project/document`) via `bootstrap`.
2. The packet now states the concrete blocker removed on that path: silent parser/catalog drift could break the deterministic CLI contract and its smoke-test coverage for the `project-open` / `bootstrap` entrypoint.
3. The scope statement stays narrow and describes this work as deterministic command-contract hardening only for that single CLI-first reachability step, with no new user-facing command breadth beyond the current MVP loop.
4. The vision mapping is intentionally limited to `Canonical engine contract`; no auditable-state claim is carried forward.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Refreshed `THREAD.md` and `THREAD_PACKET.md` so the handoff matches the reviewed command-catalog slice and its AGENTS-required demo-path mapping.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the `4`-task cap, `30m` budget, and metadata-only fixer scope.
- The reviewed implementation slice remains limited to one owned command file plus one approved shared test file, with this fixer pass limited to handoff metadata.

## Approved Exception Note

- Approved shared/non-owned paths in scope:
  - `tests/unit/test_commands_catalog.py`
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Handoff Packet

- Branch name: `codex/feat-commands`
- Reviewed implementation commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh commit: this fixer commit (`HEAD` after commit)

### Tasks Completed (Numbered)

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Refreshed the handoff metadata so the reviewer packet explicitly maps this deterministic CLI-contract hardening to the canonical engine-first CLI loop it advances.

### Files Changed

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`
- Verification date: `2026-04-18`

## Ready For Handoff

- Status: ready for re-review
- Current fixer pass: metadata-only handoff refresh plus fresh required gate rerun on `2026-04-18`
- Reviewed implementation anchor remains `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- No implementation files changed in this fixer pass

### Risks / Blockers

- Risk: `LOW`
- Remaining risk: none beyond future parser-surface changes that skip the catalog contract, which the added regression coverage is intended to catch.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract for the CLI-first MVP loop.

### Canonical demo-path step advanced

- Canonical demo-path step advanced: `project-open` (`open project/document`) via `bootstrap`.
- Concrete demo-path narrowing: this handoff ties the reviewed command-catalog slice to the active engine-first CLI path by making the `project-open` / `bootstrap` entrypoint deterministic and smoke-testable in canonical catalog order.
- Explicit handoff statement: this change makes the canonical demo path more real by keeping the CLI operator surface aligned to the catalog at the `project-open` step before the workflow proceeds further.
- Concrete blocker removed: before this hardening, the explicit CLI parser surface could drift from the canonical command catalog order or membership without failing fast, which would make the `project-open` step via `bootstrap` less deterministic and weaken smoke-test coverage for that entrypoint.
- Scope-specific alignment note: this is contract hardening only for the `project-open` reachability step, with no claim of broader retrieval, patch-application, persistence, or UI progress and no new user-facing command breadth beyond the current MVP loop.

### Routing/provider impact note

- None.

### Proposed `README.md` patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail:
  - lane-owned implementation: `src/qual/commands/catalog.py`
  - approved shared test exception: `tests/unit/test_commands_catalog.py`
  - shared metadata updated for handoff accuracy: `THREAD.md`, `THREAD_PACKET.md`
