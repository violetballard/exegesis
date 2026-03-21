## Thread Handoff Packet

- Branch name: `codex/feat-context-storage`
- Scope goal: Deliver the current context-storage recovery fix in `src/qual/context/store.py` while keeping the handoff scope-tight and limited to the approved recovery test outside owned paths.
- Scope completed: Hardened context basket recovery so malformed item-id entries are dropped, the remaining valid IDs are rewritten canonically, and the approved recovery regression coverage stays aligned with the branch diff.
- Tasks completed:
  1. Taught `ContextBasketStore` to treat dropped item-id entries as rewrite-worthy during recovery so the persisted payload is normalized even when the remaining IDs already match.
  2. Added a regression test proving invalid item-id entries force a primary rewrite and refresh the timestamp.
  3. Added a regression test proving invalid backup item-id entries are refreshed from the recovered primary state without rewriting the healthy primary.
  4. Resubmitted the handoff packet so the listed files and exception note match the actual owned-path diff exactly.
- Files changed:
  - `src/qual/context/store.py`
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
  - first green tests: `./quality-test.sh` passed (`Ran 75 tests`, `OK`)
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
