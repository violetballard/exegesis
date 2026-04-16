# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed implementation head: `629f7c27f8aea0f0299f516126f41cd40065d70b`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `metadata-only reviewer-fix packet sync`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..629f7c27f8aea0f0299f516126f41cd40065d70b`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in the reviewed implementation range.
- `fetch_excerpt` fails closed on the canonical FTS-only path and no longer falls back to PageIndex-only excerpt payloads.
- Retrieval provenance, downstream payloads, and basket-promotion snapshots now preserve `excerpt_provenance_fingerprint` through the canonical retrieval surface, including citation-based backfill paths.
- PageIndex and embeddings remain non-required compatibility paths and are not restored as required runtime retrieval backends.

## Canonical Demo-Path Step Advanced
- Canonical demo-path step advanced: `promote or gather context into the basket`
- This reviewed implementation range makes `promote or gather context into the basket` more real by preserving stable excerpt provenance fingerprints from ranked FTS hits through retrieval provenance and basket-promotion payloads, while keeping excerpt lookup fail-closed on the canonical FTS path.

## AGENTS.md Handoff Packet
- Risk reason: shared/high-risk work because the reviewed implementation includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`
- Tasks completed:
  1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
  2. Preserved `excerpt_provenance_fingerprint` in retrieval provenance and basket-promotion snapshots used by downstream engine flows.
  3. Fixed citation-based provenance backfill so sparse source bundles recover the primary excerpt provenance fingerprint deterministically.
  4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for PageIndex fail-closed behavior, provenance backfill, and basket-promotion propagation.

## Files changed
### Reviewed implementation files
- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`
- `tests/unit/test_unified_retrieval.py`

### Metadata-only handoff files
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
- `feat-retrieval-fts - authoritative FTS-first retrieval feeding the engine loop`

### Vision capability affected
- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note
- None

## Scope-check / ownership note
- Shared-by-approval edits: `YES` (Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.)
- Integrator-locked edits: `NO`

## Regression coverage note
- `tests/unit/test_unified_retrieval.py::test_retrieval_provenance_helper_backfills_primary_fingerprints_from_citations`
- `tests/unit/test_unified_retrieval.py::test_retrieval_downstream_payload_helper_backfills_basket_promotion_from_top_level_hits`
- `tests/unit/test_unified_retrieval.py::test_retrieval_downstream_payload_helper_backfills_basket_promotion_from_nested_bundles`
- `tests/unit/test_unified_retrieval.py::test_fetch_excerpt_requires_an_fts_lookup_hit`

## Traceability note
- The reviewed implementation scope ends at `629f7c27f8aea0f0299f516126f41cd40065d70b`.
- The packet refresh commit created after this edit is metadata-only and does not change the reviewed retrieval implementation range.
- Re-review should anchor retrieval implementation scope to `378cf9a74a3658058079a32f186fcd254c4a4034..629f7c27f8aea0f0299f516126f41cd40065d70b`.
