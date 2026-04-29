## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this fixer pass; final SHA is reported in the fixer handoff.
- Reviewed range: `378cf9a7..HEAD`
- Reviewed implementation range: `378cf9a7..HEAD`
- Review choice: review the true branch tip `378cf9a7..HEAD`; the branch now removes the unreported post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` drift in `src/qual/engine/retrieval/fts_strategy.py` and `src/qual/engine/retrieval/payload.py`.
- Pre-fix reviewer-cited branch tip: `ead1fb765fc849afee373e2d3d6db61264b8cf48`

## Required Fixes Addressed

The merge candidate is the branch tip, not an obsolete narrowed packet slice. The actual `378cf9a7..HEAD` runtime scope is included in tasks, file list, roadmap/vision mapping, risk accounting, and gate reporting. Post-`adfa8cd` runtime drift outside the reviewed FTS-only excerpt scope was removed before this packet stamp, so `ead1fb765fc849afee373e2d3d6db61264b8cf48` is no longer represented as a metadata-only commit with live branch-tip runtime changes. FTS-first alignment is explicit: PageIndex and embeddings remain deferred/fallback compatibility paths, not required MVP retrieval paths.

## Scope Completed

The branch delivers the FTS-first retrieval slice for the MVP engine workflow loop. SQLite FTS is authoritative; PageIndex and embeddings remain fallback shims only. Canonical excerpt lookup fails closed for unsupported IDs, payload snapshots are deterministic, and retrieved document/excerpt/provenance refs are stable for downstream basket/workflow use. The final branch-tip runtime diff is the FTS-only excerpt lookup behavior in `src/qual/retrieval/service.py` plus shared regression coverage in `tests/unit/test_unified_retrieval.py`.

## Tasks Completed

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, fallback-only PageIndex behavior, and FTS-only excerpt lookup. Canonical demo path advanced: retrieve relevant material.
2. Deterministic payloads: normalized constraints, source/context bundles, provenance/citation backfills, cache keys, and hit snapshots retained from the reviewed implementation scope. Canonical demo path advanced: retrieve relevant material.
3. Basket/workflow promotion readiness: stable refs, fingerprints, and auditable excerpt/context refs for downstream basket use retained from the reviewed implementation scope. Canonical demo path advanced: promote retrieved material into basket/workflow state.
4. Regression and handoff coverage: shared canonical retrieval coverage plus branch-tip packet metadata corrected for the actual merge candidate. Canonical demo path advanced: keep retrieval behavior reviewable before draft/revise/apply steps.

## Branch-Tip Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`: packet mirror changed earlier in the branch range, but this sandbox rejects writes to refresh its stale `adfa8cd` wording.
- `.codex/lane_meta/feat-retrieval-fts.json`: lane metadata changed earlier in the branch range, but this sandbox rejects writes to refresh its stale `adfa8cd` wording.
- `THREAD_PACKET.md`: handoff packet regenerated for branch-tip review.
- `src/qual/retrieval/service.py`: canonical FTS-only excerpt lookup.
- `tests/unit/test_unified_retrieval.py`: approved shared regression coverage for the canonical retrieval contract.

## Budget / Risk

Risk/budget: high/shared because `tests/unit/test_unified_retrieval.py` is approved shared regression coverage. Recomputed from `378cf9a7..HEAD`: task budget `4/4`; file budget `5/8`; size before this packet-only fixer commit is `5` files, `255` insertions, `131` deletions, net `+124`, within the high-risk `<=300` net LOC cap. Integrator-locked files: none. Routing/provider/core entrypoint impact: none.

## FTS-First Alignment Proof

`src/qual/retrieval/service.py` keeps SQLite FTS canonical for excerpt lookup. `src/qual/engine/retrieval/fts_strategy.py` remains the MVP retrieval strategy, `src/qual/engine/retrieval/payload.py` remains the deterministic payload/provenance normalizer, and neither file is changed in the final `378cf9a7..HEAD` merge-candidate diff. PageIndex/embeddings files are not edited in `378cf9a7..HEAD`. Shared coverage exercises FTS-only excerpt backfill and canonical retrieval behavior.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 4, Retrieval Layer: FTS-first ingestion/index path, retrieval orchestration before drafting/diff generation, source-attribution model, and deferral of PageIndex/embeddings until after the demo push.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling: source documents are retrieved as chunks, SQLite FTS is the current MVP retrieval path, and PageIndex/embeddings are deferred.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation: retrieved sources now carry deterministic provenance, citation, fingerprint, and promotion references.
- Routing/provider impact: none. This branch does not change model routing, provider configuration, or provider compatibility behavior.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh fixer pass on the branch-tip merge candidate: `make scope-check` PASS; `./quality-format.sh --check` PASS; `./quality-lint.sh` PASS; `./quality-test.sh` PASS (`124` tests); `./typecheck-test.sh` PASS; `make ci` PASS (`124` tests).

## Risks / Blockers

- Merge risk remains high because the branch-tip reviewed range includes approved shared regression coverage.
- Reviewers should evaluate `378cf9a7..HEAD` as the merge candidate; any narrower `adfa8cd` slice is obsolete.
- Packet mirror blocker: this sandbox rejects writes to `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` with `Operation not permitted`. `THREAD_PACKET.md` is the corrected handoff source of truth for re-review.
