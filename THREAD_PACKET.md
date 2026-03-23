## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed commit(s):
  - `36893f06df85409c4595d64adb8af60455c086a6`
  - `dc8f79e4abeb30de51854fdd84d35b97993955b8`
  - `f0047257cf71b750a576de84c272c0f8c5875148`
- Deferred-policy cleanup commit: `dc8f79e4abeb30de51854fdd84d35b97993955b8`
- Metadata-only follow-up commit:
  - `34dfec2f59175850da3d33e8e50b3641f1256b49`

## Scope Goal

Document the retrieval handoff boundary while keeping the lane-owned retrieval scope constrained to the reviewed implementation commit set and excluding out-of-lane tooling edits.

## Scope completed

The packet now names the reviewed implementation commit set separately from the metadata-only follow-up commit, so the handoff audit trail no longer implies that `34dfec2f59175850da3d33e8e50b3641f1256b49` is feature payload. The correction itself stays within the handoff artifacts only.

## Files changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Reviewed implementation files

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/policy.py`
- `src/qual/retrieval/service.py`

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `NO`
- Non-owned source files promoted: `NO`
- No out-of-lane tooling files are included in this correction commit.

## Tasks completed

1. Added an explicit reviewed commit-set field so the implementation bundle is auditable.
2. Separated the metadata-only follow-up commit from the feature payload.
3. Rewrote `Files changed` so it matches the correction commit's handoff artifacts.
4. Kept the reviewed implementation files listed separately for traceability.

## Commands run with results

- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed

## Risks/blockers

- No blockers.
- The earlier retrieval implementation remains in `36893f06df85409c4595d64adb8af60455c086a6` and the metadata-only follow-up remains separate.

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
