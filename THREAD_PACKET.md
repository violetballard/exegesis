## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval handoff for the FTS-first retrieval lane.
- Risk reason: approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.
- Authoritative reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`.
- Authoritative reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`, where `HEAD` is the final branch tip reported with this fixer response.
- Actual source-bearing branch tip covered by this packet: `b3b0e81e6a6754dfa3eaa3d21a01ee82817ad846`.
- Packet-only trace tip before this fixer refresh: `b1a9ea85016746bcd2a54a247e860d7c3fe4e1e9`.
- Source-bearing update note: `b3b0e81e6a6754dfa3eaa3d21a01ee82817ad846` is source-bearing, not metadata-only. It changes `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `THREAD_PACKET.md`; those retrieval source changes are included in the corrected reviewed implementation range.

## Traceability Correction

This packet supersedes stale narrow-range handoffs that described `adfa8cdadd43747ffbcb612e4151e262b13e52ca` or `b43178f56a0c78df411697654c17f2c029d44546` as the final reviewed implementation tip. The corrected reviewer range is the full cumulative branch range:

`378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`

That range includes every source-bearing retrieval commit through `b3b0e81e6a6754dfa3eaa3d21a01ee82817ad846`, including the reviewer-cited source changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`. The packet-only fixer commits on top of `b3b0e81e6a6754dfa3eaa3d21a01ee82817ad846`, including `d1440f763ae89eb3853059c8fb4a0deda6ee75ed`, `b1a9ea85016746bcd2a54a247e860d7c3fe4e1e9`, and the final fixer commit reported with this handoff response, do not move retrieval source.

The source/test implementation surface in the corrected range is:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

The full changed-file surface in the corrected range is:

- `D .codex/kickoff_packets/feat-retrieval-fts.md`
- `D .codex/lane_meta/feat-retrieval-fts.json`
- `M src/qual/engine/retrieval/__init__.py`
- `M src/qual/engine/retrieval/fts_strategy.py`
- `M src/qual/engine/retrieval/payload.py`
- `M src/qual/retrieval/__init__.py`
- `M src/qual/retrieval/service.py`
- `M tests/unit/test_unified_retrieval.py`
- `M THREAD_PACKET.md`

Current source-bearing diff size for `378cf9a74a3658058079a32f186fcd254c4a4034..b3b0e81e6a6754dfa3eaa3d21a01ee82817ad846` is `9 files changed, 888 insertions(+), 201 deletions(-)`. Excluding `THREAD_PACKET.md`, the source/artifact/test portion is `8 files changed, 806 insertions(+), 129 deletions(-)`. The final reviewed range is still `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`; later changes after `b3b0e81e6a6754dfa3eaa3d21a01ee82817ad846` are packet-only traceability refreshes. At the pre-commit packet-refresh tip `b1a9ea85016746bcd2a54a247e860d7c3fe4e1e9`, the full corrected range is `9 files changed, 891 insertions(+), 201 deletions(-)`.

The protected `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` mirror artifacts are deleted in this branch so stale contradictory packet metadata is not preserved. `THREAD_PACKET.md` is the coherent handoff packet for re-review.

## Scope Completed

SQLite FTS remains the required MVP retrieval path. PageIndex and embeddings remain deferred or compatibility-only surfaces and are not reintroduced as required paths.

The branch hardens deterministic FTS retrieval behavior across cache keys, fresh-run cache snapshots, query snapshots, result payloads, excerpt lookup, citation/provenance bundles, evidence snapshots, sparse bundle rehydration, date-range propagation, shortlist query fingerprints, matched-term provenance, result fingerprints, doc identity, doc rank, doc type, strategy aliases, query constraints, and context basket promotion evidence. The final source-bearing update adds deterministic promotion-item and promotion-bundle fingerprints so basket promotion can audit exact FTS evidence items without rehydrating the whole retrieval result.

Canonical demo path: `vault/context material -> FTS retrieval -> retrieval evidence -> context basket promotion -> engine revise/apply`.

Canonical demo-path step made real by this work: it advances both retrieving relevant material with FTS and promoting retrieved evidence into the context basket; the stable retrieval evidence and promotion fingerprints then support downstream plan/revise/apply flows without rehydrating the whole retrieval result.

## Tasks Completed

1. Made SQLite FTS the authoritative MVP retrieval path while keeping PageIndex and embeddings fallback-only/deferred.
   Canonical demo-path step advanced: `FTS retrieval`.
2. Stabilized FTS cache and query normalization for query-shaped objects, dataclasses, mappings, iterables, date ranges, shortlist queries, fingerprints, doc types, scopes, boolean constraints, fresh runner output, cache invalidation, and cache audit metadata.
   Canonical demo-path step advanced: `FTS retrieval`.
3. Normalized retrieval payload, provenance, citation, source-bundle, context-bundle, basket-promotion, and evidence snapshots so sparse downstream helpers can rehydrate FTS-first payloads without losing constraints, fingerprints, ranks, identities, policies, section hints, promotion items, promotion fingerprints, doc type, matched terms, or confidentiality profile metadata.
   Canonical demo-path steps advanced: `retrieval evidence` and `context basket promotion`.
4. Added fail-closed retrieval boundary coverage for malformed or reversed date ranges, empty query/scope inputs, unresolved `doc:` and `collection:` scopes, FTS-only excerpt lookup, excerpt lookup fingerprints, cache/query snapshot behavior, and facade/export availability for basket-promotion helpers.
   Canonical demo-path steps advanced: `FTS retrieval` and `engine revise/apply` through stable retrieval facade contracts.

Task accounting: `4` high-risk task groups completed, matching the high-risk cap of `4`.

## Budget/Risk

- Task budget: `4` high-risk task groups; completed as the four task groups above.
- File count: `9 files` in the full reviewed packet range including `THREAD_PACKET.md`; `8 files` excluding the handoff packet itself.
- Size accounting: the corrected full source-bearing range exceeds the high-risk `<=300 net LOC` size limit. The actual source-bearing range through `b3b0e81e6a6754dfa3eaa3d21a01ee82817ad846` is `9 files changed, 888 insertions(+), 201 deletions(-)`, and the source/artifact/test portion excluding `THREAD_PACKET.md` is `8 files changed, 806 insertions(+), 129 deletions(-)`. This budget overage is reported explicitly for reviewer/integrator disposition rather than hidden behind a stale narrow range.
- Shared/integrator exception status: `tests/unit/test_unified_retrieval.py` is the sole approved shared regression surface; no integrator-locked files changed.
- Routing/provider impact: none.
- Remaining risks/blockers: size budget exceeded for the full corrected range; required gates are rerun and reported below after the actual final source-bearing commit and this packet refresh.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 Product Readiness generation provenance and Milestone 4 Retrieval Layer FTS-first retrieval orchestration/source attribution.
- Product Vision capability affected: `2. Retrieval-first context handling` and `3. Auditable generation`.
- Architecture alignment: retrieval stays in `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`; no provider/routing/core app entrypoints are touched.
- Proposed `README.md` patch text: none.

## Commands Run

Required gates rerun on `2026-05-06` for the corrected full reviewed range `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` after the source-bearing tip `b3b0e81e6a6754dfa3eaa3d21a01ee82817ad846`:

- `python -m unittest tests.unit.test_unified_retrieval` - passed 61 retrieval tests.
- `make scope-check` - passed for branch `codex/feat-retrieval-fts`; no branch-specific policy was configured.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 130 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/` (exit 0).
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 130 unit tests.
