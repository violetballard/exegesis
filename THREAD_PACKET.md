# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix packet regeneration against actual branch tip`
- Current submitted implementation head before this packet refresh commit: `ced0bcaf3d5446d549b04d1bc24593eda8850266`
- Reviewed implementation head: `ced0bcaf3d5446d549b04d1bc24593eda8850266`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..ced0bcaf3d5446d549b04d1bc24593eda8850266`
- Packet traceability note: earlier packet refreshes froze the reviewed scope at `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and then `d9542206f6fd14db37d1ddf5efd76f941d32314b` even though the real branch tip kept moving with non-metadata retrieval changes. This packet treats the full cumulative implementation range through `ced0bcaf3d5446d549b04d1bc24593eda8850266` as the reviewed implementation and keeps this commit metadata-only.

## Scope goal

- Advance the canonical demo-path step `retrieve relevant material` by keeping excerpt lookup and excerpt-promotion metadata on the authoritative SQLite FTS path, and by making the handoff packet truthful about the real reviewed branch tip.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: preserve SQLite FTS as the authoritative retrieval path while closing the reviewer-requested handoff fidelity gaps on the actual branch tip.
- Risk reason: the reviewed implementation range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py` plus reviewer-fix packet-planner support edits in `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Single-thread size limits: `<=8 files`, `<=300 net LOC`
- Actual cumulative reviewed range being handed off: `11 implementation files`, `15 total changed files including metadata`, `+10482/-745` net lines. This exceeds the single-thread size limits, so the packet states that fact explicitly instead of narrowing the reviewed slice.
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Regenerate the handoff packet against the real current implementation head `ced0bcaf3d5446d549b04d1bc24593eda8850266`.
2. Restate `Scope completed`, `Files changed`, and budget/size notes so they match the full cumulative implementation range now under review.
3. Add the canonical demo-path mapping `retrieve relevant material` explicitly in both machine-readable metadata and the human handoff.
4. Re-run the required gate suite against the actual reviewed implementation head and record that evidence against the same SHA.

### Checkpoint Status

- `plan complete`: the packet now targets the real branch-tip implementation head `ced0bcaf3d5446d549b04d1bc24593eda8850266` instead of the stale `adfa8cda...` or `d9542206...` slices.
- `first green tests`: `./quality-test.sh` passed on `ced0bcaf3d5446d549b04d1bc24593eda8850266`.
- `before risky/shared file edit`: the reviewed implementation range still includes the approved shared regression file `tests/unit/test_unified_retrieval.py`; this packet refresh itself edits only handoff metadata files.
- `ready for handoff`: the packet, lane metadata, and gate summary now all refer to the same reviewed implementation head and the same canonical demo-path step.

## Scope completed

- Canonical demo-path step advanced: `retrieve relevant material`.
- `src/qual/retrieval/service.py` now prefers canonical excerpt query snapshots when rehydrating sparse lookup state, fails closed when authoritative FTS query context cannot be reconstructed, and keeps excerpt-promotion metadata bound to canonical query fingerprints rather than stale sparse mirrors.
- `src/qual/retrieval/**` and `src/qual/engine/retrieval/**` keep SQLite FTS authoritative across both retrieval facades while preserving PageIndex and embeddings as compatibility-only fallback shims.
- `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` now preserve the canonical demo-path mapping for `feat-retrieval-fts` when lane metadata is stale, so later packet refreshes do not silently drop `retrieve relevant material`.
- The reviewed implementation range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`, which exercises the FTS-first retrieval contract and the packet-planner fallback behavior now present on the real branch tip.

## Files changed

- Reviewed implementation files in `d7fd5d200358287fa42a18d39e2b277463b9b69f..ced0bcaf3d5446d549b04d1bc24593eda8850266`:
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
- Metadata-only packet refresh files in this fixer pass:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands run with results

- Gate rerun date: `2026-04-23`
- Gate rerun target: `ced0bcaf3d5446d549b04d1bc24593eda8850266`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS` (`200` tests, `OK`)
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / blockers

- Risk: `HIGH`
- Residual risk: callers that relied on incomplete sparse excerpt query mirrors will now fail closed instead of receiving partially reconstructed metadata. That is the intended FTS-first contract, but it can expose stale callers outside this lane.
- Residual risk: the reviewed implementation range includes packet-planner support edits outside the lane-owned retrieval paths. They are narrow, covered by `tests/unit/test_packet_planner.py`, and called out explicitly here so re-review is not scoped too narrowly again.
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `ROADMAP.md: Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This handoff advances `retrieve relevant material` by ensuring excerpt lookup resolves through the authoritative SQLite FTS path, preserving deterministic query/provenance snapshots for downstream workflow use.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits in the reviewed implementation range: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` remains the sole shared-by-approval implementation file in the reviewed retrieval slice.
- Additional non-lane reviewer-fix support edits in the reviewed implementation range: `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py`
- All remaining non-metadata reviewed files stay in the lane-owned retrieval paths.
