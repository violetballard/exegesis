## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Feature implementation commit: `36893f06df85409c4595d64adb8af60455c086a6`
- Deferred-policy cleanup commit: `dc8f79e4abeb30de51854fdd84d35b97993955b8`
- Current handoff alignment commit: `203906231e9c47371b6d7bc4028bc4f60e764581`
- Reviewed commit type: Retrieval feature implementation with deferred-policy cleanup.

## Scope Goal

Document the retrieval handoff boundary while keeping the lane-owned retrieval scope constrained to FTS-first MVP behavior.

## Scope completed

The delivered retrieval path is FTS-first for `vault`, `collection:`, and `doc:` scopes. `src/qual/retrieval/service.py` routes those queries through the engine-owned FTS path, `src/qual/engine/retrieval/__init__.py` exposes the canonical retrieval surface, and `src/qual/engine/retrieval/policy.py` keeps `fts` as the only active strategy while leaving `pageindex` and `embeddings` deferred. `section:` remains intentionally rejected until fallback support exists.

## Compatibility Note

Breaking compatibility note: `section:` scopes remain intentionally rejected in the owned retrieval service until section fallback support exists. Callers that depend on section targeting must switch to `vault`, `collection:`, or `doc:` scopes for the current FTS-first MVP path.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `NO`
- Non-owned source files promoted: `NO`

## Code-Diff Evidence

- `src/qual/engine/retrieval/__init__.py`: exposes the canonical FTS-first retrieval surface.
- `src/qual/retrieval/service.py`: routes retrieval queries through the FTS-first engine path.
- `src/qual/engine/retrieval/policy.py`: defines the active FTS strategy and deferred strategies.

### Prior commit references

- Reviewed retrieval implementation:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
- Cleanup boundary:
  - `src/qual/engine/retrieval/policy.py`
- Tasks completed:
  1. Re-anchored the packet to the retrieval feature commit and kept the lane-owned file list narrow.
  2. Removed the off-lane retrieval-tool path from the handoff surface.
  3. Added a concrete `Scope completed` section for the delivered FTS-first behavior.
  4. Preserved the roadmap and vision mapping while keeping `PageIndex` and embeddings deferred.
  5. Documented the `section:` compatibility boundary for the current FTS-first MVP path.
- Files changed:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `src/qual/engine/retrieval/policy.py`
- Commit split:
  - implementation: `36893f06df85409c4595d64adb8af60455c086a6`
  - cleanup: `dc8f79e4abeb30de51854fdd84d35b97993955b8`
  - handoff alignment: `203906231e9c47371b6d7bc4028bc4f60e764581`
- Commands run with results:
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- Reviewer fix closure:
  - `#1` removed the off-lane retrieval-tool path from the reviewed handoff surface.
  - `#2` added a concrete `Scope completed` section describing the delivered behavior.
  - `#3` constrained the changed-file list to `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`.
- Checkpoint status:
  - plan complete
  - first green tests: `./quality-test.sh` passed
  - ready for handoff: all required local gates passed
- Risks/blockers:
  - No blockers.
  - `section:` scopes remain intentionally rejected until fallback support exists.
- Roadmap item(s) affected:
  - Milestone 4: Retrieval Layer -> FTS-first ingestion/index path for context/vault documents
- Vision capability affected:
  - 2. Retrieval-first context handling
- Routing/provider impact note: None.
- Proposed `README.md` patch text: None.
