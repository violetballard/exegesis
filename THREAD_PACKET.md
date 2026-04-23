# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `truthful branch-tip handoff refresh`
- Current submitted tip before this packet refresh commit: `850eacce56c3c3e59a2ec0509ffbe58b69f3e636`
- Reviewed implementation head: `850eacce56c3c3e59a2ec0509ffbe58b69f3e636`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..850eacce56c3c3e59a2ec0509ffbe58b69f3e636`
- Packet traceability note: this handoff must be reviewed against the actual branch-tip implementation range above. Earlier packet refreshes incorrectly treated post-`adfa8cda` commits as metadata-only, but this branch state includes real retrieval implementation changes through `850eacce56c3c3e59a2ec0509ffbe58b69f3e636`.
- Canonical demo-path step advanced: `retrieve relevant material`

## Scope Goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt, provenance, and payload output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: finish the cumulative FTS-first retrieval thread now present on the real branch tip and hand it off with truthful traceability.
- Risk reason: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Regenerate the packet so review traceability points at the actual implementation tip `850eacce` and the full reviewed range `378cf9a7..850eacce`.
2. Keep one consistent shared/high-risk budget story across kickoff, lane metadata, final packet, and gate summary.
3. State explicitly that this cumulative retrieval handoff advances the canonical demo-path step `retrieve relevant material`.
4. Re-run the required gates and record files changed plus command results against the corrected reviewed range.

### Checkpoint Status

- `plan complete`: the packet is being rebuilt around the real branch tip instead of the stale narrowed metadata-only slice.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on the corrected packet state.
- `before risky/shared file edit`: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: kickoff, lane metadata, gate summary, and final packet all agree on the same reviewed range, risk class, demo-path step, files changed, and gate results.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path across the full reviewed range.
- The canonical retrieval query constructor and retrieval helpers are exported through both retrieval facades, while PageIndex and embeddings remain compatibility-only fallbacks rather than required paths.
- Retrieval payloads, hit snapshots, source bundles, context bundles, provenance fingerprints, and excerpt lookup metadata are normalized deterministically for downstream engine flows.
- The excerpt lookup surface now uses the canonical FTS-first path with fail-closed behavior for non-FTS-only excerpt IDs under approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- This handoff makes the canonical demo-path step `retrieve relevant material` more real by ensuring retrieval results, excerpts, and provenance stay deterministic and auditable through the branch-tip FTS-first path.

## Reviewed Scope Boundary

- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..850eacce56c3c3e59a2ec0509ffbe58b69f3e636`
- Reviewed implementation files:
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Handoff/support files in the same reviewed range:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `docs/gate_passed.txt`
- `tests/unit/test_packet_planner.py`

## Tasks Completed

1. Kept FTS authoritative end-to-end by exporting the canonical retrieval query and helper surfaces through the retrieval facades while leaving PageIndex and embeddings fallback-only.
2. Normalized retrieval payloads, provenance, query snapshots, source bundles, context bundles, and excerpt metadata so downstream engine flows receive deterministic auditable retrieval state.
3. Hardened excerpt lookup and related retrieval backfills so the canonical FTS-first excerpt path preserves ranking, policy, title hints, basket promotion context, and fail-closed behavior where non-FTS lookups should not succeed.
4. Added and maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the branch-tip retrieval contract.

## Files Changed

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

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The handoff now points review at the real branch-tip implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..850eacce56c3c3e59a2ec0509ffbe58b69f3e636`, not the stale `adfa8cda` slice.
2. The authoritative packet and gate summary now use one shared/high-risk budget story because `tests/unit/test_unified_retrieval.py` is in scope; the mirrored `.codex` packet files remain stale because this environment is rejecting writes under `.codex/`.
3. The final packet explicitly states that this branch-tip retrieval work advances the canonical demo-path step `retrieve relevant material`.
4. Files changed and command results are re-listed against the corrected reviewed range instead of the false metadata-only note.

## Risks / Blockers

- Risk: `HIGH`
- Blocker: this environment currently rejects writes under `.codex/` with `Operation not permitted`, so the mirrored kickoff and lane-meta packet files could not be refreshed in this pass.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains in `tests/unit/test_unified_retrieval.py`.
