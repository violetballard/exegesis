# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `reviewer-fix handoff refresh`
- Packet refresh basis: `post-gate revalidation of the reviewer-fix packet on 2026-04-23`
- Packet refresh parent commit: `52de8dab`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden the `feat-commands` command-catalog contract so the CLI-first MVP surface stays deterministic and drift-resistant while Textual remains disabled.
- Risk reason: the reviewed slice includes one approved shared-test file outside lane-owned paths.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Reconfirm the reviewed implementation basis as the command-catalog slice at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Refresh the handoff packet so the scope stays narrowly framed as `feat-commands` contract hardening.
3. Add the explicit canonical demo-path statement required by `AGENTS.md`.
4. Re-run the required local gates for the reviewed slice.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- The reviewed implementation basis is `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Re-review approval basis is pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and only these two reviewed implementation files: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- Later packet-refresh commits are metadata-only and do not expand the reviewed implementation scope.
- This packet was revalidated after a fresh full-gate pass in the current worktree before handoff.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only handoff file:
  - `THREAD_PACKET.md`

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly instead of rebuilding a potentially divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and parser/catalog drift rejection.
- Refreshed the handoff packet so the roadmap, vision, and demo-path mapping stay aligned with this narrow command-catalog implementation slice.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `patch-review` in the current CLI-first MVP path (`project-open -> retrieval -> patch-review -> apply-patch/reject-patch -> persist -> export-handoff`).
- Direct plan-alignment statement: this slice makes the canonical `patch-review` step more real by stabilizing the CLI/operator surface the Milestone 3 engine-first loop relies on while Textual remains disabled.
- Concrete unblocker removed: deterministic command-catalog validation now fails fast if parser tokens drift away from the canonical catalog, so operators do not lose the reviewed-patch CLI entrypoint that must remain available before `apply-patch`, `reject-patch`, `persist`, and `export-handoff`.
- CLI-first Milestone 3 loop tie-in: this is the `patch` segment of the roadmap MVP flow (`vault -> context -> run -> patch -> export`), and the contract check keeps that exact engine-first loop segment backward-compatible by policy instead of treating CLI compatibility as general polish.
- Scope guard: this remains narrow `feat-commands` contract hardening for the engine-first CLI/operator path; it does not claim broader workflow, UI, Textual, or A2UI progress.

## Approved Exception Note

- Approved shared-test exception: `tests/unit/test_commands_catalog.py`
- Approved by: the lane `reviewer` role, as recorded in archived approval packet `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/packets/lanes/feat-commands/archive/R__APPROVED__codex-feat-commands__96f57e262da909d58a61cbdf4aa162aac8f16196__20260424T005429Z.md`.
- Approval source: archived reviewer approval packet `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/packets/lanes/feat-commands/archive/R__APPROVED__codex-feat-commands__96f57e262da909d58a61cbdf4aa162aac8f16196__20260424T005429Z.md`, plus canonical lane metadata `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/lane_meta/feat-commands.json`; both describe `tests/unit/test_commands_catalog.py` as the only approved non-owned implementation path in this narrowed handoff.
- Approval scope limit: this exception applies only to the focused regression coverage needed to prove canonical-order alignment and parser/catalog drift rejection for the `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` command-catalog slice.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Refreshed the handoff packet so it explicitly states the canonical demo-path step this work advances and keeps the scope narrowed to `feat-commands` contract hardening.

### Files Changed

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD_PACKET.md`

### Commands Run and Outcomes

- `make scope-check`: `PASSED` (`[devex] scope-check: passed for branch 'codex/feat-commands'`)
- `./quality-format.sh --check`: `PASSED` (`[format] check passed`)
- `./quality-lint.sh`: `PASSED` (`[lint] passed`)
- `./quality-test.sh`: `PASSED` (`smoke passed`; `Ran 203 tests ... OK`)
- `./typecheck-test.sh`: `PASSED` (`[typecheck] compiling Python sources in src/`)
- `make ci`: `PASSED` (`[devex] CI entrypoint completed`)

### Risks / Blockers

- Risks:
  - future parser or catalog additions can still regress the CLI contract if they land without command-catalog contract coverage.
- Blockers:
  - none

## Required Handoff Fields

### Roadmap item(s) affected

- `feat-commands`: this slice is explicit CLI-compatibility hardening for the active engine-first MVP loop, specifically the `patch-review` step and its downstream `apply-patch`/`reject-patch`, `persist`, and `export-handoff` transitions.
- `ROADMAP.md` engine-first MVP loop requirement: `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`; this change removes parser/catalog drift as a blocker on the `patch` segment of that exact loop, so the live CLI surface stays migration-safe while Textual remains disabled.
- Milestone 3 `Product Readiness`: this slice counts as contract work only because it explicitly locks the `feat-commands` CLI surface for that engine-first patch/export operator path, not because it is broad contract cleanup.

### Vision capability affected

- `PRODUCT_VISION.md` operator-first control surface: `feat-commands` is responsible for keeping the active CLI operator path canonical and deterministic while the engine-first MVP loop still runs through CLI instead of Textual.
- `PRODUCT_VISION.md` CLI-first artifact consumption requirement: the reviewed `patch-review` -> `apply-patch`/`reject-patch` -> `persist` -> `export-handoff` path must stay available through CLI first, so parser/catalog drift must fail closed instead of silently weakening the engine-first command contract.

### Routing / Provider Impact Note

- None. This change only affects local command-contract validation and focused command-catalog test coverage.

### Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Approved shared-test exception: `tests/unit/test_commands_catalog.py`
- Approved by: the lane `reviewer` role, recorded in archived approval packet `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/packets/lanes/feat-commands/archive/R__APPROVED__codex-feat-commands__96f57e262da909d58a61cbdf4aa162aac8f16196__20260424T005429Z.md`
- Approval source: archived reviewer approval packet `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/packets/lanes/feat-commands/archive/R__APPROVED__codex-feat-commands__96f57e262da909d58a61cbdf4aa162aac8f16196__20260424T005429Z.md`; canonical lane metadata record `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/lane_meta/feat-commands.json`
- Approval record detail: `Approved shared-test exception for tests/unit/test_commands_catalog.py. It is the only non-owned implementation path in this handoff.`
