## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet HEAD role: `metadata-only reviewer-fix handoff refresh`
- Reviewed implementation head: `ad711fd427137a06dcf32ec7e3a692a179747f6e`
- Reviewed implementation range: `7d2774e6b2d4775241283c81edac802e4a7fca2d..ad711fd427137a06dcf32ec7e3a692a179747f6e`
- Docs-only alignment commits before this refresh:
  - `5ba8277e6be62cf7851281e1a95e951f51a65d45`
  - `2e81a35925b07898c0d2738d1296be22c824a93d`
  - `c511415bc1681be7e70ebc2bd212dbeb592c60ab`
- Handoff type: `shared/high-risk retrieval handoff for the actual implementation tip with a metadata-only packet refresh`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## High-risk kickoff alignment
- Risk reason: approved shared regression coverage in `tests/unit/test_unified_retrieval.py` makes this shared/high-risk work under `AGENTS.md`.
- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

## Canonical demo-path step advanced
- `retrieve relevant material`
- This reviewed implementation range makes `retrieve relevant material` more real by removing the PageIndex fallback from `fetch_excerpt`, preserving the canonical FTS-only excerpt lookup path, and keeping excerpt lookup fail-closed when the excerpt was not produced by the authoritative FTS path.
- PageIndex and embeddings remain deferred compatibility paths only; this handoff does not widen them into required MVP runtime retrieval paths.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path across the reviewed implementation range.
- Added `retrieve_auto_excerpt` through both retrieval facades so canonical excerpt lookup stays reachable from the FTS-first auto retrieval surface.
- Hardened retrieval snapshot copy safety so sparse source, citation, and excerpt payloads deep-copy nested structures deterministically for downstream engine flows.
- Normalized sparse excerpt provenance fields inside `RetrievalService._normalize_excerpt_payload`, including confidentiality profile, candidate counts, ranks, and section-hint metadata.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` covers the auto excerpt alias, copy-safe snapshot behavior, and sparse excerpt metadata normalization.
- PageIndex and embeddings remain deferred compatibility paths rather than required MVP retrieval strategies.

## Reviewer fix reconciliation
- Required fix 1 is satisfied by anchoring the handoff packet to the true reviewed implementation head `ad711fd427137a06dcf32ec7e3a692a179747f6e`.
- Required fix 2 is satisfied by including the real runtime/test follow-up range `7d2774e6b2d4775241283c81edac802e4a7fca2d..ad711fd427137a06dcf32ec7e3a692a179747f6e`, including `bcaec3c4`, `4640aa40`, and `ad711fd4`.
- Required fix 3 is satisfied by reconciling budget, risk, tasks completed, and files changed with the real high-risk slice instead of the stale `adfa8c` packet story.
- Required fix 4 is satisfied by keeping this refresh explicitly metadata-only rather than describing runtime-changing commits as docs-only.
- Required fix 5 is satisfied by rerunning the required gates on this packet refresh worktree before handoff.

## Authoritative re-review note
- `THREAD_PACKET.md` is the authoritative handoff packet for this fixer pass.
- It carries the reviewer-required canonical demo-path statement, shared/high-risk budget framing, and the true reviewed implementation head `ad711fd427137a06dcf32ec7e3a692a179747f6e`.
- The mirrored `.codex` packet files remain permission-locked in this worktree, so `THREAD_PACKET.md` is the authoritative corrected handoff packet for this fixer pass.
- This refresh commit is metadata-only; if a later branch tip changes retrieval code or `tests/unit/test_unified_retrieval.py`, the packet must be regenerated again.

## Approved exception note
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Tasks completed
1. Added `retrieve_auto_excerpt` through the package and engine retrieval facades so the canonical FTS-first excerpt lookup surface is reachable from the auto retrieval API.
2. Hardened retrieval snapshot copy safety so sparse source, citation, and excerpt payloads deep-copy nested structures deterministically.
3. Normalized sparse excerpt provenance fields in `RetrievalService._normalize_excerpt_payload` so confidentiality profile, candidate counts, ranks, and section-hint metadata retain canonical types.
4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the auto excerpt alias, snapshot copy safety, and sparse excerpt metadata normalization.

## Files changed
### Reviewed implementation files
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)
### Metadata-only handoff files
- `THREAD_PACKET.md`

## Commands run and outcomes
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks/blockers
- Risk: `HIGH`
- Blockers: none

## Roadmap item(s) affected
- `ROADMAP.md`: `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: authoritative FTS-first retrieval feeding the engine loop

## Vision capability affected
- `2. Retrieval-first context handling`
- `3. Canonical engine contract`
- `6. Auditable state and workflow`

## Routing/provider impact note
- None

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (approved `tests/unit/test_unified_retrieval.py` regression coverage only)
