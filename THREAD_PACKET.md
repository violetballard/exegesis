## Thread Handoff Packet

- Branch name: `codex/feat-context-storage`
- Scope goal: Deliver the context-storage recovery hardening in `src/qual/context/**` and `src/qual/storage/**` while keeping the handoff scope-tight and limited to the approved recovery test outside owned paths.
- Scope completed: Hardened context basket and vault persistence recovery so malformed optional metadata is normalized or salvaged when possible, valid primary state survives backup refresh failures, and the approved recovery regression coverage stays aligned with the branch diff.
- Tasks completed:
  1. Normalized `ContextBasket` item IDs on construction and mutation so malformed inputs are dropped before they can persist.
  2. Reworked `ContextBasketStore` load and save flows to salvage valid payloads, refresh backups safely, and preserve recoverable seed state when primary or backup writes fail.
  3. Updated `Vault` recovery to preserve valid metadata while rewriting normalized persisted state after partial corruption.
  4. Added focused regression coverage in `tests/unit/test_context_storage_recovery.py` for basket recovery, vault recovery, and backup/seed rewrite behavior.
- Files changed:
  - `src/qual/context/basket.py`
  - `src/qual/context/store.py`
  - `src/qual/storage/vault.py`
  - `tests/unit/test_context_storage_recovery.py`
- Approved exception note:
  - The only non-owned edit in this handoff is `tests/unit/test_context_storage_recovery.py`, which is the explicitly approved recovery coverage file. No shared-by-approval source files or integrator-locked files were edited, and `.codex/lane_meta/feat-context-storage.json` is not part of the submitted diff.
- Commands run with results:
  - `make scope-check` -> failed without the approved shared-test override because `tests/unit/test_context_storage_recovery.py` is outside the lane-owned paths.
  - `SCOPE_ALLOW_SHARED=1 make scope-check` -> passed.
  - `./quality-format.sh --check` -> passed.
  - `./quality-lint.sh` -> passed.
  - `./quality-test.sh` -> passed.
  - `./typecheck-test.sh` -> passed.
  - `SCOPE_ALLOW_SHARED=1 make ci` -> passed.
- Checkpoint status:
  - plan complete
  - first green tests: `./quality-test.sh` passed (`Ran 104 tests`, `OK`)
  - ready for handoff: all required local gates passed with the approved shared-file override
- Risks/blockers:
  - Shared-test approval still needs the explicit scope override in this branch lane.
  - No integrator-locked or shared-by-approval source files remain in the submitted diff.
- Roadmap item(s) affected:
  - `Milestone 1 - Bootstrap Flow Stabilization: context basket and vault persistence hardening.`
- Vision capability affected:
  - `Capability 1 - Local-first state and identity.`
- Routing/provider impact note: None.
- Proposed `README.md` patch text: None.
- Scope-check / ownership note:
  - Approved shared test-file exception only: `YES`
  - Shared-by-approval source edits: `NO`
  - Integrator-locked edits: `NO`
