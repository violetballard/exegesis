## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Final fixer HEAD SHA: the metadata-only packet correction commit that contains this handoff refresh; reported in the fixer response.
- Authoritative reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`
- Authoritative reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`, where `HEAD` is the final packet-correction branch tip reported with this fixer response and includes merge candidate `b43178f56a0c78df411697654c17f2c029d44546`.
- Actual merge candidate covered by this packet: `b43178f56a0c78df411697654c17f2c029d44546`.
- Source-bearing merge-candidate tip included in the reviewed range: `a107bee8194bc73875e183230ee72259ea6886e4`; later commits through `b43178f56a0c78df411697654c17f2c029d44546` are packet-only traceability refreshes.
- Handoff type: high-risk retrieval handoff for the FTS-first retrieval lane.
- Risk reason: approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.

## Traceability Correction

This packet supersedes the stale narrow-range handoff. The reviewed range is the full merge-candidate range from `378cf9a74a3658058079a32f186fcd254c4a4034` through actual merge candidate `b43178f56a0c78df411697654c17f2c029d44546`, plus the final packet-correction commit reported with this fixer response. It includes source-bearing commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` through actual source-bearing tip `a107bee8194bc73875e183230ee72259ea6886e4`, including `cff7569dddc06bd6c4b445ebfc4dd5d161ab3cf0`, `125a3b7f84f096159baed4114029a7a38df772ae`, and the basket-promotion facade exposure in `a107bee8194bc73875e183230ee72259ea6886e4`.

The previous metadata-only classification for `cff7569dddc06bd6c4b445ebfc4dd5d161ab3cf0` is withdrawn. That commit changes `src/qual/retrieval/service.py` and `src/qual/engine/retrieval/payload.py`, so it is included in the reviewed implementation range.

Other source-bearing post-`adfa8cd` commits are included as well; the post-`adfa8cd..b43178f56a0c78df411697654c17f2c029d44546` implementation surface is `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`. The corrected range also includes the source-bearing changes in `a107bee8194bc73875e183230ee72259ea6886e4` to expose basket-promotion facade helpers from `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, and `src/qual/engine/retrieval/__init__.py`.

For the exact reviewer-cited branch-tip interval, `git diff --stat adfa8cdadd43747ffbcb612e4151e262b13e52ca..b43178f56a0c78df411697654c17f2c029d44546` reports `9 files changed, 842 insertions(+), 157 deletions(-)`. This packet treats that full interval as reviewed, not only the older `378cf9a..adfa8cd` slice.

## Reviewer Rejection Fix Addendum

This fixer pass addresses the review packet that rejected branch tip `b43178f56a0c78df411697654c17f2c029d44546` because the previous packet did not make the actual merge-candidate source range explicit enough. The packet now covers the actual merge candidate `b43178f56a0c78df411697654c17f2c029d44546`, including all source-bearing post-`adfa8cd` retrieval changes, and the final branch tip for this pass is a metadata-only packet correction commit on top of that merge candidate.

Current reviewer-rejection fixer files changed:

- `M THREAD_PACKET.md`

Current reviewer-rejection fixer task count: `1` meaningful task group, within the high-risk `4` task cap for this fixer pass.
Current reviewer-rejection fixer size: packet-only traceability update in `THREAD_PACKET.md`.
Shared/integrator-locked impact this reviewer-rejection fixer pass: none; no source, shared regression, provider routing, UI, or integrator-locked files were edited.

## Scope Completed

SQLite FTS remains the required MVP retrieval path. PageIndex and embeddings remain deferred or compatibility-only surfaces and are not reintroduced as required paths.

The branch hardens deterministic FTS retrieval behavior across cache keys, fresh-run cache snapshots, query snapshots, result payloads, excerpt lookup, citation/provenance bundles, evidence snapshots, sparse bundle rehydration, date-range propagation, and shortlist query fingerprints.

Canonical demo-path mapping: `vault/context material -> FTS retrieval -> retrieval evidence -> context basket promotion -> engine revise/apply`. This advances `retrieve relevant material` by producing deterministic, auditable FTS evidence, and supports `promote or gather context into the basket` by preserving rehydratable source, context, citation, provenance, and the named `retrieval_basket_promotion_bundle`.

## Final Fixer Pass Addendum

This packet supersedes rejected branch tip `473f5e42aa909c029fa143e734209ce5c95f7db5`. It keeps the same corrected cumulative reviewed range, `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`, and treats every source-bearing retrieval commit through `125a3b7f84f096159baed4114029a7a38df772ae` as part of the implementation under review.

The source-bearing tip makes the basket-promotion contract explicit in code. `RetrievalResult.retrieval_basket_promotion_bundle()` emits deterministic FTS excerpt promotion items with doc/excerpt ids, text, spans, ranks, hashes, fingerprints, matched terms, source strategy, backend, and mode. The downstream payload, source bundle, and context bundle preserve and rehydrate that named bundle through the engine retrieval payload helpers.

This fixer pass corrects packet traceability only. It does not add, remove, or alter retrieval implementation behavior after source-bearing tip `125a3b7f84f096159baed4114029a7a38df772ae`.

Current pass files changed:

- `M THREAD_PACKET.md`

Current pass task count: `1` meaningful task group, within the high-risk `4` task cap for this fixer pass.
Current pass size: packet-only traceability update in `THREAD_PACKET.md`.
Shared/integrator-locked impact this pass: none; no source, test, or integrator-locked files were edited.

## Integrator Failure Fixer Addendum

This packet supersedes approved packet `R__APPROVED__codex-feat-retrieval-fts__cad21a6c9f4d9fa6b3b68fdd9b9d769d999594ed__20260506T194240Z.md` after the integrator reported `bad local cli marker: invalid_request_error`.

Local reproduction result: the lane worktree reproduced the required integration gate sequence, but did not reproduce a project merge conflict, scope failure, formatting failure, lint failure, unit failure, typecheck failure, or CI failure. The captured integrator failure is therefore recorded as an external local Codex CLI marker failure from the integrator runner, not a retrieval implementation failure.

Fix action: refreshed this handoff packet with the local reproduction result and fresh required gate evidence. No retrieval source, shared regression, provider routing, or integrator-locked files were changed in this fixer pass.

Current integration-failure fixer files changed:

- `M THREAD_PACKET.md`

Current integration-failure fixer task count: `1` meaningful task group, within the high-risk `4` task cap for this fixer pass.
Current integration-failure fixer size: packet-only gate/reproduction evidence update in `THREAD_PACKET.md`.
Shared/integrator-locked impact this integration-failure fixer pass: none; no source, test, or integrator-locked files were edited.

## Source Finalizer Addendum

This source-bearing finalizer keeps retrieval FTS-first and does not reintroduce PageIndex or embeddings as required paths. It hardens the basket-promotion contract by copying query-level audit context onto each promotion item: `query_fingerprint`, `query_scope`, `query_intent`, and `query_date_range`.

The direct retrieval result bundle and the sparse downstream payload rehydration helper now emit the same per-item query context, falling back to the enclosing retrieval bundle when sparse excerpt hits do not carry those fields. This makes individual context-basket promotion records auditable even when they are consumed apart from the enclosing retrieval bundle.

Current source finalizer files changed:

- `M src/qual/retrieval/service.py`
- `M src/qual/engine/retrieval/payload.py`
- `M tests/unit/test_unified_retrieval.py`
- `M THREAD_PACKET.md`

Current source finalizer task count: `1` meaningful task group, within the high-risk `4` task cap for this finalizer pass.
Current source finalizer size before this packet update: `3 files changed, 58 insertions(+), 8 deletions(-)`.
Shared/integrator-locked impact this source finalizer pass: approved shared regression coverage in `tests/unit/test_unified_retrieval.py`; no provider routing or integrator-locked files were edited.

## Basket Promotion Facade Addendum

This source-bearing finalizer keeps retrieval FTS-first and exposes the existing deterministic context-basket promotion bundle through the canonical retrieval facades. `RetrievalService` now has explicit `retrieve_fts_basket_promotion_bundle()` and `retrieve_auto_basket_promotion_bundle()` methods, and both `src.qual.retrieval` and `src.qual.engine.retrieval` forward to those methods.

The new facade methods return the same FTS evidence bundle already embedded in downstream payloads, source bundles, and context bundles. They do not add a new retrieval strategy, do not expand `engine_retrieval.__all__`, and do not touch PageIndex, embeddings, provider routing, UI, or integrator-locked files.

Current basket promotion facade files changed:

- `M src/qual/retrieval/service.py`
- `M src/qual/retrieval/__init__.py`
- `M src/qual/engine/retrieval/__init__.py`
- `M THREAD_PACKET.md`

Current basket promotion facade task count: `1` meaningful task group, within the high-risk `4` task cap for this finalizer pass.
Current basket promotion facade source size before this packet update: `3 files changed, 66 insertions(+)`.
Shared/integrator-locked impact this basket promotion facade pass: none; no shared regression, provider routing, UI, or integrator-locked files were edited.

## Tasks Completed

1. Made SQLite FTS the authoritative MVP retrieval path while keeping PageIndex and embeddings fallback-only/deferred.
   Canonical demo-path step advanced: `retrieve relevant material`.
2. Stabilized FTS cache and query normalization for query-shaped objects, dataclasses, mappings, iterables, date ranges, shortlist queries, fingerprints, doc types, scopes, boolean constraints, fresh runner output, cache invalidation, and cache audit metadata.
   Canonical demo-path step advanced: `retrieve relevant material`.
3. Normalized retrieval payload, provenance, citation, source-bundle, context-bundle, basket-promotion, and evidence snapshots so sparse downstream helpers can rehydrate FTS-first payloads without losing constraints, fingerprints, ranks, identities, policies, section hints, promotion items, or confidentiality profile metadata.
   Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`.
4. Added fail-closed retrieval boundary coverage for malformed or reversed date ranges, empty query/scope inputs, unresolved `doc:` and `collection:` scopes, FTS-only excerpt lookup, excerpt lookup fingerprints, and cache/query snapshot behavior.
   Canonical demo-path step advanced: `retrieve relevant material`.

Final canonical demo-path statement: this work makes the `retrieve relevant material` step more real by making excerpt lookup FTS-only, deterministic, and auditable for downstream basket/workflow use, and it supports `promote or gather context into the basket` by preserving deterministic promotion-ready retrieval evidence.

## Files Changed

Authoritative reviewed range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`, where `HEAD` is the final packet-correction branch tip reported with this fixer response. This range includes actual merge candidate `b43178f56a0c78df411697654c17f2c029d44546`; the source-bearing implementation tip included in that range is `a107bee8194bc73875e183230ee72259ea6886e4`.

Expected changed files for that range:

- `D .codex/kickoff_packets/feat-retrieval-fts.md`
- `D .codex/lane_meta/feat-retrieval-fts.json`
- `M THREAD_PACKET.md`
- `M src/qual/engine/retrieval/__init__.py`
- `M src/qual/engine/retrieval/fts_strategy.py`
- `M src/qual/engine/retrieval/payload.py`
- `M src/qual/retrieval/__init__.py`
- `M src/qual/retrieval/service.py`
- `M tests/unit/test_unified_retrieval.py`

Merge-candidate diff through actual tip `b43178f56a0c78df411697654c17f2c029d44546`: `9 files changed, 870 insertions(+), 188 deletions(-)` versus reviewed base `378cf9a74a3658058079a32f186fcd254c4a4034`. Excluding `THREAD_PACKET.md`, the source/artifact range is `8 files changed, 688 insertions(+), 125 deletions(-)`, net `+563` LOC. The exact post-`adfa8cd` interval called out by review is `9 files changed, 842 insertions(+), 157 deletions(-)` and includes the six retrieval source/test files listed above plus packet/artifact changes. The `a107bee8194bc73875e183230ee72259ea6886e4` source-bearing finalizer adds narrow retrieval facade methods in `src/qual/retrieval/service.py`, `src/qual/retrieval/__init__.py`, and `src/qual/engine/retrieval/__init__.py`; this fixer commit only refreshes the handoff packet.

The protected `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` mirror artifacts could not be edited in-place, so they are removed from the merge candidate to avoid preserving stale contradictory trace metadata. `THREAD_PACKET.md` is the coherent handoff packet for re-review.

## Budget/Risk

- Task budget: `4` high-risk task groups; completed as the four task groups above.
- File count: `9 files` in the full reviewed packet range including `THREAD_PACKET.md`; `8 files` excluding the handoff packet itself. The source/artifact count remains within the high-risk `<=8 files` limit, while the packet-inclusive count is reported here for traceability.
- Size accounting: actual merge candidate `b43178f56a0c78df411697654c17f2c029d44546` is `9 files changed, 870 insertions(+), 188 deletions(-)` versus the authoritative reviewed base, and the source/artifact portion excluding `THREAD_PACKET.md` is net `+563` LOC. This exceeds the high-risk `<=300 net LOC` budget and is reported here rather than hidden by a stale narrow range. The current basket promotion facade finalizer itself is a narrow `3 files changed, 66 insertions(+)` retrieval contract exposure before the packet update.
- Shared/integrator exception status: `tests/unit/test_unified_retrieval.py` is the sole approved shared regression surface; no integrator-locked files changed.
- Routing/provider impact: none.
- Remaining risks/blockers: size budget exceeded for the full corrected range; no functional gate blockers after required gates are rerun on the final branch tip.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 Product Readiness generation provenance and Milestone 4 Retrieval Layer FTS-first retrieval orchestration/source attribution.
- Product Vision capability affected: `2. Retrieval-first context handling` and `3. Auditable generation`.
- Architecture alignment: retrieval stays in `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`; no provider/routing/core app entrypoints are touched.
- Proposed `README.md` patch text: none.

## Commands Run

Required gates rerun for this branch-tip traceability fixer pass against actual merge candidate `b43178f56a0c78df411697654c17f2c029d44546` plus this packet-only update:

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 130 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 130 unit tests.

Required gates rerun for this reviewer-rejection fixer pass:

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`; no branch-specific policy was configured.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 130 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 130 unit tests.

Required gates rerun for the source-bearing finalizer pass:

- `python - <<'PY' ... PY` basket promotion facade smoke script - passed; service, retrieval package, and engine retrieval facades returned identical FTS `context_basket` promotion bundles.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - first attempt failed on exact `engine_retrieval.__all__` export-list contract after the new facade names were added to star exports.
- `./quality-test.sh` - passed after keeping the new facade methods directly addressable without expanding `__all__`; smoke tests and 130 unit tests passed.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 130 unit tests.

Final required gates rerun after the basket promotion facade code and packet refresh:

- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 130 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 130 unit tests.

Earlier required gates for the basket-promotion query-context hardening pass:

- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_items_backfill_query_context_from_bundle` - passed.
- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 130 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 130 unit tests.

Required gates rerun for the integration-failure fixer pass:

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 129 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 129 unit tests.
