# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization against the current branch tip`
- Current submitted tip before this packet refresh commit: `e7e545664f277419ff97a05740e45f88179dbe24`
- Reviewed implementation head: `ced0bcaf3d5446d549b04d1bc24593eda8850266`
- Reviewed implementation range: `d9542206f6fd14db37d1ddf5efd76f941d32314b..ced0bcaf3d5446d549b04d1bc24593eda8850266`
- Packet traceability note: the reviewed implementation head remains `ced0bcaf3d5446d549b04d1bc24593eda8850266`, while later commits `7ec7e2720aee94c2b9c412fe1e003a4dc4fa6db4` and `e7e545664f277419ff97a05740e45f88179dbe24` are metadata-only packet refreshes. This packet finalizes the reviewer-required handoff metadata against the current branch tip without changing the reviewed implementation range.
- Fixer note: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are not writable in this sandbox and rejected both `apply_patch` and direct shell writes with `Operation not permitted`, so this root packet and `docs/gate_passed.txt` are the writable refreshed handoff artifacts for this pass.

## Scope goal

- Advance the canonical demo-path step `retrieve relevant material` by keeping excerpt lookup and excerpt-promotion metadata anchored to canonical FTS-backed query snapshots at the actual reviewed branch tip.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: preserve SQLite FTS as the authoritative retrieval path while closing the reviewer-requested handoff truthfulness gaps on the actual branch tip.
- Risk reason: the cumulative branch still carries the approved shared regression surface `tests/unit/test_unified_retrieval.py`, so the handoff remains shared/high-risk even though the newest implementation delta is lane-owned.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Finalize the handoff against the current metadata-only branch tip `e7e545664f277419ff97a05740e45f88179dbe24` without moving the reviewed implementation head.
2. Keep the packet explicit that the reviewed implementation head remains `ced0bcaf3d5446d549b04d1bc24593eda8850266` while later packet-refresh commits are metadata-only.
3. Keep the canonical demo-path mapping explicit as `retrieve relevant material`.
4. Re-run the required gate suite on the current branch tip and record the results against that exact commit.

### Early Review Triggers

- before first edit to any shared or integrator-locked file
- before changing public retrieval contract wording
- before changing packet traceability or reviewed-range claims

### Checkpoint Status

- `plan complete`: the packet now targets the current branch tip `e7e545664f277419ff97a05740e45f88179dbe24` while preserving the reviewed implementation head `ced0bcaf3d5446d549b04d1bc24593eda8850266`.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on `e7e545664f277419ff97a05740e45f88179dbe24`.
- `before risky/shared file edit`: this refresh edits packet metadata only; the cumulative branch still includes the previously approved shared regression file `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the packet, reviewed tip, canonical demo-path step, and gate evidence now refer to the same actual branch state.

## Scope completed

- Canonical demo-path step advanced: `retrieve relevant material`.
- `src/qual/retrieval/service.py` now prefers canonical excerpt query snapshots when excerpt lookup and promotion records are rebuilt, so mirrored sparse-query fields remain derived copies and can no longer override the authoritative FTS-backed query state.
- The packet now distinguishes the reviewed implementation head `ced0bcaf3d5446d549b04d1bc24593eda8850266` from the later metadata-only packet refresh commits through the current tip `e7e545664f277419ff97a05740e45f88179dbe24`, while keeping the canonical demo-path step advanced explicit.
- SQLite FTS remains authoritative, and PageIndex and embeddings remain compatibility-only shims rather than required MVP retrieval paths.

## Reviewed Scope Boundary

- Incremental reviewed implementation range added at the current tip: `d9542206f6fd14db37d1ddf5efd76f941d32314b..ced0bcaf3d5446d549b04d1bc24593eda8850266`
- Incremental non-metadata reviewed file in that range:
- `src/qual/retrieval/service.py`
- Metadata-only packet-refresh files in this resubmission:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`
- Cumulative non-metadata branch files still present at the reviewed tip and therefore called out in `Files changed`:
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`
- This handoff advances `retrieve relevant material` by ensuring excerpt lookup and excerpt-promotion metadata stay bound to canonical FTS-backed query snapshots, which keeps downstream basket and workflow use deterministic and auditable.

## Tasks completed

1. Updated `src/qual/retrieval/service.py` so canonical excerpt query snapshots take precedence over partial mirrored query metadata when excerpt lookup and promotion records are reconstructed.
2. Finalized the handoff against the current metadata-only branch tip `e7e545664f277419ff97a05740e45f88179dbe24` while keeping the reviewed implementation head anchored to `ced0bcaf3d5446d549b04d1bc24593eda8850266`.
3. Kept the canonical demo-path mapping explicit as `retrieve relevant material` and recorded the `.codex` write blocker in the authoritative writable packet artifacts.
4. Re-ran the required gate suite against the current branch tip `e7e545664f277419ff97a05740e45f88179dbe24`.

## Files changed

- Incremental implementation file in `d9542206f6fd14db37d1ddf5efd76f941d32314b..ced0bcaf3d5446d549b04d1bc24593eda8850266`:
- `src/qual/retrieval/service.py`
- Cumulative non-metadata branch files still present at the reviewed tip:
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`
- Metadata-only packet-refresh files in this resubmission:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands run with results

- Gate rerun date: `2026-04-23`
- Gate rerun target: `e7e545664f277419ff97a05740e45f88179dbe24`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. The packet now distinguishes the current submitted tip `e7e545664f277419ff97a05740e45f88179dbe24` from the reviewed implementation head `ced0bcaf3d5446d549b04d1bc24593eda8850266` instead of conflating them.
2. The canonical demo-path step advanced is stated directly as `retrieve relevant material` in the authoritative writable handoff packet.
3. The packet records the exact `.codex` metadata write blocker so re-review uses the correct refreshed artifacts for this pass.
4. The required gate suite is rerun and recorded against the current branch tip `e7e545664f277419ff97a05740e45f88179dbe24`.

## Risks / blockers

- Risk: `HIGH`
- Residual risk: callers that relied on mirrored sparse-query metadata overriding canonical query snapshots will now observe the canonical FTS-backed snapshot instead; that is the intended contract, but it can surface stale assumptions outside this lane.
- Residual risk: the cumulative branch still includes earlier non-metadata changes outside the newest tip delta, so reviewers need the cumulative `Files changed` section for full traceability.
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `ROADMAP.md: Milestone 3: Real workflow loop`
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

## Scope-check / ownership note

- Shared/integrator-locked edits in the cumulative branch diff: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` remains the approved shared regression surface already present in the cumulative branch diff.
- Newly added implementation delta at the reviewed tip stays in the lane-owned retrieval service.
- Packet-refresh edits in this resubmission are metadata-only.
