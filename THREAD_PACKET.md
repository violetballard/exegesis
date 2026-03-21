## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Feature implementation commit: `36893f06df85409c4595d64adb8af60455c086a6`
- Deferred-policy cleanup commit: `dc8f79e4abeb30de51854fdd84d35b97993955b8`
- Current handoff alignment commit: `f137c7c818f4da705a9f98bdf2b03e991924e636`
- Reviewed commit type: Docs-only handoff alignment; no retrieval code changes in this commit.

## Scope Goal

Document the retrieval handoff boundary while keeping the current commit strictly limited to docs-only handoff alignment.

## Scope completed

Delivered behavior: FTS-first retrieval is active for `vault`, `collection:`, and `doc:` scopes. `src/qual/retrieval/service.py` forwards those queries to the owned retrieval engine, `src/qual/retrieval/__init__.py` exposes the retrieval helper wrappers for the owned retrieval package, and `src/qual/engine/retrieval/policy.py` keeps `fts` active while leaving `pageindex` and `embeddings` deferred. `section:` remains rejected until fallback support exists.

## Files changed

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/policy.py`

## Compatibility Note

Breaking compatibility note: `section:` scopes remain intentionally rejected in the owned retrieval service until section fallback support exists. Callers that depend on section targeting must switch to `vault`, `collection:`, or `doc:` scopes for the current FTS-first MVP path.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `NO`
- Non-owned source files promoted: `NO`

## Code-Diff Evidence

- `src/qual/retrieval/service.py`: routes retrieval queries through the FTS-first engine path.
- `src/qual/engine/retrieval/__init__.py`: exposes the canonical FTS-first retrieval surface.
- `src/qual/engine/retrieval/policy.py`: defines the active FTS strategy and deferred strategies.
- Roadmap/vision mapping: documents the Milestone 4 retrieval boundary while keeping `PageIndex` and embeddings out of the required MVP path.

### Prior commit references

- Handoff files updated for this packet:
  - `src/qual/retrieval/service.py`
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/policy.py`
- Tasks completed:
  1. Re-anchored the packet to the retrieval feature commit and kept the lane-owned file list narrow.
  2. Added a concrete `Scope completed` section describing the delivered retrieval behavior.
  3. Rewrote `Files changed` so it only lists the lane-owned retrieval source files.
  4. Preserved the roadmap and vision mapping while keeping `PageIndex` and embeddings deferred.
  5. Documented the `section:` compatibility boundary for the current FTS-first MVP path.
- Files changed:
  - `src/qual/retrieval/service.py`
  - `src/qual/engine/retrieval/__init__.py`
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
  - `#1` keeps the handoff surface limited to the owned retrieval lanes.
  - `#2` adds a concrete `Scope completed` section describing the delivered retrieval behavior.
  - `#3` rewrites `Files changed` so it only lists the lane-owned retrieval source files.
  - `#4` tightens the roadmap/vision mapping to describe the retrieval MVP boundary rather than handoff mechanics.
  - `#5` documents the `section:` compatibility boundary for the current FTS-first MVP path.
- Checkpoint status:
  - plan complete
  - first green tests: `./quality-test.sh` passed
  - ready for handoff: all required local gates passed
- Risks/blockers:
  - No blockers.
  - The earlier retrieval implementation remains in `36893f06df85409c4595d64adb8af60455c086a6`.
- Compatibility note:
  - `section:` scopes are intentionally rejected in the owned retrieval service until section fallback support exists. Callers that depend on section targeting must switch to `vault`, `collection:`, or `doc:` scopes for the current FTS-first MVP path.
- Roadmap item(s) affected:
  - Milestone 4: Retrieval Layer -> FTS-first ingestion/index path for context/vault documents
- Vision capability affected:
  - 2. Retrieval-first context handling
- Routing/provider impact note: None.
- Proposed `README.md` patch text: None.
