## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this fixer pass.
- Reviewed range: `378cf9a7..HEAD`
- Reviewed implementation range: `378cf9a7..HEAD`
- Review choice: review the true branch tip, not the narrowed `adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice.
- Pre-fix reviewer-cited branch tip: `343757023`
- Pre-fix packet tip before this fixer pass: `3b00f1025`

## Required Fixes Addressed

The merge candidate is the branch tip, not `adfa8cdadd43747ffbcb612e4151e262b13e52ca`; post-`adfa8cd` implementation changes are included in scope, files, tasks, budget, roadmap/vision mapping, and gates. FTS-first alignment is explicit: PageIndex and embeddings remain deferred/fallback compatibility paths, not required MVP retrieval paths.

## Scope Completed

The branch delivers the FTS-first retrieval slice for the MVP engine workflow loop. SQLite FTS is authoritative; PageIndex and embeddings remain fallback shims only. Canonical excerpt lookup fails closed for unsupported IDs, FTS cache state is invalidated after document writes, payload snapshots are deterministic, and retrieved document/excerpt/provenance refs are stable for basket/workflow promotion. This fixer pass also adds query date range, candidate document count, and FTS shortlist IDs to canonical `retrieval_evidence` so basket promotion and later revise/apply steps can audit the retrieval set without reading diagnostics. The branch-tip review range includes the post-`adfa8cd` runtime retrieval work in `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `src/qual/engine/retrieval/fts_strategy.py`.

## Tasks Completed

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, fallback-only PageIndex behavior, document-update cache invalidation, and FTS-only excerpt lookup.
2. Deterministic payloads: normalized constraints, source/context bundles, provenance/citation backfills, cache keys, and hit snapshots.
3. Basket/workflow promotion readiness: stable refs, promotion candidates, fingerprints, ranked IDs, context status, retrieval-set evidence, and audit fields.
4. Regression and handoff coverage: shared canonical retrieval coverage plus branch-tip packet metadata corrected for the actual merge candidate.

## Branch-Tip Files Changed

`.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are stale packet mirrors from earlier commits that this sandbox cannot rewrite; use `THREAD_PACKET.md` as source of truth. Runtime/test changes are `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`. This fixer pass changes only `src/qual/retrieval/service.py` plus this handoff packet.

## Budget / Risk

Risk/budget: high/shared because `tests/unit/test_unified_retrieval.py` is approved shared regression coverage; task budget `4/4`; file budget `7/8`; final `378cf9a7..HEAD` remains within the high-risk `<=300` net LOC cap after this packet trim. Integrator-locked files: none.

## FTS-First Alignment Proof

`src/qual/retrieval/service.py` keeps SQLite FTS canonical, invalidates FTS query cache entries after writes, and now carries retrieval-set evidence directly in `retrieval_evidence`. `src/qual/engine/retrieval/fts_strategy.py` remains the MVP retrieval strategy, `src/qual/engine/retrieval/payload.py` normalizes FTS-backed hits into deterministic payload/provenance records, and PageIndex/embeddings files are not edited in `378cf9a7..HEAD`. Shared coverage exercises FTS-only excerpt backfill and canonical retrieval behavior.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 4, Retrieval Layer: FTS-first ingestion/index path, retrieval orchestration before drafting/diff generation, source-attribution model, and deferral of PageIndex/embeddings until after the demo push.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling: source documents are retrieved as chunks, SQLite FTS is the current MVP retrieval path, and PageIndex/embeddings are deferred.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation: retrieved sources now carry deterministic provenance, citation, fingerprint, and promotion references.
- Routing/provider impact: none. This branch does not change model routing, provider configuration, or provider compatibility behavior.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh fixer pass on the branch-tip merge candidate: `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh` (`124` tests), `./typecheck-test.sh`, `make scope-check`, and `make ci` (`124` tests): PASS. Direct `python -m pytest tests/unit/test_unified_retrieval.py` was attempted first and could not run because this Python environment has no `pytest` module; the repo-required `quality-test.sh` path passed.

## Risks / Blockers

- Merge risk remains high because the branch-tip reviewed range includes approved shared regression coverage.
- Reviewers should evaluate `378cf9a7..HEAD` as the merge candidate; any narrower `adfa8cd` slice is obsolete.
- Packet mirror blocker: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still carry stale `adfa8cdadd43747ffbcb612e4151e262b13e52ca` packet text because this sandbox rejects writes to those protected `.codex` files with `Operation not permitted`. Use this `THREAD_PACKET.md` as the corrected handoff source of truth for re-review.
