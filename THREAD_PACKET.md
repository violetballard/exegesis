## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this fixer pass.
- Reviewed range: `378cf9a7..HEAD`
- Reviewed implementation range: `378cf9a7..HEAD`
- Review choice: review the true branch tip, not the narrowed `adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice.
- Pre-fix reviewer-cited branch tip: `343757023`
- Pre-fix packet tip before this fixer pass: `ff9f658dfdfc429ceecc800ccfce33244498b263`

## Required Fixes Addressed

1. The merge candidate is the branch tip. This packet does not treat `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the reviewed endpoint.
2. All post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` implementation changes are included in scope, files changed, completed tasks, budget accounting, and roadmap/vision mapping.
3. Required gates are rerun against the exact branch-tip merge candidate and recorded below.
4. FTS-first alignment is explicit: PageIndex and embeddings remain deferred/fallback compatibility paths, not required MVP retrieval paths.

## Scope Completed

The branch delivers the FTS-first retrieval slice for the MVP engine workflow loop. SQLite FTS is the authoritative retrieval path; PageIndex and embeddings remain fallback shims only. Canonical excerpt lookup fails closed for unsupported IDs, FTS cache state is invalidated after document writes, payload snapshots are deterministic, and retrieved document/excerpt/provenance references are stable for basket and workflow promotion.

The branch-tip review range includes the post-`adfa8cd` runtime retrieval work in `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `src/qual/engine/retrieval/fts_strategy.py`.

## Tasks Completed

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, fallback-only PageIndex behavior, document-update cache invalidation, and FTS-only excerpt lookup.
2. Deterministic payloads: normalized constraints, source/context bundles, provenance/citation backfills, cache keys, and hit snapshots.
3. Basket/workflow promotion readiness: stable refs, promotion candidates, fingerprints, ranked IDs, context status, and audit fields.
4. Regression and handoff coverage: shared canonical retrieval coverage plus branch-tip packet metadata corrected for the actual merge candidate.

## Branch-Tip Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`: stale packet mirror from earlier commits; this sandbox rejects writes to this protected file.
- `.codex/lane_meta/feat-retrieval-fts.json`: stale metadata mirror from earlier commits; this sandbox rejects writes to this protected file.
- `THREAD_PACKET.md`: handoff packet regenerated for branch-tip review.
- `src/qual/engine/retrieval/fts_strategy.py`: FTS cache isolation and copied hit snapshots.
- `src/qual/engine/retrieval/payload.py`: deterministic payload normalization, provenance backfills, and basket promotion refs.
- `src/qual/retrieval/service.py`: cache invalidation after document updates, stable fingerprints, and doc/excerpt promotion refs.
- `tests/unit/test_unified_retrieval.py`: approved shared regression coverage for the canonical retrieval contract.

## Budget / Risk

- Risk: high/shared because `tests/unit/test_unified_retrieval.py` is approved shared regression coverage.
- Task budget: `4/4`.
- File budget: `7/8`.
- Size budget before this fixer metadata update: `7` files, `438` insertions, `143` deletions, net `+295` in `378cf9a7..ff9f658dfdfc429ceecc800ccfce33244498b263`; within the high-risk `<=300` net LOC cap.
- Size budget after this fixer metadata update: recompute with `git diff --numstat 378cf9a7..HEAD` during review; the only additional changes in this pass are packet metadata.
- Integrator-locked files: none.

## FTS-First Alignment Proof

- `src/qual/retrieval/service.py` keeps SQLite FTS as the canonical retrieval path and invalidates FTS query cache entries after writes.
- `src/qual/engine/retrieval/fts_strategy.py` remains the engine strategy for MVP retrieval and returns isolated hit snapshots.
- `src/qual/engine/retrieval/payload.py` normalizes retrieved FTS-backed hits into deterministic payload/provenance records.
- PageIndex and embeddings files are not edited in the branch-tip review range `378cf9a7..HEAD`; they are not reintroduced as required MVP retrieval paths.
- Shared coverage in `tests/unit/test_unified_retrieval.py` exercises FTS-only excerpt backfill and canonical retrieval behavior.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 4, Retrieval Layer: FTS-first ingestion/index path, retrieval orchestration before drafting/diff generation, source-attribution model, and deferral of PageIndex/embeddings until after the demo push.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling: source documents are retrieved as chunks, SQLite FTS is the current MVP retrieval path, and PageIndex/embeddings are deferred.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation: retrieved sources now carry deterministic provenance, citation, fingerprint, and promotion references.
- Routing/provider impact: none. This branch does not change model routing, provider configuration, or provider compatibility behavior.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh fixer pass on the branch-tip merge candidate:

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.

## Risks / Blockers

- Merge risk remains high because the branch-tip reviewed range includes approved shared regression coverage.
- Reviewers should evaluate `378cf9a7..HEAD` as the merge candidate; any narrower `adfa8cd` slice is obsolete.
- Packet mirror blocker: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still carry stale `adfa8cdadd43747ffbcb612e4151e262b13e52ca` packet text because this sandbox rejects writes to those protected `.codex` files with `Operation not permitted`. Use this `THREAD_PACKET.md` as the corrected handoff source of truth for re-review.
