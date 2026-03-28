# Thread Handoff Packet

- Branch name: `codex/feat-context-storage`

## Scope goal
- Harden context basket/set and vault recovery so malformed or incomplete local state is quarantined or canonicalized safely without promoting stale auxiliary state.

## Scope completed
- Quarantined malformed context basket and context-set payloads during recovery so rewritten state stays normalized and auditable.
- Hardened vault recovery so malformed or incomplete persisted state is recovered or rewritten safely while preserving the safe lock default.
- Kept regression coverage in `tests/unit/test_context_storage_recovery.py` under the approved shared-file exception for the vault recovery regression.

## Files changed
- `src/qual/context/set_store.py`
- `src/qual/context/store.py`
- `src/qual/storage/vault.py`
- `tests/unit/test_context_storage_recovery.py`

## Tasks completed
1. Tightened `ContextBasketStore` recovery so malformed basket payloads are quarantined and canonical rewrites remain auditable.
2. Tightened `ContextSetStore` recovery so malformed context-set payloads are quarantined and canonical rewrites remain auditable.
3. Tightened `VaultService` recovery so malformed vault state is recovered or rewritten safely while preserving the safe lock default.
4. Kept regression coverage in `tests/unit/test_context_storage_recovery.py` under the approved shared-file exception.

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
- Milestone 3 - Real workflow loop: persistent basket/document/session state.

### Vision capability affected
- Capability 6 - Auditable state and workflow: persistent project/document/basket/session state with safe recovery and traceable rewrites.

### Routing/provider impact note
- None

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` - approved shared-test exception only, limited to `tests/unit/test_context_storage_recovery.py`; no integrator-locked files changed.
- Ownership detail: runtime edits are limited to `src/qual/context/**` and `src/qual/storage/**`. The only non-owned edit is `tests/unit/test_context_storage_recovery.py`, and it is covered by the explicit shared-test exception.
- Approval basis: `scripts/scope-check.sh` explicitly allows `tests/unit/test_context_storage_recovery.py` for `codex/feat-context-storage*` when `SCOPE_ALLOW_SHARED=1` is set.
