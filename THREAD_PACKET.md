## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet HEAD role: `metadata-only reviewer-fix traceability refresh`
- Current branch head before this fixer commit: `5ba8277e6be62cf7851281e1a95e951f51a65d45`
- Reviewed implementation head: `7d2774e6b2d4775241283c81edac802e4a7fca2d`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..7d2774e6b2d4775241283c81edac802e4a7fca2d`
- Handoff type: `shared/high-risk retrieval handoff for the actual implementation tip plus later metadata-only packet refreshes`

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
- This reviewed implementation range advances the Milestone 3 engine-first canonical demo-path step `retrieve relevant material` by hardening FTS-only excerpt retrieval and deterministic provenance on the canonical engine retrieval surface.
- PageIndex and embeddings remain deferred compatibility paths only; this handoff does not widen them into required MVP runtime retrieval paths.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path across the reviewed implementation range.
- The reviewed retrieval contract explicitly strengthens `retrieve relevant material` on the canonical engine-facing retrieval path.
- Retrieval query construction, payload normalization, citation/provenance bundles, and sparse source/context rehydration stay deterministic for downstream engine flows using the canonical retrieval facade.
- `RetrievalService.fetch_excerpt()` now resolves through the canonical FTS-only lookup path, so PageIndex-only excerpt IDs fail closed instead of reviving PageIndex as a required runtime path.
- `FTSStrategy` now canonicalizes query-shaped cache keys and candidate doc scopes, so semantically equivalent FTS requests reuse the same one-entry cache deterministically while preserving FTS-first behavior.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` covers the fail-closed excerpt contract, deterministic retrieval payload behavior, and the FTS cache scope canonicalization behavior at `7d2774e6b2d4775241283c81edac802e4a7fca2d`.
- PageIndex and embeddings remain deferred compatibility paths rather than required MVP retrieval strategies.

## Reviewer fix reconciliation
- Required fix 1 is satisfied by anchoring the handoff packet to the true reviewed implementation head `7d2774e6b2d4775241283c81edac802e4a7fca2d` while treating later packet-only commits as metadata-only refreshes.
- Required fix 2 is satisfied by classifying `7d2774e6` as retrieval implementation work, not metadata-only work, and by naming `src/qual/engine/retrieval/fts_strategy.py` in the reviewed file list.
- Required fix 3 is satisfied by re-stating roadmap and product alignment for the true scope: FTS-only excerpt lookup plus cache-key canonicalization strengthen the Milestone 3 `retrieve relevant material` step without widening beyond FTS-first MVP retrieval.
- Required fix 4 is satisfied by naming the canonical demo-path step advanced in its own section.
- Required fix 5 is satisfied by rerunning the required gates on the corrected packet branch tip in this fixer pass.

## Authoritative re-review note
- `THREAD_PACKET.md` is the authoritative handoff packet for this fixer pass.
- It carries the reviewer-required canonical demo-path statement, shared/high-risk budget framing, and the true reviewed implementation head `7d2774e6b2d4775241283c81edac802e4a7fca2d`.
- The mirrored `.codex` packet files remain read-only in this worktree, so re-review should use this packet as the source of truth for the corrected handoff metadata.
- Later packet-only commits after `7d2774e6b2d4775241283c81edac802e4a7fca2d`, including `5ba8277e6be62cf7851281e1a95e951f51a65d45`, remain metadata-only unless this packet is regenerated again.

## Approved exception note
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Tasks completed
1. Hardened the canonical FTS-first retrieval surface in `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`, including deterministic payload/provenance shaping and FTS-only excerpt lookup behavior.
2. Canonicalized FTS cache keys and candidate-doc scope handling in `src/qual/engine/retrieval/fts_strategy.py` so equivalent FTS-first requests share stable FTS cache entries without widening retrieval scope.
3. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the FTS-only excerpt contract, deterministic retrieval payload behavior, and FTS cache scope canonicalization.
4. Regenerated the handoff packet so scope completed, files changed, roadmap/vision alignment, and the canonical demo-path step all match the actual reviewed implementation head.

## Files changed
### Reviewed implementation files
- `src/qual/retrieval/service.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)
### Metadata-only handoff files
- `THREAD_PACKET.md`
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

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
