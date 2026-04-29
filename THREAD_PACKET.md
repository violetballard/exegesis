## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this fixer pass; final SHA is reported in the fixer handoff.
- Reviewed range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD`
- Review choice: keep the current branch tip and regenerate the packet for the full branch-tip implementation range. The older narrowed `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice is obsolete and must not be used for approval.
- Canonical demo-path step advanced: retrieve relevant material through the FTS-first retrieval service, then expose stable context/promotion refs for downstream basket and workflow use.

## Required Fixes Addressed

1. The reviewable merge candidate is the branch tip. This packet uses `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD`, the actual merge-base-to-tip range for `codex/feat-retrieval-fts`.
2. The full implementation diff is in scope, including all post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` runtime retrieval and regression-test changes.
3. Files changed, task count, line/file budget accounting, shared-file exception notes, roadmap/product vision mapping, and canonical demo-path mapping are regenerated for the actual branch tip.
4. Gate results below are tied to this branch-tip merge candidate and must be refreshed again by the final fixer pass before re-review.

## Scope Completed

The branch delivers the cumulative FTS-first retrieval slice for the MVP engine workflow loop. SQLite FTS is the canonical retrieval path; PageIndex and embeddings remain compatibility/fallback shims rather than required paths. Retrieval query construction, payload normalization, provenance bundles, source/context bundles, cache snapshots, excerpt lookup, and downstream context refs are deterministic enough for engine orchestration and auditable handoff into basket/workflow flows.

Canonical demo path advanced by the full branch tip:

1. Retrieve relevant material through SQLite FTS-backed retrieval.
2. Preserve document/excerpt provenance and citations in deterministic payload snapshots.
3. Expose `retrieval_context_refs` and promotion-ready bundle data for downstream basket/context use.

## Tasks Completed

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, FTS-only excerpt lookup, guarded scope handling, compatibility exports, and fallback-only PageIndex/embedding shims.
2. Deterministic payloads: normalized queries, constraints, date ranges, cache keys, ranked IDs, hit snapshots, policy metadata, citation fields, and provenance/source/context bundles.
3. Basket/workflow promotion readiness: stable context refs, fingerprints, source bundle aliases, sparse bundle rehydration, and downstream helper backfills.
4. Regression and packet coverage: shared canonical retrieval tests plus packet planner coverage and branch-tip handoff metadata corrected for the actual merge candidate.

## Branch-Tip Files Changed

Matches `git diff --name-status d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD` for the true merge candidate:

- `M .codex/kickoff_packets/feat-retrieval-fts.md`
- `M .codex/lane_meta/feat-retrieval-fts.json`
- `M THREAD_PACKET.md`
- `M codex_packet_handoff/tools/planner.py`
- `M src/qual/engine/retrieval/__init__.py`
- `A src/qual/engine/retrieval/embeddings_strategy.py`
- `M src/qual/engine/retrieval/fts_strategy.py`
- `A src/qual/engine/retrieval/pageindex_strategy.py`
- `M src/qual/engine/retrieval/payload.py`
- `M src/qual/retrieval/__init__.py`
- `M src/qual/retrieval/service.py`
- `A tests/unit/test_packet_planner.py`
- `M tests/unit/test_unified_retrieval.py`

## Focused Regression Coverage

- `tests/unit/test_unified_retrieval.py` covers FTS-first retrieval behavior, FTS-only excerpt lookup, payload normalization, sparse bundle backfills, provenance/citation fields, fingerprint stability, and promotion-ready `retrieval_context_refs`.
- `tests/unit/test_packet_planner.py` covers packet-planner metadata emitted for handoff traceability.

## Budget / Risk

Risk/budget: high/shared because shared regression coverage and runtime retrieval payload/service behavior are included in the reviewed range. Recomputed from `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD`: task budget `4/4`; file budget `13/8`; size budget `13 files changed, 1938 insertions(+), 264 deletions(-)`, which is `1674` net LOC and exceeds the high-risk `<=300` net LOC cap. Integrator-locked files: none. Shared-by-approval files: `tests/unit/test_unified_retrieval.py` and `tests/unit/test_packet_planner.py` as regression/packet coverage for this lane. Routing/provider/core entrypoint impact: none.

## FTS-First Alignment Proof

`src/qual/retrieval/service.py` and `src/qual/engine/retrieval/fts_strategy.py` keep SQLite FTS canonical for retrieval and excerpt lookup. PageIndex and embeddings are compatibility/fallback surfaces only; they are not required for the MVP retrieval path. Context refs are built from canonical retrieval hits and carry FTS provenance so downstream basket/workflow consumers can audit source material.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 4, Retrieval Layer: FTS-first ingestion/index path, retrieval orchestration before drafting/diff generation, source-attribution model, and auditable deterministic retrieval paths.
- Roadmap item affected: `ROADMAP.md` Milestone 3, Product Readiness: generation provenance contract with retrieval evidence attached to outputs.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling: source documents are retrieved as chunks and SQLite FTS remains the current MVP retrieval path.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation: retrieved sources carry deterministic provenance, citation, fingerprint, and promotion references.
- Routing/provider impact: none. This branch does not change model routing, provider configuration, or provider compatibility behavior.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh branch-tip fixer pass: `make scope-check` PASS; `./quality-format.sh --check` PASS; `./quality-lint.sh` PASS; `./quality-test.sh` PASS (`124` tests); `./typecheck-test.sh` PASS; `make ci` PASS (`124` tests).

## Risks / Blockers

- The branch-tip merge candidate now has truthful traceability, but it exceeds the high-risk AGENTS size/file budget for a single thread. This is an explicit integration risk for re-review rather than an underreported packet slice.
- The `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` mirrors still contain stale narrowed-slice text because `apply_patch` rejected writes under `.codex` as outside the editable project boundary and direct filesystem write failed with `PermissionError: [Errno 1] Operation not permitted`. This `THREAD_PACKET.md` is the authoritative regenerated packet for re-review.
- Reviewers should evaluate `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD` as the merge candidate; any narrower `adfa8cd` or `378cf9a..adfa8cd` slice is obsolete.
