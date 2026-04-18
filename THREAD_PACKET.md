# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix packet regeneration`
- Current packet branch tip before this fixer pass: `49adae86`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..245ddb91b906caf392797830468606ec1101c3d2`
- Exact reviewed implementation head: `245ddb91b906caf392797830468606ec1101c3d2`
- Packet traceability note: the reviewed retrieval implementation ends at `245ddb91b906caf392797830468606ec1101c3d2`. The later commits `36e68d83`, `bb3cd335`, and `49adae86` update handoff metadata only and do not change retrieval implementation files.

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: keep the FTS-first retrieval lane scoped to deterministic excerpt and provenance output on the canonical engine retrieval surface.
- Risk reason: the reviewed implementation includes the approved shared regression file `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep public excerpt lookup on the canonical FTS-only path so PageIndex-only excerpt IDs fail closed.
2. Preserve deterministic sparse excerpt query-context backfill on the FTS-first retrieval path.
3. Keep the handoff packet aligned to the real reviewed implementation range and current branch tip.
4. Keep approved shared regression coverage in `tests/unit/test_unified_retrieval.py` aligned with the canonical FTS retrieval contract.

### Checkpoint Status

- `plan complete`: the packet is regenerated against the actual reviewed implementation head instead of the stale `adfa8cda` packet story.
- `first green tests`: recorded after rerunning all required gates on the reviewed branch state.
- `before risky/shared file edit`: the only shared implementation file in scope remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the handoff now describes branch tip `49adae86` while anchoring reviewed retrieval scope to `245ddb91b906caf392797830468606ec1101c3d2`.

## Scope completed

- `fetch_excerpt` resolves only through the canonical FTS lookup path in `src/qual/retrieval/service.py`.
- Sparse excerpt query context fails closed on the canonical FTS-only path in `src/qual/retrieval/service.py`.
- Canonical retrieval query construction, provenance, and payload normalization stay deterministic across `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` verifies PageIndex-only excerpt IDs raise `KeyError`.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff advances `retrieve relevant material` by forcing excerpt lookup through the authoritative SQLite FTS path. The true branch contents still keep SQLite FTS as the required MVP retrieval path and do not reintroduce PageIndex or embeddings as required runtime paths.

## Tasks completed

1. Kept `fetch_excerpt` on the canonical FTS-only path so PageIndex-only excerpt IDs fail closed.
2. Preserved deterministic sparse excerpt query-context backfill on the FTS-first retrieval path.
3. Preserved deterministic retrieval payload, provenance, and facade export behavior across the cumulative reviewed implementation range.
4. Extended approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the canonical FTS-only excerpt contract.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/service.py`
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet metadata files:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. Regenerated the handoff for the actual branch tip lineage instead of keeping review anchored to the stale `adfa8cda` packet range.
2. Added the explicit canonical demo-path mapping required by `AGENTS.md`: `retrieve relevant material`.
3. Restated roadmap and product-vision impact for the true cumulative retrieval contents on this branch.
4. Confirmed the extra retrieval commits in the reviewed range still keep SQLite FTS as the required MVP path without reintroducing PageIndex or embeddings as required runtime paths.

## Risks / blockers

- Risk: `HIGH`
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `ROADMAP.md: Milestone 4: Retrieval Layer`
- `ROADMAP.md: MVP Focus Through 2026-05-04 - feat-retrieval-fts`

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file in the reviewed implementation.
