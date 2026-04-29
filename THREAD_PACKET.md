## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Implementation merge candidate reviewed by this packet: `3bef51f327ec4d37780b518790840cf3bf9563b7`
- Reviewed implementation range: `378cf9a..3bef51f327ec4d37780b518790840cf3bf9563b7`
- Final packet-refresh HEAD: reported in the fixer handoff after commit.
- Handoff classification: high-risk/shared because branch-tip review includes shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Canonical demo-path step advanced: `retrieve relevant material` and `promote or gather context into the basket`.

## Required Fixes Addressed

1. This packet is regenerated against the actual merge candidate tip `3bef51f327ec4d37780b518790840cf3bf9563b7`; earlier narrowed-slice packets anchored to `adfa8cdadd43747ffbcb612e4151e262b13e52ca` are superseded.
2. Post-`adfa8cd` implementation changes are included in reviewed scope: retrieval context refs in `src/qual/retrieval/service.py`, context-ref preservation in `src/qual/engine/retrieval/payload.py`, and shared regression coverage in `tests/unit/test_unified_retrieval.py`.
3. High-risk task/file/LOC budget is recalculated against `378cf9a..3bef51f327ec4d37780b518790840cf3bf9563b7`.
4. Required gates are rerun for the branch-tip worktree and reported below.
5. The canonical demo-path step is explicit: FTS retrieval now returns promotion-ready source/context references so retrieved material can be gathered into the basket with auditable provenance.

## Scope Completed

The branch delivers the cumulative FTS-first retrieval slice for the MVP. SQLite FTS is the canonical retrieval and excerpt lookup path; PageIndex and embeddings remain compatibility/fallback surfaces rather than required paths. Retrieval query construction, payload normalization, provenance bundles, citation bundles, source bundles, excerpt bundles, cache snapshots, and downstream context bundles are deterministic for engine orchestration.

The actual branch tip also makes basket promotion more real by carrying `retrieval_context_refs` from FTS hits through source bundles, downstream payloads, sparse bundle reconstruction, and nested payload normalization. Those refs include excerpt IDs, source strategy, FTS provenance, query/result fingerprints, span data, matched-term metadata, and stable context-ref fingerprints.

## Tasks Completed

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, FTS-only excerpt lookup, guarded scope handling, compatibility exports, and fallback-only PageIndex/embedding shims.
2. Deterministic retrieval payloads: normalized queries, constraints, date ranges, cache keys, ranked IDs, hit snapshots, policy metadata, citation fields, provenance bundles, and source/context/excerpt bundles.
3. Basket promotion readiness: stable `retrieval_context_refs`, context-ref fingerprints, source bundle aliases, sparse bundle rehydration, nested context-ref extraction, and downstream helper backfills.
4. Regression and packet coverage: shared canonical retrieval tests plus branch-tip handoff metadata corrected for the actual merge candidate.

## Files Changed

Reviewed implementation range `378cf9a..3bef51f327ec4d37780b518790840cf3bf9563b7`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Implementation files in that range:

- `src/qual/retrieval/service.py`: adds promotion-ready `retrieval_context_refs` to retrieval results, source bundles, downstream payloads, and context bundles; removes PageIndex fallback from `fetch_excerpt`.
- `src/qual/engine/retrieval/payload.py`: preserves and rehydrates `retrieval_context_refs` from top-level and nested source/doc/excerpt/context snapshots.
- `tests/unit/test_unified_retrieval.py`: verifies FTS-only excerpt lookup, rejection of PageIndex-only excerpt IDs, context-ref fields/fingerprints, defensive copies, and sparse payload rehydration.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`.
- File budget: `6/8`.
- Size budget for `378cf9a..3bef51f327ec4d37780b518790840cf3bf9563b7`: `6 files changed, 422 insertions(+), 131 deletions(-)`, net `291` LOC, within the high-risk `<=300` net LOC cap.
- Integrator-locked files: none.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py`, used only for canonical retrieval regression coverage.
- Routing/provider impact: none. This branch does not change model routing, provider configuration, provider compatibility behavior, CLI entrypoints, or app entrypoints.

## FTS-First Alignment

`src/qual/retrieval/service.py` keeps SQLite FTS authoritative for retrieval and excerpt lookup. PageIndex-only excerpt IDs now fail closed with `KeyError`, and the regression tests cover that behavior. Context refs are derived from FTS hits and retain FTS provenance so downstream basket/workflow consumers can audit the retrieved source material.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 4 Retrieval Layer: FTS-first ingestion/retrieval, retrieval orchestration before drafting/diff generation, source attribution for retrieved chunks, and PageIndex/embeddings deferred until after the demo push.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling: generation consumes retrieved chunks, SQLite FTS remains the MVP retrieval path, and PageIndex/embeddings are deferred.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation: retrieved sources carry deterministic provenance, citations, fingerprints, and promotion references.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh fixer pass on `2026-04-29`:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS (`124` tests).
- `./typecheck-test.sh` PASS.
- `make ci` PASS (`124` tests).

## Risks / Blockers

- No blockers remain in the packet metadata.
- This fixer creates a metadata-only commit after `3bef51f327ec4d37780b518790840cf3bf9563b7`; the final HEAD SHA is reported in the fixer handoff. Review should treat `378cf9a..3bef51f327ec4d37780b518790840cf3bf9563b7` as the reviewed implementation range and the final fixer commit as packet/gate reconciliation metadata.
