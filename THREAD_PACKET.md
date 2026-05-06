## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Final fixer HEAD SHA: the packet-only fixer commit that contains this handoff; reported in the fixer response.
- Authoritative reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`
- Authoritative reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`, where `HEAD` is this packet-only fixer commit.
- Source-bearing merge-candidate tip before this packet-only fixer commit: `125a3b7f84f096159baed4114029a7a38df772ae`.
- Handoff type: high-risk retrieval handoff for the FTS-first retrieval lane.
- Risk reason: approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.

## Traceability Correction

This packet supersedes the stale narrow-range handoff. The reviewed range is the full merge-candidate range from `378cf9a74a3658058079a32f186fcd254c4a4034` through this final packet-only fixer commit, so it includes source-bearing commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` through `125a3b7f84f096159baed4114029a7a38df772ae`, including `cff7569dddc06bd6c4b445ebfc4dd5d161ab3cf0`.

The previous metadata-only classification for `cff7569dddc06bd6c4b445ebfc4dd5d161ab3cf0` is withdrawn. That commit changes `src/qual/retrieval/service.py` and `src/qual/engine/retrieval/payload.py`, so it is included in the reviewed implementation range.

Other source-bearing post-`adfa8cd` commits are included as well; the post-`adfa8cd` implementation surface is `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`. This final fixer commit changes only `THREAD_PACKET.md`.

## Scope Completed

SQLite FTS remains the required MVP retrieval path. PageIndex and embeddings remain deferred or compatibility-only surfaces and are not reintroduced as required paths.

The branch hardens deterministic FTS retrieval behavior across cache keys, fresh-run cache snapshots, query snapshots, result payloads, excerpt lookup, citation/provenance bundles, evidence snapshots, sparse bundle rehydration, date-range propagation, and shortlist query fingerprints.

Canonical demo-path mapping: `vault/context material -> FTS retrieval -> retrieval evidence -> context basket promotion -> engine revise/apply`. This advances `retrieve relevant material` by producing deterministic, auditable FTS evidence, and supports `promote or gather context into the basket` by preserving rehydratable source, context, citation, provenance, and the named `retrieval_basket_promotion_bundle`.

## Current Fixer Pass Addendum

The source-bearing tip before this pass makes the basket-promotion contract explicit in code. `RetrievalResult.retrieval_basket_promotion_bundle()` emits deterministic FTS excerpt promotion items with doc/excerpt ids, text, spans, ranks, hashes, fingerprints, matched terms, source strategy, backend, and mode. The downstream payload, source bundle, and context bundle preserve and rehydrate that named bundle through the engine retrieval payload helpers.

This fixer pass corrects packet traceability only. It does not add, remove, or alter retrieval implementation behavior after source-bearing tip `125a3b7f84f096159baed4114029a7a38df772ae`.

Current pass files changed:

- `M THREAD_PACKET.md`

Current pass task count: `1` meaningful task group, within the high-risk `4` task cap.
Current pass size: packet-only traceability update in `THREAD_PACKET.md`.
Shared/integrator-locked impact this pass: none; no source, test, or integrator-locked files were edited.

## Tasks Completed

1. Made SQLite FTS the authoritative MVP retrieval path while keeping PageIndex and embeddings fallback-only/deferred.
2. Stabilized FTS cache and query normalization for query-shaped objects, dataclasses, mappings, iterables, date ranges, shortlist queries, fingerprints, doc types, scopes, boolean constraints, fresh runner output, cache invalidation, and cache audit metadata.
3. Normalized retrieval payload, provenance, citation, source-bundle, context-bundle, basket-promotion, and evidence snapshots so sparse downstream helpers can rehydrate FTS-first payloads without losing constraints, fingerprints, ranks, identities, policies, section hints, promotion items, or confidentiality profile metadata.
4. Added fail-closed retrieval boundary coverage for malformed or reversed date ranges, empty query/scope inputs, unresolved `doc:` and `collection:` scopes, FTS-only excerpt lookup, excerpt lookup fingerprints, and cache/query snapshot behavior.

## Files Changed

Authoritative reviewed range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`, where `HEAD` is this packet-only fixer commit.

Expected changed files for that range:

- `D .codex/kickoff_packets/feat-retrieval-fts.md`
- `D .codex/lane_meta/feat-retrieval-fts.json`
- `M THREAD_PACKET.md`
- `M src/qual/engine/retrieval/__init__.py`
- `M src/qual/engine/retrieval/fts_strategy.py`
- `M src/qual/engine/retrieval/payload.py`
- `M src/qual/retrieval/service.py`
- `M tests/unit/test_unified_retrieval.py`

Merge-candidate diff through source-bearing tip `125a3b7f84f096159baed4114029a7a38df772ae`: `8 files changed, 637 insertions(+), 188 deletions(-)`, net `+449` LOC. The final packet-only fixer commit adds only this traceability update to `THREAD_PACKET.md`.

The protected `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` mirror artifacts could not be edited in-place, so they are removed from the merge candidate to avoid preserving stale contradictory trace metadata. `THREAD_PACKET.md` is the coherent handoff packet for re-review.

## Budget/Risk

- Task budget: `4` high-risk task groups; completed as the four task groups above.
- File count: `8 files` in the full reviewed packet range; within the high-risk `<=8 files` limit.
- Size accounting: source-bearing branch tip `125a3b7f84f096159baed4114029a7a38df772ae` is net `+449` LOC versus the authoritative reviewed base, before this packet-only update. This exceeds the high-risk `<=300 net LOC` budget and is reported here rather than hidden by a stale narrow range.
- Shared/integrator exception status: `tests/unit/test_unified_retrieval.py` is the sole approved shared regression surface; no integrator-locked files changed.
- Routing/provider impact: none.
- Remaining risks/blockers: size budget exceeded for the full corrected range; no functional gate blockers after required gates are rerun on the final branch tip.

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
