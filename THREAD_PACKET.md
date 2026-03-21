## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Feature implementation commit: `36893f06df85409c4595d64adb8af60455c086a6`
- Deferred-policy cleanup commit: `dc8f79e4abeb30de51854fdd84d35b97993955b8`
- Current handoff alignment commit: `203906231e9c47371b6d7bc4028bc4f60e764581`
- Reviewed commit type: Docs-only handoff alignment; no retrieval code changes in this commit.

## Scope Goal

Document the retrieval handoff boundary while keeping the current commit strictly limited to docs-only handoff alignment.

## Scope completed

This commit updates only the handoff artifacts in lane-owned docs paths. The completed scope is the three packet files: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, and `THREAD_PACKET.md`. It records that the reviewed retrieval implementation lives in `36893f06df85409c4595d64adb8af60455c086a6`, that the deferred-policy boundary lives in `dc8f79e4abeb30de51854fdd84d35b97993955b8`, and that `203906231e9c47371b6d7bc4028bc4f60e764581` does not add retrieval code changes. The handoff keeps the file list restricted to those docs files, states the owned retrieval behavior as FTS-first for `vault`, `collection:`, and `doc:` scopes, and documents `section:` as a compatibility break in the current MVP until fallback support exists. PageIndex and embeddings references remain deferred-only history, and the roadmap/vision mapping stays scoped to the docs-only handoff boundary rather than claiming feature delivery in this commit.

## Compatibility Note

Breaking compatibility note: `section:` scopes remain intentionally rejected in the owned retrieval service until section fallback support exists. Callers that depend on section targeting must switch to `vault`, `collection:`, or `doc:` scopes for the current FTS-first MVP path.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `NO`
- Non-owned source files promoted: `NO`

## Code-Diff Evidence

- `.codex/kickoff_packets/feat-retrieval-fts.md`: re-anchors the handoff metadata to the actual commit boundary.
- `.codex/lane_meta/feat-retrieval-fts.json`: mirrors the same scope and file-list correction in structured form.
- `THREAD_PACKET.md`: records the docs-only nature of this commit and the earlier implementation/cleanup commits it points to.

### Prior commit references

- Handoff-only artifacts updated in this fix commit:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
- Tasks completed:
  1. Re-anchored the packet to the actual commit under review and stated that it is docs-only.
  2. Rewrote `Files changed` so it only lists the docs files changed in this commit.
  3. Added a concrete `Scope completed` section describing the docs-only handoff alignment.
  4. Preserved the roadmap and vision mapping for the earlier retrieval implementation without claiming it landed in this commit.
  5. Documented the `section:` compatibility boundary for the current FTS-first MVP path.
- Files changed:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
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
  - `make ci` re-ran the full gate stack after the docs-only fix.
- Reviewer fix closure:
  - `#1` re-anchored the packet to the actual reviewed commit boundaries and stated that `203906231e9c47371b6d7bc4028bc4f60e764581` is docs-only.
  - `#2` rewrote `Files changed` so it only lists the docs files changed here.
  - `#3` added a concrete `Scope completed` section describing the docs-only handoff alignment.
  - `#4` removed the stale cross-lane retrieval-tool claim from the handoff surface.
  - `#5` tightened the roadmap/vision mapping to describe the handoff boundary rather than feature delivery.
  - `#6` documented the `section:` compatibility boundary for the current FTS-first MVP path.
- Checkpoint status:
  - plan complete
  - first green tests: `./quality-test.sh` passed
  - ready for handoff: all required local gates passed
- Risks/blockers:
  - No blockers.
  - The earlier retrieval implementation remains in `36893f06df85409c4595d64adb8af60455c086a6`; this commit only documents that boundary.
- Compatibility note:
  - `section:` scopes are intentionally rejected in the owned retrieval service until section fallback support exists. Callers that depend on section targeting must switch to `vault`, `collection:`, or `doc:` scopes for the current FTS-first MVP path.
- Roadmap item(s) affected:
  - Milestone 4: Retrieval Layer -> FTS-first ingestion/index path for context/vault documents
- Vision capability affected:
  - 2. Retrieval-first context handling
- Routing/provider impact note: None.
- Proposed `README.md` patch text: None.
