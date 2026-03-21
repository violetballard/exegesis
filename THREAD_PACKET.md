## Thread Handoff Packet

- Branch name: `codex/feat-context-storage`
- Scope goal: Correct the handoff packet so it matches the actual `src/qual/context/store.py` recovery fix on this branch.
- Scope completed: Rewrote `THREAD_PACKET.md` to describe the context-basket persistence recovery change in `src/qual/context/store.py`: stale quarantine is cleared when an empty basket carries malformed metadata, and empty tmp payloads do not override backup recovery.
- Tasks completed:
  1. Reframed the packet around the actual `src/qual/context/store.py` and `tests/unit/test_context_storage_recovery.py` change set.
  2. Replaced the stale vault/set-store/basket narrative with the real empty-basket quarantine cleanup and backup-recovery precedence behavior.
  3. Updated `Files changed` to match the actual diff only.
  4. Aligned the scope-completed bullets with the regression tests for empty-basket malformed metadata recovery and backup precedence.
- Files changed:
  - `src/qual/context/store.py`
  - `tests/unit/test_context_storage_recovery.py`
- Commands run with results:
  - `git show --stat --name-only --oneline HEAD` -> confirmed the reviewed commit changes `src/qual/context/store.py` and `tests/unit/test_context_storage_recovery.py`
  - `git show --unified=0 --format=medium HEAD -- src/qual/context/store.py tests/unit/test_context_storage_recovery.py` -> confirmed the commit changes the quarantine guard and adds the empty-basket malformed-metadata regression test
  - `SCOPE_ALLOW_SHARED=1 make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed (`Ran 145 tests`, `OK`)
  - `./typecheck-test.sh` -> passed
  - `SCOPE_ALLOW_SHARED=1 make ci` -> passed
- Reviewer fix closure:
  - `#1` rewrote the packet around the actual `src/qual/context/store.py` scope.
  - `#2` replaced the stale vault/set-store/basket claims with the empty-basket quarantine cleanup behavior.
  - `#3` kept the files-changed list to the real diff only.
  - `#4` aligned the scope-completed bullets with the added regression tests for malformed empty-basket metadata and backup precedence.
- Checkpoint status:
  - plan complete
  - first green tests: `./quality-test.sh` passed (`Ran 145 tests`, `OK`)
  - ready for handoff: all required local gates passed
- Risks/blockers:
  - None.
- Roadmap item(s) affected:
  - `Context basket persistence recovery hardening`
- Vision capability affected:
  - `Project-scoped context basket with safe recovery behavior`
- Routing/provider impact note:
  - None.
