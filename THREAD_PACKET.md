# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Current submitted tip before this packet refresh commit: `764dc41208453059a2a8c96502a092b6676d4fd2`
- Reviewed implementation head: `9d9e11a1929dc56e44f5a4d459aa385e7a6ce1e5`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..9d9e11a1929dc56e44f5a4d459aa385e7a6ce1e5`
- Packet traceability note: review this lane against the cumulative implementation range above. That range includes the substantive post-`adfa8cda` retrieval commits, including `a96043fee95c3be1b69fba0148e6fdbb5d1d51a9` and `9d9e11a1929dc56e44f5a4d459aa385e7a6ce1e5`. This fixer commit is metadata-only and does not broaden retrieval scope beyond `378cf9a7..9d9e11a1`.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: This work makes the `retrieve relevant material` step more real by ensuring excerpt lookup fails closed to the canonical FTS-backed retrieval path and returns deterministic provenance only for FTS hits.
- Evidence note: `tests/unit/test_unified_retrieval.py` covers both the canonical/public FTS excerpt helpers and the fail-closed excerpt contract, while the cumulative reviewed range also carries the sparse-hit query-constraint preservation fixes in `src/qual/engine/retrieval/payload.py`.
- Packet authority note: this top-level packet and [docs/gate_passed.txt](/Users/doctor-violet/.codex/worktrees/rfts/qual/docs/gate_passed.txt:1) are the reviewer-facing source of truth for the corrected reviewed range, demo-path mapping, and gate results on this branch. The mirrored `.codex/*` packet artifacts remain read-only in this worktree, so they are supporting context rather than the writable handoff source of truth for this fixer pass.

## Scope Goal

- Re-emit the retrieval handoff truthfully against the real reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..9d9e11a1929dc56e44f5a4d459aa385e7a6ce1e5`, state explicitly that this work advances `retrieve relevant material`, record that the mirrored `.codex/*` packet artifacts are read-only in this worktree, and keep this final fixer commit metadata-only on top of `764dc41208453059a2a8c96502a092b6676d4fd2`.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the reviewer packet without widening the lane beyond the real cumulative retrieval implementation already present on the branch tip.
- Risk reason: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Move the reviewed implementation head and range to the real branch-tip retrieval implementation.
2. Replace the stale metadata-only narrative with truthful cumulative traceability.
3. State the canonical demo-path step explicitly as `retrieve relevant material`.
4. Re-run the required gates and record results against the corrected reviewed range.

### Checkpoint Status

- `plan complete`: the packet stays anchored to the real reviewed implementation head `9d9e11a1929dc56e44f5a4d459aa385e7a6ce1e5` while refreshing the writable handoff artifacts on top of `764dc41208453059a2a8c96502a092b6676d4fd2`.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- `before risky/shared file edit`: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the top-level packet and gate summary agree on the same reviewed implementation head, reviewed range, risk class, and demo-path statement.

## Scope Completed

- Kept excerpt lookup on the canonical FTS-only path so PageIndex-only excerpt IDs fail closed.
- Preserved mirrored query constraints in deterministic sparse hit/source/context payloads so retrieval state remains auditable downstream.
- Kept retrieval FTS-first and left PageIndex plus embeddings as compatibility-only fallback shims rather than required runtime paths.
- Regenerated the reviewer-facing handoff against the real cumulative implementation range instead of the stale `adfa8cda`-anchored slice.

## Reviewed Scope Boundary

- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..9d9e11a1929dc56e44f5a4d459aa385e7a6ce1e5`
- Reviewed implementation files:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `docs/gate_passed.txt`
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
- Metadata-only packet refresh files in this fixer commit:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Corrected the reviewed implementation head and range so the packet now includes the substantive post-`adfa8cda` retrieval commits through `9d9e11a1929dc56e44f5a4d459aa385e7a6ce1e5`.
2. Replaced the false metadata-only branch-history claim with truthful cumulative traceability and the real file list.
3. Added the explicit canonical demo-path statement naming `retrieve relevant material` and tying it to the FTS-first excerpt and sparse-payload contract.
4. Re-ran the required gate suite on top of this metadata-only packet refresh and recorded the `.codex/*` permission constraint in the authoritative packet.

## Files Changed

- Reviewed implementation files in `378cf9a74a3658058079a32f186fcd254c4a4034..9d9e11a1929dc56e44f5a4d459aa385e7a6ce1e5`:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `docs/gate_passed.txt`
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
- Metadata-only packet refresh files in this commit:
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

1. The packet now includes the real substantive history after `adfa8cda`, including `a96043f` and `9d9e11a1`.
2. The reviewed file list is now the real cumulative file set for `378cf9a7..9d9e11a1`; the fake metadata-only implementation file list is gone.
3. The packet names the canonical demo-path step directly as `retrieve relevant material` and explains how this range makes that step more real.
4. This final fixer commit is metadata-only, so the corrected packet cleanly separates the reviewed implementation head `9d9e11a1` from the handoff-refresh commit that follows it.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: retrieval/search

### Canonical demo-path step advanced

- `retrieve relevant material`
- This work makes the `retrieve relevant material` step more real by ensuring excerpt lookup fails closed to the canonical FTS-backed retrieval path and returns deterministic provenance only for FTS hits.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
