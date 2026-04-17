# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-required handoff regeneration`
- Reviewed implementation head: `c0d9ef3520f490da556d6fa88b979dadc548ea4e`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..c0d9ef3520f490da556d6fa88b979dadc548ea4e`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt, provenance, and basket-promotion output on the canonical retrieval surface.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt, provenance, and basket-promotion output on the canonical retrieval surface.
- Risk reason: the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Checkpoint Status

- `plan complete`: regenerated the handoff around the actual reviewed implementation head and file set on the branch.
- `first green tests`: all required gates were re-run on the regenerated packet state.
- `before risky/shared file edit`: no new shared implementation edit was introduced; the only shared implementation file remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the packet now matches the true branch scope, high-risk classification, and Milestone 3 mapping.

## Budget classification

- Shared/high-risk handoff under the `4`-task cap because the reviewed implementation range includes the approved shared regression file `tests/unit/test_unified_retrieval.py`.
- This regenerated packet reports the true cumulative branch scope: `9` implementation files changed with `6611` insertions and `811` deletions in the reviewed implementation range.

## Scope completed

- Kept SQLite FTS authoritative for the MVP retrieval path and preserved the canonical retrieval helper exports across the retrieval facades.
- Hardened deterministic retrieval payloads, provenance snapshots, query normalization, audit metadata, and excerpt lookup fingerprints for engine-side downstream consumers.
- Rehydrated sparse source/context bundles and backfilled basket-promotion metadata so the canonical engine loop can promote auditable retrieval state into basket/context flows.
- Enforced the FTS-only excerpt lookup path so PageIndex-only excerpt ids now fail closed under the canonical retrieval contract.

## Canonical demo-path steps advanced

- `retrieve relevant material`
- `promote or gather context into the basket`

The additional payload work after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` is in scope because it keeps retrieval outputs structured, deterministic, and auditable enough for basket promotion in Milestone 3's engine loop. The reviewed range still does not claim workflow-action, UI, or alternate-retrieval-mode expansion.

## Required reviewer fixes addressed

1. Regenerated the handoff so it points at the actual reviewed implementation head `c0d9ef3520f490da556d6fa88b979dadc548ea4e`.
2. Removed the false `metadata-only` claim for `a23e45b02a8f21092f99852325e88c983f1ba862` and included all post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` runtime retrieval files in the reviewed scope.
3. Mapped the added payload and basket-promotion work to the Milestone 3 canonical demo-path steps `retrieve relevant material` and `promote or gather context into the basket`.
4. Reconciled the kickoff packet, lane metadata, and handoff packet so risk class, reviewed range, tasks, and files changed are consistent.
5. Re-ran the required gate suite against the regenerated packet state and recorded the results below.

## Tasks completed

1. Kept the canonical retrieval surface FTS-first by exporting the retrieval helpers consistently and enforcing FTS-only excerpt lookup behavior.
2. Hardened deterministic retrieval query, payload, provenance, ranking, and audit snapshots so downstream engine flows can trust stable retrieval state.
3. Backfilled sparse source/context and basket-promotion snapshots so retrieved material can be promoted into the basket with auditable fingerprints, ranked ids, and query constraints intact.
4. Added and maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the canonical retrieval contract.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet refresh files:
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

## Risks / blockers

- Risk: `HIGH`
- Blockers: none

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
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file in the reviewed implementation range.
