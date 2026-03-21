# Feature → Review Packet

- Lane: `feat-context-storage`
- Branch: `codex/feat-context-storage`
- Commit: `5cd2c4a5a44ce18409b52e44db51a9824f411a5c`

## Scope goal
- Harden context basket and vault persistence recovery so malformed optional metadata is salvaged and rewritten without discarding valid local state, and cover that recovery contract with focused tests.

## Lane/owned paths
- `src/qual/context/**`
- `src/qual/storage/**`

## Kickoff budget/limits compliance
- Thread Kickoff Template budget applied: task budget `8`, time budget `45m`, size limits `<=12 files` and `<=500 net LOC`, max fix attempts per failing gate `2`. Tasks completed: `4 of 8`. Budget status: within limits at `4` files changed with `399` insertions and `35` deletions versus `codex/integrator`; this lane stayed within the time window and did not exceed the `2`-attempt gate-fix limit.

## Approved exception note
- Ownership note: runtime edits stay within the lane-owned paths `src/qual/context/**` and `src/qual/storage/**`. Approved shared-file exception covers `tests/unit/test_context_storage_recovery.py` for the vault recovery regression alongside the owned-path storage fix. There are no shared-by-approval source-file edits and no integrator-locked edits.

## Tasks completed (numbered)
1. Updated context basket recovery to treat malformed optional metadata as salvageable while still rejecting unrecoverable schema or item-id payloads.
2. Updated vault state recovery to preserve valid lock and project metadata when optional metadata fields are malformed, then rewrite normalized persisted state.
3. Added focused metadata-only corruption tests for both context basket and vault persistence paths, including backup-promotion recovery cases.
4. Added corrupt-primary recovery tests and explicit rewrite behavior so fallback provenance is not persisted when the primary file was present but corrupt.

## Files changed
- `src/qual/context/basket.py`
- `src/qual/context/store.py`
- `src/qual/storage/vault.py`
- `tests/unit/test_context_storage_recovery.py`

## Commands run and outcomes
- `make scope-check`: FAIL (approved non-owned test file requires `SCOPE_ALLOW_SHARED=1`)
- `SCOPE_ALLOW_SHARED=1 make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `SCOPE_ALLOW_SHARED=1 make ci`: PASS

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
- Ownership detail: runtime edits stay within the lane-owned paths `src/qual/context/**` and `src/qual/storage/**`. Approved shared-file exception covers `tests/unit/test_context_storage_recovery.py` for the vault recovery regression alongside the owned-path storage fix. No shared-by-approval source files were edited, and no integrator-locked files were edited.
- Integrator-locked edits: `NO`
