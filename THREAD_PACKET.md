## Thread Handoff Packet

- Branch name: `codex/feat-context-storage`
- Scope goal: Harden context basket and vault persistence recovery so malformed optional metadata is salvaged and rewritten without discarding valid local state, and cover that recovery contract with focused tests.
- Scope completed: Hardened context basket and vault persistence recovery, then kept the recovery regression coverage aligned with the branch diff.
- Tasks completed:
  1. Updated context basket recovery to treat malformed optional metadata as salvageable while still rejecting unrecoverable schema or item-id payloads.
  2. Updated vault state recovery to preserve valid lock and project metadata when optional metadata fields are malformed, then rewrite normalized persisted state.
  3. Normalized context basket item-id handling so mixed invalid entries can be salvaged and rewritten instead of forcing a full discard.
  4. Added focused metadata-only corruption tests for both context basket and vault persistence paths, including backup-promotion recovery cases.
- Files changed:
  - `src/qual/context/basket.py`
  - `src/qual/context/store.py`
  - `src/qual/storage/vault.py`
  - `tests/unit/test_context_storage_recovery.py`
- Approved exception note:
  - The only non-owned edit in this handoff is `tests/unit/test_context_storage_recovery.py`, which is the explicitly approved recovery coverage file. No shared-by-approval source files or integrator-locked files were edited.
- Commands run with results:
  - `make scope-check` -> passed.
  - `./quality-format.sh --check` -> passed.
  - `./quality-lint.sh` -> passed.
  - `./quality-test.sh` -> passed.
  - `./typecheck-test.sh` -> passed.
  - `make ci` -> passed.
- Checkpoint status:
  - plan complete
  - first green tests: `./quality-test.sh` passed (`Ran 114 tests`, `OK`)
  - ready for handoff: all required local gates passed
- Risks/blockers:
  - The approved shared test file is the only non-owned edit in the submitted diff.
- Roadmap item(s) affected:
  - `Milestone 1 - Bootstrap Flow Stabilization: context basket and vault persistence hardening.`
  - `Milestone 2 - Recovery and Export Robustness: vault recovery and persistence normalization.`
- Vision capability affected:
  - `Capability 1 - Local-first state and identity.`
- Routing/provider impact note: None.
- Proposed `README.md` patch text: None.
- Scope-check / ownership note:
  - Approved shared test-file exception only: `YES`
  - Shared-by-approval source edits: `NO`
  - Integrator-locked edits: `NO`
