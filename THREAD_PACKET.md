## Thread Handoff Packet

- Branch name: `codex/feat-context-storage`
- Reviewed commit(s):
  - `47cda4df831ac41867a8792f40d720e0cb109514` (runtime storage/context hardening)
  - `002668f6` (metadata-only handoff alignment)

## Scope completed

This handoff is context basket and vault persistence hardening within the lane-owned storage/context paths. The lane hardened context basket, context-set, and vault persistence so malformed or incomplete local state is quarantined or canonicalized safely, valid recovery paths are preserved, and recovery rewrites stay auditable. The shipped runtime changes are in `src/qual/context/set_store.py`, `src/qual/context/store.py`, and `src/qual/storage/vault.py`. The approved shared-test exception is limited to `tests/unit/test_context_storage_recovery.py`.

## Files changed

- `src/qual/context/set_store.py`
- `src/qual/context/store.py`
- `src/qual/storage/vault.py`
- `tests/unit/test_context_storage_recovery.py`

## Tasks completed

1. Tightened `ContextBasketStore` recovery so malformed basket payloads are quarantined, recoverable payloads are canonicalized, and rewritten state stays auditable.
2. Tightened `ContextSetStore` recovery so malformed context-set payloads are quarantined, recoverable payloads are canonicalized, and rewritten state stays auditable.
3. Tightened `VaultService` recovery so malformed vault state is recovered or rewritten safely while preserving the safe lock default.
4. Added and maintained regression coverage in `tests/unit/test_context_storage_recovery.py` for the vault recovery regression under the approved shared-test exception.

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

## Roadmap item(s) affected

- MVP Focus Through 2026-05-04: `feat-context-storage`

## Vision capability affected

- 1. Local-first state and identity

## Routing/provider impact note

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: approved shared-test exception only, limited to `tests/unit/test_context_storage_recovery.py`; no integrator-locked files changed.
- Approval basis: `scripts/scope-check.sh` explicitly allows `tests/unit/test_context_storage_recovery.py` for `codex/feat-context-storage*` when `SCOPE_ALLOW_SHARED=1` is set.
- Branch-head bookkeeping note: `002668f6` records lane metadata only; it does not change the owned runtime scope.
- Ownership detail: lane-owned runtime edits are limited to `src/qual/context/**` and `src/qual/storage/**`. The only non-owned edit is `tests/unit/test_context_storage_recovery.py`, and it is covered by the explicit shared-test exception.
