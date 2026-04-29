## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip `HEAD`, including this packet-regeneration fixer commit.
- Branch-tip SHA: reported in the final fixer response after commit creation.
- Reviewed range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`
- Reviewer trace anchor being corrected: `f137cfd00db49bb99790a5c6e82bd919a560a330`
- Handoff classification: high-risk/shared because the merge candidate includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`.

## Required Fixes Addressed

1. The handoff is regenerated against the actual branch-tip merge candidate. It no longer asks review to stop at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, and it no longer labels branch-tip source/test changes as metadata-only.
2. The reviewed range is the full branch-tip merge-candidate range `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`, which includes the post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval context-promotion implementation.
3. Scope, task list, files changed, line-count budget, high-risk/shared status, and gate evidence are reported for the actual merge candidate.
4. Required gates are rerun on the corrected branch tip and reported below.

## Scope Completed

The branch delivers the cumulative Milestone 3 FTS-first retrieval slice for the MVP. SQLite FTS is the authoritative retrieval and excerpt lookup path; PageIndex and embeddings remain compatibility/fallback surfaces rather than required paths. Retrieval query construction, payload normalization, provenance bundles, citation bundles, source bundles, excerpt bundles, cache snapshots, and downstream context bundles are deterministic for engine orchestration.

The actual merge candidate also carries basket-promotion context through the retrieval flow. `retrieval_context_refs` and citation refs are derived from FTS hits and preserved through source bundles, downstream payloads, sparse bundle reconstruction, and nested payload normalization. These refs include excerpt IDs, source strategy, FTS provenance, query/result fingerprints, span data, matched-term metadata, stable context-ref fingerprints, and citation identifiers.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: make SQLite FTS the canonical retrieval and excerpt lookup path, keep PageIndex/embeddings fallback-only, guard scoped query handling, and preserve compatibility exports.
2. Canonical demo-path step `retrieve relevant material`: normalize retrieval queries, constraints, date ranges, cache keys, ranked IDs, hit snapshots, policy metadata, citation fields, provenance bundles, and source/context/excerpt bundles.
3. Canonical demo-path step `promote or gather context into the basket`: provide stable `retrieval_context_refs`, citation refs, context-ref fingerprints, source bundle aliases, sparse bundle rehydration, nested context-ref extraction, and downstream helper backfills.
4. Canonical demo-path steps `retrieve relevant material` and `promote or gather context into the basket`: add approved shared regression coverage and refresh branch-tip handoff metadata for the actual merge candidate.

## Files Changed

Reviewed merge-candidate range `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Implementation files in that range:

- `src/qual/retrieval/service.py`: adds promotion-ready `retrieval_context_refs` and citation refs to retrieval results, source bundles, downstream payloads, and context bundles; keeps `fetch_excerpt` on the FTS-first path.
- `src/qual/engine/retrieval/payload.py`: preserves and rehydrates `retrieval_context_refs` from top-level and nested source/doc/excerpt/context snapshots.
- `tests/unit/test_unified_retrieval.py`: verifies FTS-only excerpt lookup, rejection of PageIndex-only excerpt IDs, context-ref fields/fingerprints, citation ref propagation, defensive copies, and sparse payload rehydration.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`.
- File budget: `6/8`.
- Size accounting for `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` is recomputed after this metadata refresh and reported in the final fixer response; the pre-refresh range was `6 files changed, 397 insertions(+), 87 deletions(-)`, net `310` LOC.
- This fixer commit changes editable packet metadata only and does not change retrieval implementation behavior.
- Integrator-locked files: none.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py`, used only for canonical retrieval regression coverage.
- Routing/provider impact: none. This branch does not change model routing, provider configuration, provider compatibility behavior, CLI entrypoints, or app entrypoints.

## FTS-First Alignment

`src/qual/retrieval/service.py` keeps SQLite FTS authoritative for retrieval and excerpt lookup. PageIndex-only excerpt IDs fail closed with `KeyError`, and regression tests cover that behavior. Context refs and citation refs are derived from FTS hits and retain FTS provenance so downstream basket/workflow consumers can audit retrieved source material.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 3 real workflow loop: retrieval supplies workflow-ready source context before drafting or diff generation.
- Roadmap item affected: `ROADMAP.md` Milestone 4 retrieval layer: FTS-first retrieval, source attribution for retrieved chunks, and PageIndex/embeddings deferred until after the demo push.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation.
- Canonical demo-path step made more real by context promotion: `promote or gather context into the basket`.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh fixer pass on `2026-04-29` for the actual branch-tip merge candidate:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS.
- `./typecheck-test.sh` PASS.
- `make ci` PASS.

## Risks / Blockers

- No implementation blockers are known.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain stale packet text but are not writable in this sandbox: `test -w` reports not writable, `apply_patch` rejects edits under those paths, and removing `com.apple.provenance` fails with `Operation not permitted`.
- Re-review should use this `THREAD_PACKET.md`, `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` as the reviewed merge-candidate range, and the final HEAD SHA reported by this fixer as the branch tip.
