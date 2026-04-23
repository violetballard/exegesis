# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix packet finalization against the actual branch tip`
- Current submitted implementation head before this packet refresh commit: `ced0bcaf3d5446d549b04d1bc24593eda8850266`
- Reviewed implementation head: `ced0bcaf3d5446d549b04d1bc24593eda8850266`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..ced0bcaf3d5446d549b04d1bc24593eda8850266`
- Packet traceability note: the previous packet falsely anchored review at `adfa8cdadd43747ffbcb612e4151e262b13e52ca` even though later commits changed `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`, and retrieval code in `src/qual/retrieval/service.py`. This packet treats the full code-bearing cumulative range through `ced0bcaf3d5446d549b04d1bc24593eda8850266` as the reviewed implementation, and this commit changes only handoff metadata.
- Fixer note: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` could not be rewritten in this sandbox because writes under `.codex/` failed with `Operation not permitted`, so the writable review packet files in the repo root are the authoritative refreshed handoff for this pass.

## Scope goal

- Advance the canonical demo-path step `retrieve relevant material` by keeping excerpt lookup and excerpt-promotion metadata on the authoritative SQLite FTS path, by failing closed when sparse mirrors cannot reconstruct canonical query state, and by making packet generation keep the retrieval demo-path mapping explicit even when lane metadata is stale.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: preserve SQLite FTS as the authoritative retrieval path while truthfully regenerating the handoff packet against the actual code-bearing branch tip.
- Risk reason: the reviewed implementation range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py` plus reviewer-fix support edits in `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Normal size limits: `<=8 files`, `<=300 net LOC`
- Actual reviewed range size: `15 files`, `10482 insertions`, `745 deletions`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Regenerate the handoff packet so the reviewed implementation range reaches the actual branch tip `ced0bcaf3d5446d549b04d1bc24593eda8850266`.
2. Restate the reviewed scope so it covers both the retrieval-runtime work and the packet-planner safeguard that now preserves the retrieval demo-path mapping.
3. Keep the canonical demo-path mapping explicit as `retrieve relevant material` and tie it to the FTS-first behavior in `src/qual/retrieval/service.py`.
4. Re-run the required gate suite on the true reviewed implementation head and record the results against that exact SHA.

### Early Review Triggers

- before first edit to the shared-by-approval regression file `tests/unit/test_unified_retrieval.py`
- before changing public retrieval contract wording in the handoff packet
- before changing packet-generator behavior outside the reviewer-required demo-path field backfill

### Checkpoint Status

- `plan complete`: this packet now targets the actual branch tip `ced0bcaf3d5446d549b04d1bc24593eda8850266` instead of the stale `adfa8cdadd43747ffbcb612e4151e262b13e52ca` anchor.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on `ced0bcaf3d5446d549b04d1bc24593eda8850266`.
- `before risky/shared file edit`: the reviewed range still includes the approved shared regression file `tests/unit/test_unified_retrieval.py`; this packet refresh itself edits only handoff metadata files.
- `ready for handoff`: this packet now aligns the reviewed range, canonical demo-path step, file list, size statement, and gate evidence to the same real reviewed implementation head.

## Scope completed

- Canonical demo-path step advanced: `retrieve relevant material`.
- `src/qual/retrieval/service.py` now keeps `retrieve relevant material` FTS-first by clearing orphaned sparse query mirrors, fingerprinting provenance snapshots from canonical query state, rehydrating sparse retrieval query metadata deterministically, and deriving excerpt-promotion metadata from canonical query snapshots instead of stale provenance fragments.
- `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` close the reviewer-requested packet gap by making packet generation include the canonical demo-path step and impact for `feat-retrieval-fts` even when lane metadata is stale.
- The cumulative reviewed runtime changes remain narrow in behavior even though the branch range is large: SQLite FTS stays authoritative, PageIndex and embeddings remain compatibility-only shims, and no routing, provider, CLI, app, or integrator-locked entrypoints are added to the retrieval surface.

## Reviewed Scope Boundary

- The reviewed implementation range is `d7fd5d200358287fa42a18d39e2b277463b9b69f..ced0bcaf3d5446d549b04d1bc24593eda8850266`.
- Non-metadata reviewed files in that range:
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
- Metadata-only packet-refresh files in this fixer pass:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`
- This handoff advances `retrieve relevant material` by ensuring excerpt lookup and excerpt-promotion records stay bound to canonical FTS-backed query context, which keeps downstream basket and workflow use deterministic and auditable.

## Tasks completed

1. Built out the cumulative FTS-first retrieval implementation so the canonical retrieval facade, payload normalization, provenance snapshots, and sparse source or context rehydration stay deterministic for downstream engine flows while PageIndex and embeddings remain fallback-only.
2. Added and kept approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for normalized payload snapshots, facade exports, citation and provenance helpers, and the FTS-only excerpt lookup and fail-closed behavior.
3. Updated `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` so `feat-retrieval-fts` packets keep the canonical demo-path step `retrieve relevant material` even when lane metadata is stale.
4. Tightened the final branch-tip retrieval changes in `src/qual/retrieval/service.py` so canonical query snapshots drive provenance fingerprinting, sparse query rehydration, and excerpt-promotion metadata throughout the actual reviewed implementation head `ced0bcaf3d5446d549b04d1bc24593eda8850266`.

## Files changed

- Reviewed implementation files in `d7fd5d200358287fa42a18d39e2b277463b9b69f..ced0bcaf3d5446d549b04d1bc24593eda8850266`:
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
- Metadata-only packet-refresh files in the same branch window:
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

## Reviewer fix closure

1. The packet is regenerated so the reviewed implementation range reaches the actual code-bearing branch tip `ced0bcaf3d5446d549b04d1bc24593eda8850266`.
2. `Reviewed implementation range`, `Scope completed`, `Files changed`, and budget or size statements now cover the true cumulative reviewed implementation instead of the older narrowed historical slice.
3. The canonical demo-path step advanced is stated directly as `retrieve relevant material` and is tied both to the FTS-first retrieval behavior and to the packet-generator fallback that now preserves that mapping.
4. The gate evidence section is commit-scoped to the real reviewed implementation head `ced0bcaf3d5446d549b04d1bc24593eda8850266`, and all required gates passed on that SHA.

## Risks / blockers

- Risk: `HIGH`
- Residual risk: callers that relied on incomplete sparse excerpt query mirrors will now fail closed instead of receiving partially reconstructed metadata; that is the intended FTS-first contract but can expose stale callers outside this lane.
- Residual risk: the truthful cumulative handoff is much larger than the normal high-risk size budget, so reviewer attention needs to stay on scope accuracy and regression coverage.
- Residual risk: the branch includes reviewer-fix support edits in packet-planner tooling outside the lane-owned retrieval paths; those changes are narrow and regression-tested, but they are still part of the reviewed tip and remain called out explicitly.
- Blocker: the sandbox rejected writes under `.codex/`, so `.codex/lane_meta/feat-retrieval-fts.json` and `.codex/kickoff_packets/feat-retrieval-fts.md` remain stale copies of the older handoff narrative in this session.

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

- Shared/integrator-locked edits in the reviewed implementation range: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` remains the sole shared-by-approval implementation file in the retrieval-runtime slice.
- Additional non-lane reviewer-fix support edits in the reviewed tip: `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py`.
- All remaining non-metadata reviewed files stay in the lane-owned retrieval paths.
