# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `metadata-only reviewer-fix handoff refresh`
- Packet refresh basis: `narrowed to the reviewer-approved implementation basis on 2026-04-24`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden the `feat-commands` command-catalog contract so the CLI-first MVP surface stays deterministic and drift-resistant for the canonical patch-review step.
- Risk reason: the reviewed slice includes one approved shared-test file outside lane-owned paths.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Reconfirm the reviewed implementation basis as the command-catalog slice at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Regenerate the handoff packet so the scope stays narrowly framed as deterministic CLI contract validation plus regression tests.
3. Name the exact canonical demo-path step this work strengthens and the concrete blocker it removes.
4. Re-run the required local gates for the reviewed slice.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- The reviewed implementation basis is `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Re-review approval basis is pinned to that commit and only these two reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- The implementation reviewed in that commit is limited to deterministic CLI contract validation plus regression tests:
  - `src/qual/commands/catalog.py` rejects parser/catalog drift by raising `ValueError` when canonical names or declared CLI entrypoints diverge from the validated catalog projection.
  - `tests/unit/test_commands_catalog.py` adds regression coverage for canonical ordering and parser/catalog drift rejection.
- Later handoff refresh commits are documentation-only and do not broaden the approval basis described here.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares the CLI contract against the validated command catalog and fails fast if parser/catalog drift would silently change the exposed CLI surface.
- Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly instead of rebuilding a potentially divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and parser/catalog drift rejection.
- Regenerated the handoff packet so the roadmap, vision, and canonical demo-path mapping stay aligned with this narrow command-catalog implementation slice.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Concrete blocker removed: parser/catalog drift could silently reorder or drop the canonical CLI token used to enter the patch-review surface, which weakens the CLI contract the MVP loop depends on before an operator can apply or reject a patch.
- Direct plan-alignment statement: this slice makes the canonical `preview and apply or reject a patch` step more real by ensuring the CLI parser surface stays pinned to the validated command catalog instead of drifting silently.
- Scope guard: this packet does not claim broader workflow progress beyond the named canonical patch step.

## Approved Exception Note

- Approved shared-test exception: `tests/unit/test_commands_catalog.py`
- Approval scope limit: this exception applies only to the focused regression coverage needed to prove canonical-order alignment and parser/catalog drift rejection for `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Hardened `command_cli_contract()` to verify canonical-name consistency and parser/catalog entrypoint consistency against the validated command catalog.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated the handoff packet so it explicitly names the canonical demo-path step advanced and keeps the approval basis narrowed to the reviewed implementation.

### Files Changed

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD_PACKET.md`
- `THREAD.md`

### Commands Run and Outcomes

- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`

### Risks / Blockers

- Risks:
  - future parser or catalog additions can still regress the CLI contract if they land without command-catalog contract coverage.
- Blockers:
  - none

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3 / `feat-commands`: CLI compatibility and migration-safe entrypoints.
- This slice keeps the reviewed patch-review CLI entrypoint deterministic and fail-closed within that scope.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the CLI remains the active first-class operator surface for the MVP loop while Textual stays disabled, so the parser surface must stay deterministic and fail closed when parser/catalog drift appears.

### Routing / Provider Impact Note

- None. This change only affects local command-contract validation and focused command-catalog test coverage.

### Scope-Check / Ownership Note

- Shared/integrator-locked edits: `NO`
- Shared-by-approval implementation path included: `tests/unit/test_commands_catalog.py`
