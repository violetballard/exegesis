# Feature → Review Packet

- Lane: `feat-context-storage`
- Branch: `codex/feat-context-storage`
- Commit: `9b447b46c20a4d5c112f35dea7c9c0e3532fdde7`

## Scope goal
- Harden context basket and vault persistence recovery so malformed optional metadata is salvaged and rewritten without discarding valid local state, and cover that recovery contract with focused tests.

## Lane/owned paths
- `src/qual/context/**`
- `src/qual/storage/**`

## Kickoff budget/limits compliance
- Thread Kickoff Template budget applied: task budget `8`, time budget `45m`, size limits `<=12 files` and `<=500 net LOC`, max fix attempts per failing gate `2`. Tasks completed: `4 of 8`. Budget status: within limits at `5` files changed with `304` insertions and `33` deletions versus `codex/integrator`; this lane stayed within the time window and did not exceed the `2`-attempt gate-fix limit.

## Approved exception note
- Ownership note: runtime edits stay within the lane-owned paths `src/qual/context/**` and `src/qual/storage/**`. The only non-owned change is the approved test file `tests/unit/test_context_storage_recovery.py`, and no integrator-locked files were edited.

## Tasks completed (numbered)
1. Updated context basket recovery to treat malformed optional metadata as salvageable while still rejecting unrecoverable schema or item-id payloads.
2. Updated vault state recovery to preserve valid lock/project state when optional metadata fields are malformed, then rewrite normalized persisted state.
3. Normalized context basket item-id handling so mixed invalid entries can be salvaged and rewritten instead of forcing a full discard.
4. Added focused metadata-only corruption tests for both context basket and vault persistence paths, including backup-promotion recovery cases.

## Files changed
- `src/qual/context/basket.py`
- `src/qual/context/store.py`
- `src/qual/storage/vault.py`
- `tests/unit/test_context_storage_recovery.py`

## Commands run and outcomes
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `MEDIUM`
- Blockers: none

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: context basket and vault persistence hardening.
### Vision capability affected
- Capability 1 - Local-first state and identity.
### Routing/provider impact note
- None

## Scope-check / ownership note
- Approved shared test-file exception only: `YES`
- Shared-by-approval source edits: `NO`
- Ownership detail: runtime edits stay within the lane-owned paths `src/qual/context/**` and `src/qual/storage/**`. The only approved exception is the shared test file `tests/unit/test_context_storage_recovery.py`. No shared-by-approval source files were edited, and no integrator-locked files were edited.
- Integrator-locked edits: `NO`
