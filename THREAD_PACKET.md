## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this fixer pass; final SHA is reported in the fixer handoff.
- Reviewed range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`
- Review choice: review the true branch tip, including the runtime retrieval changes originally introduced after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and the follow-up context-ref fingerprint fix.
- Pre-fix reviewer-cited commits: `68f23aa26ae0be2b043484d61aa6fa5c4c3f10bd` and `0d9723f6be77cb1be30ae97f7bfe82c1dd2d1698`.
- Canonical demo-path step advanced: retrieve relevant material.

## Required Fixes Addressed

The merge candidate is the branch tip, not an obsolete narrowed packet slice. The actual `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` runtime scope is included in tasks, file list, roadmap/vision mapping, risk accounting, and gate reporting. The branch keeps the promotion-ready context ref behavior and explicitly includes `src/qual/engine/retrieval/payload.py` and `src/qual/retrieval/service.py` in the reviewed implementation scope.

## Scope Completed

The branch delivers the FTS-first retrieval slice for the MVP engine workflow loop. SQLite FTS is authoritative; PageIndex and embeddings remain fallback/deferred compatibility paths. Canonical excerpt lookup fails closed for unsupported IDs, payload snapshots are deterministic, and retrieved document/excerpt/provenance refs now include promotion-ready context refs for downstream basket/workflow use.

Canonical demo path advanced by the full branch tip:

1. Retrieve relevant material through the FTS-first retrieval service.
2. Promote or gather retrieved excerpts into basket/context-ready state through stable `retrieval_context_refs`.

## Tasks Completed

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, fallback-only PageIndex behavior, and FTS-only excerpt lookup. Canonical demo path advanced: retrieve relevant material.
2. Deterministic payloads: normalized constraints, source/context bundles, provenance/citation backfills, cache keys, and hit snapshots retained across helper facades. Canonical demo path advanced: retrieve relevant material.
3. Basket/workflow promotion readiness: stable refs, fingerprints, and auditable excerpt/context refs added to downstream payloads, source bundles, context bundles, doc/excerpt bundles, and helper backfills. Canonical demo path advanced: promote or gather context into the basket.
4. Regression and handoff coverage: shared canonical retrieval coverage plus branch-tip packet metadata corrected for the actual merge candidate. Canonical demo path advanced: keep retrieval and context-promotion behavior reviewable before draft/revise/apply steps.

## Packet Mirror Write Blocker

The patch tool rejects edits under `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` as outside the editable project boundary during this fixer pass. This `THREAD_PACKET.md` is therefore the authoritative regenerated handoff packet for re-review and supersedes stale mirror text that still references `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the implementation head.

## Branch-Tip Files Changed

Matches `git diff --name-status 378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` for the true merge candidate:

- `M .codex/kickoff_packets/feat-retrieval-fts.md`
- `M .codex/lane_meta/feat-retrieval-fts.json`
- `M THREAD_PACKET.md`
- `M src/qual/engine/retrieval/payload.py`
- `M src/qual/retrieval/service.py`
- `M tests/unit/test_unified_retrieval.py`

## Focused Regression Coverage

- `tests/unit/test_unified_retrieval.py::UnifiedRetrievalTests::test_retrieval_context_bundle_helper_packages_payload_and_bundles` asserts `retrieval_context_refs` are present, FTS-only, fingerprinted, provenance-linked, and snapshot-safe.
- `tests/unit/test_unified_retrieval.py::UnifiedRetrievalTests::test_retrieval_downstream_payload_helper_backfills_sparse_context_bundle_fields` removes sparse downstream `retrieval_context_refs` and verifies helper backfill restores the context refs from the context/source bundle.
- Existing canonical FTS tests in `tests/unit/test_unified_retrieval.py` cover FTS-only excerpt fetch and rejection of PageIndex excerpt payloads.

## Budget / Risk

Risk/budget: high/shared because `tests/unit/test_unified_retrieval.py` is approved shared regression coverage and the reviewed range includes runtime retrieval payload/service behavior. Recomputed from `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`: task budget `4/4`; file budget `6/8`; size budget remains within the high-risk `<=300` net LOC cap after this packet fixer commit is reviewed against its final SHA. Integrator-locked files: none. Routing/provider/core entrypoint impact: none.

## FTS-First Alignment Proof

`src/qual/retrieval/service.py` keeps SQLite FTS canonical for retrieval and excerpt lookup. `src/qual/engine/retrieval/fts_strategy.py` remains the MVP retrieval strategy, and PageIndex/embeddings remain deferred/fallback paths. The context refs are built only from FTS hits (`ref_id` uses `fts:<excerpt_id>`, `source_strategy` is `fts`, and `retrieval_backend` is `sqlite_fts`).

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 4, Retrieval Layer: FTS-first ingestion/index path, retrieval orchestration before drafting/diff generation, source-attribution model, and deferral of PageIndex/embeddings until after the demo push.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling: source documents are retrieved as chunks, SQLite FTS is the current MVP retrieval path, and retrieved excerpts are made basket/context-ready through stable context refs.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation: retrieved sources now carry deterministic provenance, citation, fingerprint, and promotion references.
- Routing/provider impact: none. This branch does not change model routing, provider configuration, or provider compatibility behavior.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh fixer pass on the branch-tip merge candidate: `make scope-check` PASS; `./quality-format.sh --check` PASS; `./quality-lint.sh` PASS; `./quality-test.sh` PASS (`124` tests); `./typecheck-test.sh` PASS; `make ci` PASS (`124` tests).

## Risks / Blockers

- Merge risk remains high because the branch-tip reviewed range includes approved shared regression coverage and runtime retrieval payload/service changes.
- Reviewers should evaluate `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` as the merge candidate; any narrower `adfa8cd` slice is obsolete.
