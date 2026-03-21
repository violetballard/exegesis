## Thread Handoff Packet

- Branch name: `codex/feat-context-storage`
- Reviewed commit: `8c4dfc5ea3370d7b354881bb889a66147d5d769c`
- Scope goal: Harden context basket and vault persistence recovery so malformed optional metadata is salvaged and rewritten without discarding valid local state, and cover that recovery contract with focused tests.
- Scope completed: Updated context basket recovery to treat malformed optional metadata as salvageable while still rejecting unrecoverable schema or item-id payloads.
- Scope completed: Updated vault state recovery to preserve valid lock and project state when optional metadata fields are malformed, then rewrite normalized persisted state.
- Scope completed: Normalized context basket item-id handling so mixed invalid entries can be salvaged and rewritten instead of forcing a full discard.
- Scope completed: Added focused metadata-only corruption tests for both context basket and vault persistence paths, including backup-promotion recovery cases and invalid project-name metadata.
- Tasks completed:
  1. Updated context basket recovery to treat malformed optional metadata as salvageable while still rejecting unrecoverable schema or item-id payloads.
  2. Updated vault state recovery to preserve valid lock and project state when optional metadata fields are malformed, then rewrite normalized persisted state.
  3. Normalized context basket item-id handling so mixed invalid entries can be salvaged and rewritten instead of forcing a full discard.
  4. Added focused metadata-only corruption tests for both context basket and vault persistence paths, including backup-promotion recovery cases.
  5. Added a focused vault regression test for invalid project-name metadata so valid lock state is preserved safely and rewritten instead of being treated as unrecoverable corruption.
  6. Re-ran scope, format, lint, unit, typecheck, and CI gates on the reviewed branch head and confirmed they all pass.
- Files changed:
  - `src/qual/context/basket.py`
  - `src/qual/context/set_store.py`
  - `src/qual/context/store.py`
  - `src/qual/storage/vault.py`
  - `tests/unit/test_context_storage_recovery.py`
- Shared/integrator-locked edits:
  - `YES` - `tests/unit/test_context_storage_recovery.py` is approved shared recovery coverage; no integrator-locked source files were touched.
- Commands run with results:
  - `git show --stat --name-only --oneline 8c4dfc5e` -> confirmed the reviewed feature commit spans the context/storage recovery source and test updates
  - `git show --unified=0 --format=medium 8c4dfc5e -- src/qual/context/basket.py src/qual/context/set_store.py src/qual/context/store.py src/qual/storage/vault.py tests/unit/test_context_storage_recovery.py` -> confirmed the feature diff matches the recovery scope described above
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed (`Ran 145 tests`, `OK`)
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- Reviewer fix closure:
  - `#1` repointed the handoff at the actual feature commit instead of the docs-only packet commit.
  - `#2` made `Files changed` match the real recovery source/test diff and removed the packet-only file from that list.
  - `#3` called out the approved shared test coverage explicitly so the ownership note is self-consistent.
  - `#4` kept the scope tied to `feat-context-storage` work in owned paths plus the approved shared test file.
- Checkpoint status:
  - plan complete
  - first green tests: `./quality-test.sh` passed (`Ran 145 tests`, `OK`)
  - ready for handoff: all required local gates passed
- Risks/blockers:
  - None.
- Roadmap item(s) affected:
  - Milestone 1 - Bootstrap Flow Stabilization: context basket and vault persistence hardening.
  - Milestone 2 - Test Hardening: focused recovery coverage for metadata-only corruption and salvage behavior.
- Vision capability affected:
  - Capability 1 - Local-first state and identity.
  - Capability 3 - Auditable generation through deterministic recovery and rewrite behavior for persisted local state.
- Routing/provider impact note:
  - None.
