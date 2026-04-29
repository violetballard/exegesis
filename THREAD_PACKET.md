## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this fixer pass; final SHA is reported in the fixer handoff.
- Reviewed range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Review choice: make the branch-tip implementation match the reviewed `adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice; later commits are metadata-only for runtime code.
- Pre-fix reviewer-cited branch tip: `343757023`
- Pre-fix packet tip before this fixer pass: `ead1fb765`

## Required Fixes Addressed

The merge candidate now contains the reviewed `adfa8cdadd43747ffbcb612e4151e262b13e52ca` implementation plus metadata-only packet commits. Post-`adfa8cd` runtime drift in `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, and `src/qual/retrieval/service.py` was reverted in this fixer pass. FTS-first alignment is explicit: PageIndex and embeddings remain deferred/fallback compatibility paths, not required MVP retrieval paths.

## Scope Completed

The branch delivers the reviewed FTS-first retrieval slice for the MVP engine workflow loop. SQLite FTS is authoritative; PageIndex and embeddings remain fallback shims only. Canonical excerpt lookup fails closed for unsupported IDs, payload snapshots are deterministic, and retrieved document/excerpt/provenance refs are stable for basket/workflow promotion. The branch tip no longer contains unreviewed post-`adfa8cd` runtime retrieval changes.

## Tasks Completed

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, fallback-only PageIndex behavior, and FTS-only excerpt lookup.
2. Deterministic payloads: normalized constraints, source/context bundles, provenance/citation backfills, cache keys, and hit snapshots.
3. Basket/workflow promotion readiness: stable refs, fingerprints, and auditable excerpt/context refs for downstream basket use.
4. Regression and handoff coverage: shared canonical retrieval coverage plus branch-tip packet metadata corrected so runtime code matches the reviewed slice.

## Branch-Tip Files Changed

Runtime/test changes in the reviewed implementation range are `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`. Packet metadata changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` do not change the reviewed runtime implementation.

## Budget / Risk

Risk/budget: high/shared because `tests/unit/test_unified_retrieval.py` is approved shared regression coverage; task budget `4/4`; reviewed implementation files `4/8`; integrator-locked files: none.

## FTS-First Alignment Proof

`src/qual/retrieval/service.py` keeps SQLite FTS canonical for excerpt lookup. `src/qual/engine/retrieval/fts_strategy.py` remains the MVP retrieval strategy, `src/qual/engine/retrieval/payload.py` normalizes FTS-backed hits into deterministic payload/provenance records, and PageIndex/embeddings files are not edited in the reviewed implementation range. Shared coverage exercises FTS-only excerpt backfill and canonical retrieval behavior.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 4, Retrieval Layer: FTS-first ingestion/index path, retrieval orchestration before drafting/diff generation, source-attribution model, and deferral of PageIndex/embeddings until after the demo push.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling: source documents are retrieved as chunks, SQLite FTS is the current MVP retrieval path, and PageIndex/embeddings are deferred.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation: retrieved sources now carry deterministic provenance, citation, fingerprint, and promotion references.
- Routing/provider impact: none. This branch does not change model routing, provider configuration, or provider compatibility behavior.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh fixer pass on the corrected merge candidate: `make scope-check` PASS (`no policy for branch`, then passed), `./quality-format.sh --check` PASS, `./quality-lint.sh` PASS, `./quality-test.sh` PASS (`124` tests), `./typecheck-test.sh` PASS, and `make ci` PASS (`124` tests).

## Risks / Blockers

- Merge risk remains high because the branch-tip reviewed range includes approved shared regression coverage.
- Reviewers should evaluate the runtime implementation against `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`; branch-tip commits after that point are metadata-only or this fixer revert.
- Packet mirror blocker: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` already describe the reviewed `adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice and cannot be rewritten in this sandbox (`Operation not permitted`). That is now consistent with the corrected branch-tip runtime state.
