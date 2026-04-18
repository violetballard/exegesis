# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix packet regeneration`
- Trace anchor before this fixer pass: `838b4c4251e19e2f685267215198cff8a38d3f1f`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..838b4c4251e19e2f685267215198cff8a38d3f1f`
- Exact reviewed implementation head: `838b4c4251e19e2f685267215198cff8a38d3f1f`
- Packet traceability note: this fixer pass updates packet metadata only. The final fixer commit advances the branch tip for handoff traceability, but it does not change the reviewed implementation head or reviewed implementation range.

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
2. Normalize FTS cache query variants in `src/qual/engine/retrieval/fts_strategy.py` so equivalent retrieval requests share deterministic cache keys.
3. Backfill missing doc-hit and excerpt-hit provenance during payload normalization in `src/qual/engine/retrieval/payload.py`.
4. Keep approved shared regression coverage in `tests/unit/test_unified_retrieval.py` aligned with the FTS-first retrieval contract and the new provenance backfill behavior.

### Checkpoint Status

- `plan complete`: the packet is regenerated against the actual implementation head instead of an older narrowed slice hidden behind a falsely labeled metadata-only head.
- `first green tests`: recorded after rerunning all required gates on this fixer pass branch tip.
- `before risky/shared file edit`: the only shared implementation file in scope remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the handoff now describes the real retrieval implementation under review at `838b4c4251e19e2f685267215198cff8a38d3f1f`.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path in the reviewed implementation.
- Public excerpt lookup resolves only through the canonical FTS-backed path in `src/qual/retrieval/service.py`, so PageIndex-only excerpt IDs fail closed instead of silently backfilling from compatibility storage.
- `src/qual/engine/retrieval/fts_strategy.py` normalizes equivalent query variants for deterministic cache behavior on the FTS-first path.
- `src/qual/engine/retrieval/payload.py` backfills missing doc-hit and excerpt-hit provenance from canonical top-level fields so sparse source/context bundle rehydration stays deterministic and auditable.
- PageIndex and embeddings remain compatibility-only paths; the lane does not reintroduce them as required runtime retrieval paths.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` exercises both the FTS-only excerpt contract and the missing-provenance backfill behavior.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff advances `retrieve relevant material` by tightening the canonical retrieval contract around deterministic FTS behavior, excerpt lookup, cache-key normalization, and sparse payload rehydration that downstream basket promotion and workflow consumers can audit.

## Tasks completed

1. Kept `fetch_excerpt` on the canonical FTS-only path so PageIndex-only excerpt IDs fail closed.
2. Normalized FTS cache query variants in `src/qual/engine/retrieval/fts_strategy.py` so equivalent retrieval requests share deterministic cache keys.
3. Backfilled missing doc-hit and excerpt-hit provenance during payload normalization in `src/qual/engine/retrieval/payload.py`.
4. Extended approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the FTS-only excerpt contract and missing-provenance backfill behavior.

## Files changed

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
- Handoff metadata files:
  - `THREAD_PACKET.md`
- Mirrored packet artifacts blocked by workspace permissions:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. Regenerated the handoff against the actual implementation head instead of keeping review anchored to a falsely labeled metadata-only head.
2. Updated scope completed and files changed so they describe the real retrieval code under review, including `src/qual/engine/retrieval/fts_strategy.py` and the payload normalization work.
3. Kept the risk story aligned to the shared/high-risk lane rules because the approved shared regression file is part of the reviewed implementation.
4. Stated explicitly that the canonical demo-path step advanced is `retrieve relevant material`.

## Risks / blockers

- Risk: `HIGH`
- Blocker: writes under `.codex/` are denied in this worktree, so the mirrored kickoff and lane-meta packet artifacts could not be updated here.

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file in the reviewed implementation.
