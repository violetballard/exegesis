## Thread Handoff Packet

- Branch name: `codex/feat-context-storage`
- Scope goal: Harden lane-owned context and vault persistence so incomplete local state is quarantined before canonical rewrite.
- Scope completed: Hardened `ContextBasketStore` and `VaultService` recovery behavior so malformed or incomplete primary state is quarantined, then rewritten deterministically from the canonical load path.
- Tasks completed:
  1. Quarantined incomplete primary context-basket state before canonical rewrite.
  2. Quarantined incomplete primary vault state before canonical rewrite.
  3. Added regression coverage for both quarantine-before-rewrite recovery paths.
  4. Revalidated the lane handoff metadata so the submission stays scope-clean and ownership-accurate.
- Files changed:
  - `src/qual/context/store.py`
  - `src/qual/storage/vault.py`
  - `tests/unit/test_context_storage_recovery.py`
- Commands run with results:
  - `python -m unittest tests.unit.test_context_storage_recovery` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make scope-check` -> passed
  - `make ci` -> passed
- Risks/blockers:
  - No shared, integrator-locked, `.codex`, or thread files are included in the feature diff.
  - Recovery behavior still depends on local filesystem atomicity for primary/backup writes, which is expected for this lane.
- Roadmap item(s) affected:
  - `Milestone 1: Bootstrap Flow Stabilization` -> Context basket and vault persistence hardening
  - `Milestone 2: Test Hardening` -> Add focused unit coverage for core behaviors
- Vision capability affected:
  - `1. Local-first state and identity` -> Project-scoped vault and context basket with safe recovery behavior
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
