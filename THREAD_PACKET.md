# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `actual-branch-tip handoff with metadata-only refresh`
- Current branch tip before this packet refresh commit: `c8df93427a6974883518f7857b015fb7424795ce`
- Reviewed implementation head: `c8df93427a6974883518f7857b015fb7424795ce`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..c8df93427a6974883518f7857b015fb7424795ce`
- Canonical demo-path step advanced: `retrieve relevant material`
- Canonical demo-path statement: This branch advances `retrieve relevant material` by keeping excerpt lookup, evidence context, and basket-promotion inputs on deterministic, auditable SQLite FTS-backed payloads that are suitable for later promotion without reintroducing PageIndex or embeddings as required retrieval paths.

## Scope Goal

- Regenerate the handoff packet against the actual branch-tip implementation, include the post-`adfa8cda` retrieval changes in scope, and rerun the required gates for the exact handoff content.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: hand off the real branch-tip retrieval implementation through `c8df9342` and keep the packet refresh itself limited to metadata files.
- Risk reason: this branch includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py` and branch-tip support changes in `codex_packet_handoff/tools/planner.py`, so the handoff is treated as high-risk and summarized under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the packet to the real branch-tip implementation range `d7fd5d20..c8df9342`.
2. State explicitly that this work advances `retrieve relevant material`.
3. Tighten the scope summary so the post-`adfa8cda` retrieval changes are justified as deterministic FTS payload/provenance work for the Milestone 4 path.
4. Rerun and report `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` for the exact handoff content.

### Checkpoint Status

- `plan complete`: the handoff is re-anchored to `d7fd5d20..c8df9342`.
- `first green tests`: recorded after rerunning the required gate stack for this handoff refresh.
- `before risky/shared file edit`: the branch still includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the reviewer-facing packet files and gate summary agree on the same implementation head, implementation range, and file inventory.

## Scope Completed

- Kept SQLite FTS authoritative for the excerpt-lookup surface and the engine/public retrieval facades; PageIndex and embeddings remain compatibility-only shims that fail closed rather than becoming routing-authoritative paths.
- Hardened deterministic retrieval payloads across `src/qual/retrieval/service.py` and `src/qual/engine/retrieval/payload.py`, including normalized query snapshots, confidentiality/redaction handling, ranked-hit metadata, provenance fingerprints, and nested excerpt-query metadata.
- Preserved deterministic sparse source/context bundle rehydration and basket-promotion inputs so later promotion can consume auditable excerpt payloads without reconstructing ambiguous retrieval state.
- Updated `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` so packet emission stays attached to the actual reviewed tip instead of silently drifting to a narrowed or stale slice.
- This handoff stays scope-tight even though it is broader than the earlier `adfa8cda` slice: the additional retrieval commits are still all in service of the Milestone 4 FTS-first path and do not restore PageIndex or embeddings as required runtime retrieval strategies.

## Reviewed Scope Boundary

- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..c8df93427a6974883518f7857b015fb7424795ce`
- Reviewed implementation files:
- `codex_packet_handoff/tools/planner.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_unified_retrieval.py`
- Current metadata-only packet refresh files:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Kept the excerpt-lookup entrypoints FTS-first and fail-closed while exporting the canonical helpers through the retrieval facades.
2. Normalized retrieval payloads, provenance, ranked-hit snapshots, query constraints, confidentiality metadata, and nested excerpt-query state so downstream engine consumers receive deterministic audit-friendly data.
3. Preserved deterministic sparse source/context bundle and basket-promotion backfills without widening runtime retrieval authority beyond SQLite FTS.
4. Reattached packet/planner traceability to the real branch tip and refreshed the reviewer-facing handoff metadata to cover the full non-metadata implementation through `c8df9342`.

## Files Changed

- Reviewed implementation files in `d7fd5d200358287fa42a18d39e2b277463b9b69f..c8df93427a6974883518f7857b015fb7424795ce`:
- `codex_packet_handoff/tools/planner.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_unified_retrieval.py`
- Current metadata-only packet refresh files:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The packet now covers the actual non-metadata branch-tip implementation through `c8df93427a6974883518f7857b015fb7424795ce`; it no longer presents `adfa8cda` as the effective reviewed head.
2. `Files changed`, `Scope completed`, and the reviewed range now include the post-`adfa8cda` retrieval code changes and the branch-tip packet-planner support changes.
3. The packet explicitly states which canonical demo-path step this work advances: `retrieve relevant material`.
4. The scope statement stays tight by classifying the added retrieval work as deterministic FTS payload/provenance/basket-promotion support for the Milestone 4 retrieval path.
5. The current refresh commit is metadata-only only because its diff is limited to packet files; the reviewed implementation remains the full branch-tip code through `c8df9342`.

## Risks / Blockers

- Remaining risks: the branch includes packet-planner support outside the lane-owned retrieval paths, but it is isolated to handoff traceability and covered by `tests/unit/test_packet_planner.py`.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 4: Retrieval Layer`
- `MVP Focus Through 2026-05-04: feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`
- Deterministic FTS excerpt payloads now remain suitable for later basket promotion without ambiguous fallback state.

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
- The non-lane support files in the reviewed implementation range are `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py`; they exist to keep packet emission aligned with the actual reviewed tip and do not alter provider routing behavior.
