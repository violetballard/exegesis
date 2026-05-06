## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Final fixer HEAD SHA: reported in the fixer response after this packet commit.
- Authoritative reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`
- Authoritative reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_FIXER_HEAD_REPORTED_IN_RESPONSE`
- Handoff type: high-risk retrieval handoff for the FTS-first retrieval lane.
- Risk reason: approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.

## Traceability Correction

This packet supersedes the stale narrow-range handoff. The reviewed range is the full merge-candidate range from `378cf9a74a3658058079a32f186fcd254c4a4034` through the final fixer HEAD, so it includes source-bearing commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, including `cff7569dddc06bd6c4b445ebfc4dd5d161ab3cf0`.

The previous metadata-only classification for `cff7569dddc06bd6c4b445ebfc4dd5d161ab3cf0` is withdrawn. That commit changes `src/qual/retrieval/service.py` and `src/qual/engine/retrieval/payload.py`, so it is included in the reviewed implementation range.

Other source-bearing post-`adfa8cd` commits are included as well; the post-`adfa8cd` implementation surface is `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`.

## Scope Completed

SQLite FTS remains the required MVP retrieval path. PageIndex and embeddings remain deferred or compatibility-only surfaces and are not reintroduced as required paths.

The branch hardens deterministic FTS retrieval behavior across cache keys, fresh-run cache snapshots, query snapshots, result payloads, excerpt lookup, citation/provenance bundles, evidence snapshots, sparse bundle rehydration, date-range propagation, and shortlist query fingerprints.

Canonical demo-path mapping: `vault/context material -> FTS retrieval -> retrieval evidence -> context basket promotion -> engine revise/apply`. This advances `retrieve relevant material` by producing deterministic, auditable FTS evidence, and supports `promote or gather context into the basket` by preserving rehydratable source, context, citation, provenance, and the named `retrieval_basket_promotion_bundle`.

## Current Fixer Pass Addendum

This pass makes the basket-promotion contract explicit in code. `RetrievalResult.retrieval_basket_promotion_bundle()` now emits deterministic FTS excerpt promotion items with doc/excerpt ids, text, spans, ranks, hashes, fingerprints, matched terms, source strategy, backend, and mode. The downstream payload, source bundle, and context bundle now preserve and rehydrate that named bundle through the engine retrieval payload helpers.

Current pass files changed:

- `M THREAD_PACKET.md`
- `M src/qual/engine/retrieval/payload.py`
- `M src/qual/retrieval/service.py`

Current pass task count: `1` meaningful task group, within the high-risk `4` task cap.
Current pass size: `2` source files changed, `145` source insertions before this packet edit; within the high-risk `<=8` files and `<=300` net LOC limits for this pass.
Shared/integrator-locked impact this pass: none; no test or integrator-locked files were edited.

## Tasks Completed

1. Made SQLite FTS the authoritative MVP retrieval path while keeping PageIndex and embeddings fallback-only/deferred.
2. Stabilized FTS cache and query normalization for query-shaped objects, dataclasses, mappings, iterables, date ranges, shortlist queries, fingerprints, doc types, scopes, boolean constraints, fresh runner output, cache invalidation, and cache audit metadata.
3. Normalized retrieval payload, provenance, citation, source-bundle, context-bundle, basket-promotion, and evidence snapshots so sparse downstream helpers can rehydrate FTS-first payloads without losing constraints, fingerprints, ranks, identities, policies, section hints, promotion items, or confidentiality profile metadata.
4. Added fail-closed retrieval boundary coverage for malformed or reversed date ranges, empty query/scope inputs, unresolved `doc:` and `collection:` scopes, FTS-only excerpt lookup, excerpt lookup fingerprints, and cache/query snapshot behavior.

## Files Changed

Authoritative reviewed range: `378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_FIXER_HEAD_REPORTED_IN_RESPONSE`.

Expected changed files for that range:

- `D .codex/kickoff_packets/feat-retrieval-fts.md`
- `D .codex/lane_meta/feat-retrieval-fts.json`
- `M THREAD_PACKET.md`
- `M src/qual/engine/retrieval/__init__.py`
- `M src/qual/engine/retrieval/fts_strategy.py`
- `M src/qual/engine/retrieval/payload.py`
- `M src/qual/retrieval/service.py`
- `M tests/unit/test_unified_retrieval.py`

Final merge-candidate diff for this corrected range: `8 files changed, 477 insertions(+), 188 deletions(-)`, net `+289` LOC.

The protected `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` mirror artifacts could not be edited in-place, so they are removed from the merge candidate to avoid preserving stale contradictory trace metadata. `THREAD_PACKET.md` is the coherent handoff packet for re-review.

## Budget/Risk

- Task budget: `4` high-risk task groups; completed as the four task groups above.
- File count: `8 files` in the full reviewed packet range; within the high-risk `<=8 files` limit.
- Size accounting: final reviewed range is net `+289` LOC, under the high-risk `<=300 net LOC` limit.
- Shared/integrator exception status: `tests/unit/test_unified_retrieval.py` is the sole approved shared regression surface; no integrator-locked files changed.
- Routing/provider impact: none.
- Remaining risks/blockers: none known after required gates are rerun on the final branch tip.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 Product Readiness generation provenance and Milestone 4 Retrieval Layer FTS-first retrieval orchestration/source attribution.
- Product Vision capability affected: `2. Retrieval-first context handling` and `3. Auditable generation`.
- Architecture alignment: retrieval stays in `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`; no provider/routing/core app entrypoints are touched.
- Proposed `README.md` patch text: none.

## Commands Run

Required gates rerun for this final merge candidate:

- `python -m unittest tests.unit.test_unified_retrieval` - passed 60 focused retrieval tests.
- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 129 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 129 unit tests.
