# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `reviewer-fix handoff refresh`

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
- Later packet-refresh commits are metadata-only and do not expand the reviewed implementation scope.
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
- Explicit statement of what this work makes more real: deterministic command-catalog validation removes a concrete blocker for `patch-review` by failing fast when parser tokens drift away from the canonical catalog, so the CLI cannot silently stop exposing the reviewed-patch entrypoint operators need before they can `apply-patch`, `reject-patch`, `persist`, and `export-handoff` the result.
- CLI-first Milestone 3 loop tie-in: this is the `patch` segment of the roadmap MVP flow (`vault -> context -> run -> patch -> export`), and the contract check keeps that exact segment backward-compatible by policy instead of relying on best-effort CLI compatibility.
- Scope guard: this remains `feat-commands` contract hardening for the engine-first MVP loop; it does not claim broader workflow, UI, or A2UI progress.

## Approved Exception Note

- Approved shared-test exception: `tests/unit/test_commands_catalog.py`
- Approval source: prior reviewer approval packet at `.codex/packet_router/local_jobs/reviewer/20260416T185314Z__feat-commands__F__codex-feat-commands__f3e88eb90a1116054bac208067568d3c7fbed927__20260416T185054Z.md.spec.json`, which approved this same narrowed `feat-commands` handoff with `tests/unit/test_commands_catalog.py` as the only non-owned implementation path.
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

- Milestone 3: `Product Readiness` requires user-facing output contracts to be defined and locked and end-to-end verification scenarios to expand; this change makes that concrete for the CLI-first MVP loop by locking the command-catalog contract that drives `patch-review` before `apply-patch`/`reject-patch`, `persist`, and `export-handoff`.
- `ROADMAP.md` CLI-first Milestone 3 loop requirement: `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`; this change removes parser/catalog drift as a blocker on the `patch` segment of that exact loop and helps keep the output contract test-covered and backward-compatible by policy.
- `feat-commands`: keep migration-safe command entrypoints deterministic so the active Milestone 3 lane can still exercise the reviewed patch/export path through CLI while Textual remains disabled.

### Vision capability affected

- `PRODUCT_VISION.md` operator-first control surface: CLI remains a first-class development and reliability surface, so the reviewed patch command path must stay canonical and deterministic instead of depending on parser alias drift.
- `PRODUCT_VISION.md` CLI-first artifact consumption requirement: artifacts must be consumable by CLI first, with CLI text fallback preserved, so silent parser drift cannot be allowed to break the CLI command path that reaches `patch-review` and the downstream `export-handoff`.

### Routing / Provider Impact Note

- None. This change only affects local command-contract validation and focused command-catalog test coverage.

### Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Approved shared-test exception: `tests/unit/test_commands_catalog.py`
- Approval source: `.codex/packet_router/local_jobs/reviewer/20260416T185314Z__feat-commands__F__codex-feat-commands__f3e88eb90a1116054bac208067568d3c7fbed927__20260416T185054Z.md.spec.json`
