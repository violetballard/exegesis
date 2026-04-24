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

- Canonical demo-path step advanced: the CLI/operator-contract portion of the current MVP path that makes `produce a plan or revision` and `preview and apply or reject a patch` reachable through a stable command surface while Textual remains disabled.
- Explicit statement of what this work makes more real: it hardens the CLI-first operator route across the canonical demo path by preventing parser/catalog drift from silently changing the command surface.
- Scope guard: this remains `feat-commands` contract hardening for the engine-first MVP loop; it does not claim broader workflow, UI, or A2UI progress.

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

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.
- Canonical demo-path step advanced: the stable CLI/operator-contract path used to produce a plan or revision and to preview, apply, or reject a patch while Textual remains disabled.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract.
- Auditable state and workflow - the command surface now fails loudly on catalog/parser drift, making the operator-facing contract explicit and traceable.

### Routing / Provider Impact Note

- None. This change only affects local command-contract validation and focused command-catalog test coverage.

### Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Approved shared-test exception: `tests/unit/test_commands_catalog.py`
