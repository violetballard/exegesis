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
- First green tests: recorded after the full required gate suite on `2026-04-23`.
- Before risky/shared file edit: this fixer pass only edits `THREAD.md` and `THREAD_PACKET.md`.
- Ready for handoff: the packet now names the canonical engine-first CLI loop mapping and keeps scope limited to command-contract hardening.

## Packet Traceability Note

- Review basis for re-review includes the two implementation commits in this narrow command-catalog slice:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `1e04f9633c4abc4988dcb991944680b86f94f753` (`Fix command shim subcommand routing`)
- Metadata-only handoff refresh commits in this re-review thread are:
  - `6a8eb130cafd8415f09223e1d51d76079972a754`
  - `9049bfd99ec15b89f983b78a53092713750a3031`
  - `6d40bdd5c1643b2e9b8688029daffcd264905dfd`
  - `49865ddc1337e78850134479abd03610075e20e3`
- This fixer adds one more metadata-only handoff refresh on top of the current reviewed implementation slice.
- Approval basis for re-review stays limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; this packet refresh corrects the handoff traceability without broadening the implementation claim beyond the current branch tip.

## Reviewer Required Fixes Satisfied

1. The handoff packet now explicitly maps this slice to the concrete canonical demo-path steps it advances: `vault` via the existing `bootstrap` / `project-open` entrypoint and `context` via the routed `context-basket search` surface while Textual remains disabled.
2. The packet now states the concrete blockers removed on those steps: silent parser/catalog drift could break the deterministic CLI contract for the `bootstrap` / `project-open` `vault` surface, and routed retrieval shims could lose the explicit `search` subcommand inside the `context` step.
3. The scope statement stays narrow and describes this work as deterministic CLI contract hardening only for those existing CLI fallback surfaces, with no claim that this patch implements later `run`, `patch`, or `export` steps, any audit/traceability behavior, or any new user-facing command breadth beyond the current MVP loop.
4. The vision mapping is intentionally limited to `Canonical engine contract`; no auditable-state claim is carried forward.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Fixed command shim subcommand routing so flow-step retrieval shims preserve explicit subcommands such as `search` instead of falling back to the default `context-basket list` tail.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for retrieval shim subcommand preservation through `command_cli_entry_argv()` and `command_resolve_argv()`.
- Refreshed `THREAD.md` and `THREAD_PACKET.md` so the handoff matches the reviewed command-catalog slice and its current roadmap-aligned MVP CLI-fallback `vault`/`context` mapping.

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
- Reviewed implementation commits:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
  - `1e04f9633c4abc4988dcb991944680b86f94f753`
- Packet refresh commit: this fixer commit (`HEAD` after commit)

### Tasks Completed (Numbered)

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Fixed command shim subcommand routing so retrieval flow-step shims preserve explicit routed actions such as `search`.
5. Added regression coverage in `tests/unit/test_commands_catalog.py` for retrieval shim subcommand preservation.
6. Refreshed the handoff metadata so the reviewer packet explicitly maps this deterministic CLI-contract hardening to the CLI fallback `vault` and `context` steps it advances and accurately points to the current reviewed implementation commits.

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
- Verification date: `2026-04-23`
- Fixer verification note: reran `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on `2026-04-23` after confirming the reviewed implementation anchors and the reviewer-requested canonical demo-path mapping remained present and scope-tight in the handoff metadata.

## Ready For Handoff

- Status: ready for re-review
- Current fixer pass: metadata-only handoff refresh plus fresh required gate rerun on `2026-04-23`
- Reviewed implementation anchors are `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and `1e04f9633c4abc4988dcb991944680b86f94f753`
- No implementation files changed in this fixer pass

### Risks / Blockers

- Risk: `LOW`
- Remaining risk: none beyond future parser-surface changes that skip the catalog contract, which the added regression coverage is intended to catch.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 5: A2UI Presentation Layer - preserve CLI fallback compatibility for the current MVP exit criterion `vault -> context -> run -> patch -> export` by keeping the command-catalog-backed `vault` and `context` operator surfaces deterministic and drift-resistant while Textual remains disabled.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract for the existing CLI-first `vault` and `context` steps in the MVP loop.

### Canonical demo-path step advanced

- Canonical demo-path step advanced: the CLI fallback `vault` and `context` steps, specifically the existing `bootstrap` / `project-open` entrypoint for `vault` and the routed `context-basket search` surface for `context` while Textual remains disabled.
- Concrete demo-path narrowing: this handoff ties the reviewed command-catalog slice to `A2UI contracts with CLI fallback` by making the `bootstrap` / `project-open` `vault` surface and the routed `context-basket search` `context` surface deterministic and smoke-testable for those steps only.
- Explicit handoff statement: this change makes the canonical demo path more real for `A2UI contracts with CLI fallback` by hardening the existing CLI operator surface for `vault` and `context`, without claiming that this patch implements `run`, later `patch` / `export` steps, or any audit/traceability behavior.
- Concrete blockers removed:
  - before this hardening, the explicit CLI parser surface could drift from the canonical command catalog order or membership without failing fast, which would make the `bootstrap` / `project-open` `vault` step less deterministic and weaken smoke-test coverage for that path
  - before the shim routing fix, an explicit retrieval subcommand such as `search` could be swallowed by the default `context-basket list` tail when resolved through the flow-step shim, making the CLI fallback `context` step less trustworthy for the already-in-scope retrieval surface
- Scope-specific alignment note: this is CLI contract hardening only for the existing `bootstrap` / `project-open` `vault` surface and `context-basket search` `context` shim surface, with no claim of broader retrieval ranking, `run` execution, patch application, persistence, auditability, or UI progress and no new user-facing command breadth beyond the current MVP loop.

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
