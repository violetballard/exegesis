## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Feature implementation commit: `36893f06df85409c4595d64adb8af60455c086a6`
- Deferred-policy cleanup commit: `dc8f79e4abeb30de51854fdd84d35b97993955b8`
- Current handoff alignment commit: `203906231e9c47371b6d7bc4028bc4f60e764581`
- Reviewed commit type: Docs-only handoff alignment; no retrieval code changes in this commit.

## Scope Goal

Document the retrieval handoff boundary while keeping the current commit strictly limited to docs-only handoff alignment.

## Scope Completed

This commit updates the handoff artifacts only. It states that the reviewed retrieval implementation lives in `36893f06df85409c4595d64adb8af60455c086a6`, that the deferred-policy boundary lives in `dc8f79e4abeb30de51854fdd84d35b97993955b8`, and that `203906231e9c47371b6d7bc4028bc4f60e764581` does not add retrieval code changes. The packet keeps the file list restricted to the docs files actually changed here, removes any stale cross-lane retrieval-tool claim, states the owned retrieval behavior as FTS-first for `vault`, `collection:`, and `doc:` scopes, and documents `section:` as an intentional compatibility boundary until fallback support exists. PageIndex and embeddings references remain deferred-only history, and the roadmap/vision mapping stays scoped to the docs-only handoff boundary rather than claiming feature delivery in this commit.

## Compatibility Note

`section:` scopes remain intentionally rejected in the owned retrieval service until section fallback support exists. Callers that depend on section targeting must switch to `vault`, `collection:`, or `doc:` scopes for the current FTS-first MVP path.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `NO`

## Code-Diff Evidence

- `.codex/kickoff_packets/feat-retrieval-fts.md`: re-anchors the handoff metadata to the actual commit boundary.
- `.codex/lane_meta/feat-retrieval-fts.json`: mirrors the same scope and file-list correction in structured form.
- `THREAD_PACKET.md`: records the docs-only nature of this commit and the earlier implementation/cleanup commits it points to.

### Prior commit references

- Reviewed code files:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Cleanup boundary file:
  - `src/qual/engine/retrieval/policy.py`
- Handoff-only artifacts updated in this fix commit:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
- Tasks completed:
  1. Re-anchored the packet to the earlier retrieval implementation and deferred-policy cleanup commits.
  2. Marked the current commit as docs-only and removed claims that it delivered retrieval code changes.
  3. Removed the stale cross-lane retrieval-tool reference from the handoff surface.
  4. Kept the file list restricted to the docs files actually changed in this commit.
  5. Tightened the roadmap and vision mapping so it describes the handoff boundary rather than feature delivery.
  6. Documented the section-scope compatibility boundary for the current FTS-first MVP path.
- Files changed:
  - Handoff-only artifacts:
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
  - `#3` added a concrete `Scope completed` paragraph describing the docs-only handoff alignment.
  - `#4` removed the stale cross-lane retrieval-tool claim from the handoff surface.
  - `#5` tightened the roadmap/vision mapping to describe the handoff boundary rather than feature delivery.
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
