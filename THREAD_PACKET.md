## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Feature implementation commit: `36893f06df85409c4595d64adb8af60455c086a6`
- Deferred-policy cleanup commit: `dc8f79e4abeb30de51854fdd84d35b97993955b8`
- Current handoff alignment commit: `203906231e9c47371b6d7bc4028bc4f60e764581`
- Reviewed commit type: Retrieval feature implementation with deferred-policy cleanup.

## Scope Goal

Document the retrieval handoff boundary while keeping the lane-owned retrieval scope constrained to FTS-first MVP behavior.

## Scope completed

FTS-first retrieval is active for `vault`, `collection:`, and `doc:` scopes. `src/qual/retrieval/service.py` forwards those queries to the owned retrieval engine, `src/qual/engine/retrieval/__init__.py` exposes the canonical retrieval surface, and `src/qual/engine/retrieval/policy.py` keeps `fts` active while leaving `pageindex` and `embeddings` deferred. `section:` remains rejected until fallback support exists. This handoff stays within `src/qual/retrieval/**` and `src/qual/engine/retrieval/**` only.

## Files changed

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/policy.py`

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `NO`
- Non-owned source files promoted: `NO`

## Tasks completed

1. Re-anchored the packet to the retrieval feature commit and kept the lane-owned file list narrow.
2. Added a concrete `Scope completed` section describing the delivered retrieval behavior.
3. Rewrote `Files changed` so it only lists the lane-owned retrieval source files.
4. Kept the changed-file list constrained to `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`.
5. Preserved the roadmap and vision mapping while keeping `PageIndex` and embeddings deferred.
6. Documented the `section:` compatibility boundary for the current FTS-first MVP path.

## Commands run with results

- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed

## Risks/blockers

- No blockers.
- The earlier retrieval implementation remains in `36893f06df85409c4595d64adb8af60455c086a6`.

## Compatibility note

`section:` scopes are intentionally rejected in the owned retrieval service until section fallback support exists. Callers that depend on section targeting must switch to `vault`, `collection:`, or `doc:` scopes for the current FTS-first MVP path.

## Roadmap item(s) affected

- Milestone 4: Retrieval Layer -> FTS-first ingestion/index path for context/vault documents

## Vision capability affected

- 2. Retrieval-first context handling

## Routing/provider impact note

None.

## Proposed `README.md` patch text

None.
