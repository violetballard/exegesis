## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: reviewer-fix re-review packet for the actual branch tip.
- Review baseline from reviewer packet: `378cf9a74a3658058079a32f186fcd254c4a4034`
- Reviewed implementation range before this metadata-only fixer commit: `378cf9a74a3658058079a32f186fcd254c4a4034..c11be4126a063df52096fc7a46c88c848fda69d3`
- Runtime/test implementation head in that range: `e11cdde8610587c865afec904674f9366cbfa0cf`
- Canonical demo-path step advanced: retrieve relevant material
- Final reviewed head: reported in the fixer response after this metadata-only packet correction is committed.

## Scope Completed

This re-review packet keeps the post-`378cf9a` scope tight to `feat-retrieval-fts`: FTS-only excerpt lookup, structured source/context/citation bundles for workflow-ready retrieval results, deterministic basket-promotion provenance, and payload rehydration from sparse source bundles. PageIndex-only excerpt IDs fail closed, and PageIndex/embeddings remain deferred compatibility paths rather than required retrieval paths.

## Tasks Completed

1. Added FTS-only excerpt lookup/backfill behavior and fail-closed handling for PageIndex-only excerpt IDs.
2. Added deterministic source/context/citation bundle snapshots for basket promotion, including stable source IDs, fingerprints, citation status, query scope, intent, and date range.
3. Added engine payload rehydration from compact source/context bundles so sparse downstream inputs recover deterministic retrieval payloads.
4. Added shared regression coverage for excerpt backfill, facade exports, payload normalization, provenance helpers, and basket-promotion snapshots.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Budget

- Risk: high, because approved shared regression coverage touches `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4`.
- File budget before this metadata-only fixer commit: `6/8`.
- Size budget before this metadata-only fixer commit: `6 files changed, 474 insertions(+), 120 deletions(-)` for `378cf9a74a3658058079a32f186fcd254c4a4034..c11be4126a063df52096fc7a46c88c848fda69d3`.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is included as approved shared regression coverage for the retrieval lane; no integrator-locked files are edited in this re-review slice.

## Roadmap / Vision

- Roadmap items: `ROADMAP.md` Milestone 3 Product Readiness and Milestone 4 Retrieval Layer.
- Vision capabilities: `PRODUCT_VISION.md` capability 2 retrieval-first context handling and capability 6 auditable state/workflow.
- Routing/provider impact: none.

## Canonical Demo Path

This branch advances the canonical demo-path step `retrieve relevant material`. FTS-only `fetch_excerpt` makes retrieved material auditable and deterministic before basket/context promotion.

## Traceability Correction

Earlier packet text incorrectly treated commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as metadata-only. That claim is withdrawn. This handoff chooses the actual branch-tip lineage for the reviewer packet baseline and reviews `378cf9a74a3658058079a32f186fcd254c4a4034..c11be4126a063df52096fc7a46c88c848fda69d3` before this metadata-only fixer commit. That range includes runtime/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` in `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`.

This fixer pass changes packet metadata only. It does not narrow, split, reset, or modify the reviewed runtime/test implementation. The final HEAD SHA and gate outcomes against that final branch tip are reported in the fixer response after commit.

## Commands Run

Required gates rerun for this fixer pass against the exact pre-commit branch tip `c11be4126a063df52096fc7a46c88c848fda69d3`:

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS, including smoke plus 126 unit tests
- `./typecheck-test.sh`: PASS
- `make ci`: PASS, including scope-check, format, lint, compileall, and smoke plus 126 unit tests

## Risks / Blockers

- Residual risk: broader retrieval orchestration beyond deterministic source/context bundles remains separate high-risk work.
- Scope risk: none identified in this re-review slice; changes remain FTS-first and deterministic.
- Shared-file note: `tests/unit/test_unified_retrieval.py` is the only shared-by-approval file in this slice.
- Packet mirror blocker: this sandbox returned `Operation not permitted` when attempting to update `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json`; `THREAD_PACKET.md` is the updated handoff packet for this fixer commit.
