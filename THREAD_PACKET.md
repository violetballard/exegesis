## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Authoritative merge/review range for the actual integration candidate: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`
- Current pre-fix branch tip audited for source/test surface: `0e0f34cf763a26a2c21eb5813bf4d16227be96d5`
- Merge candidate: the branch tip after this reviewer-fix commit. It is not `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, `e4f835c50`, or `43654937a196977d7cd53c4e355b4f8ea7fb93b7`.
- Scope classification: high-risk/shared because the candidate includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Packet type: retrieval feature handoff for the full branch-tip FTS-first retrieval candidate.

## Scope Completed

The actual branch-tip candidate keeps SQLite FTS as the only active retrieval path and reconciles the handoff with the full source/test surface from `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`. The candidate exports canonical retrieval query construction through the engine retrieval facade, normalizes boolean constraints deterministically, removes stale FTS strategy caching, makes payload/source/context snapshots deterministic, adds policy-bound basket-promotion item fingerprints, and keeps excerpt lookup on the canonical FTS-only path so PageIndex-only excerpt IDs fail closed under shared regression coverage.

PageIndex and embeddings remain compatibility-only fallback shims and are not reintroduced as required retrieval paths. This packet supersedes earlier narrowed claims that stopped at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, `e4f835c50`, or `43654937a196977d7cd53c4e355b4f8ea7fb93b7`; re-review should inspect the full `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` candidate.

## Required Fixes Addressed

1. Reproduced the reported integrator failure context locally by reading the captured integrator prompt and rerunning the lane/integration gates on the branch-tip candidate; no retrieval test, typecheck, lint, format, scope, CI, or merge-tree conflict failure reproduced.
2. Fixed the review-facing handoff packet to present the actual branch-tip candidate range. The tracked `.codex` packet mirrors still cannot be edited in this lane sandbox because writes fail with `Operation not permitted`, so `THREAD_PACKET.md` remains the authoritative corrected feature packet for re-review.
3. Kept post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` commits classified accurately: commits touching `src/qual/engine/retrieval/**`, `src/qual/retrieval/**`, or `tests/unit/test_unified_retrieval.py` are implementation commits, not metadata-only commits.
4. Rerun results for `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` are recorded below against the corrected branch-tip candidate for fresh re-review.

## Integrator Failure Reproduction

- Referenced integrator prompt existed and contained an approved fallback packet with no requested code fixes.
- Local branch-tip gates all pass on this lane worktree.
- `git merge-tree $(git merge-base codex/integrator HEAD) codex/integrator HEAD` reports a clean textual merge for the candidate files; no conflict marker output was produced.
- The actionable integration blocker found in-lane was stale packet metadata that could cause automation to re-submit or review the old narrowed implementation head instead of the actual branch tip. The corrected branch-tip packet is recorded in `THREAD_PACKET.md`.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: kept retrieval FTS-first by making excerpt lookup require an FTS excerpt hit, removing stale FTS strategy caching, and keeping PageIndex/embeddings fallback-only.
2. Canonical demo-path step `retrieve relevant material`: exported and normalized canonical retrieval query construction through the engine retrieval facade, including deterministic boolean and date constraint handling.
3. Canonical demo-path step `retrieve relevant material`: made retrieval payloads, provenance snapshots, citation bundles, and sparse source/context rehydration deterministic for downstream engine flows.
4. Canonical demo-path step `promote or gather context into the basket`: added deterministic basket-promotion refs, item IDs, context-bundle fingerprints, policy snapshots on basket refs, and `basket_item_fingerprint` backfill for sparse excerpt-hit snapshots.

## Post-`adfa8cd` Classification

The branch contains implementation commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`; they are part of this merge candidate and are included in the reviewed range:

- `src/qual/engine/retrieval/__init__.py`: post-`adfa8cd` retrieval facade export and constraint-normalization commits are implementation.
- `src/qual/engine/retrieval/fts_strategy.py`: post-`adfa8cd` cache invalidation/removal and hit snapshot commits are implementation.
- `src/qual/engine/retrieval/payload.py`: post-`adfa8cd` payload, context bundle, basket ref, fingerprint, and sparse rehydration commits are implementation.
- `src/qual/retrieval/service.py`: post-`adfa8cd` FTS service, citation, evidence context, basket promotion, query snapshot, and policy-bound fingerprint commits are implementation.
- `tests/unit/test_unified_retrieval.py`: post-`adfa8cd` shared regression coverage commits are implementation-test commits under the approved shared-file exception.
- `THREAD_PACKET.md`, `.codex/kickoff_packets/feat-retrieval-fts.md`, and `.codex/lane_meta/feat-retrieval-fts.json`: packet and lane metadata refresh commits are metadata.

## Files Changed

Authoritative candidate files changed for `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`:

- `.codex/kickoff_packets/feat-retrieval-fts.md` - stale packet mirror present in the candidate; this fixer session could not refresh it because filesystem writes under `.codex` fail with `Operation not permitted`.
- `.codex/lane_meta/feat-retrieval-fts.json` - stale lane metadata mirror present in the candidate; this fixer session could not refresh it because filesystem writes under `.codex` fail with `Operation not permitted`.
- `THREAD_PACKET.md` - handoff packet regenerated for the actual branch-tip candidate.
- `src/qual/engine/retrieval/__init__.py` - exports canonical query construction with strict optional-boolean normalization.
- `src/qual/engine/retrieval/fts_strategy.py` - removes stale result caching while preserving the compatibility `clear_cache` hook.
- `src/qual/engine/retrieval/payload.py` - normalizes deterministic retrieval payloads, source/context bundles, policy-bound basket-promotion items, and sparse snapshot backfill.
- `src/qual/retrieval/service.py` - keeps FTS as the authoritative lookup path and emits deterministic result/query/policy-bound basket fingerprints.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage for cache invalidation, deterministic payloads, facade exports, basket refs, and FTS-only excerpt lookup.

Full corrected candidate stat including this reviewer-fix packet refresh: `8 files changed, 980 insertions(+), 207 deletions(-)`.

Source/test surface included for review:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Source/test stat included for implementation review: `5 files changed, 690 insertions(+), 119 deletions(-)`.

Lane-owned source files:

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`

Shared-by-approval files:

- `tests/unit/test_unified_retrieval.py` - approved shared regression surface for the retrieval lane.

Out-of-lane tooling files:

- None.

Integrator-locked files:

- None.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `8/8` high-risk files in the corrected candidate.
- Source/test file count: `5` files.
- Full corrected candidate net LOC including this reviewer-fix packet refresh: `+773`.
- Source/test net LOC included for implementation review: `+571`.
- Size exception required: yes. The candidate exceeds the AGENTS.md high-risk `<=300` net LOC guideline because the actual branch-tip surface includes the full retrieval payload/service/test implementation, not only the earlier narrowed packet slice.
- Explicit size exception request: approve review of the full `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` candidate as a single high-risk retrieval handoff because splitting the already-committed branch tip would reintroduce the traceability gap the reviewer flagged.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is included as the approved shared-by-approval regression surface for the retrieval lane.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; PageIndex and embeddings remain deferred/compatibility-only and are not active retrieval paths.
- Merge risk: high until reviewer accepts the corrected full branch-tip range and size exception; implementation risk is contained to retrieval-owned paths plus the approved shared test file.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 4 retrieval layer; active MVP focus for FTS-first retrieval.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable state/workflow.
- Canonical demo-path mapping:
  - `retrieve relevant material`: tasks 1, 2, and 3 keep FTS authoritative, deterministic, and promotion-ready for engine retrieval.
  - `promote or gather context into the basket`: task 4 makes retrieved evidence traceable through deterministic basket refs and policy-bound item fingerprints.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

Required gates for the corrected candidate, rerun on 2026-05-05 for this fixer pass:

- `python -m unittest tests.unit.test_unified_retrieval` PASS, 57 tests.
- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, smoke plus 126 unit tests.
- `./typecheck-test.sh` PASS, Python sources under `src/` compile.
- `make ci` PASS, includes scope-check, format, lint, typecheck, and 126 unit tests.
- `git merge-tree $(git merge-base codex/integrator HEAD) codex/integrator HEAD` PASS, clean textual merge with no conflict output.

Focused gate already run earlier in this branch:

- `python -m unittest tests.unit.test_unified_retrieval` PASS, 57 tests, after fixing the first focused fingerprint-helper failure.

## Risks/Blockers

No implementation blocker is known. The remaining reviewer-facing risks are the requested AGENTS.md size exception for the full high-risk branch-tip candidate and the protected `.codex` packet mirrors, which still cannot be edited from this lane worktree because writes fail with `Operation not permitted`. `THREAD_PACKET.md` is the corrected authoritative handoff packet for re-review.
