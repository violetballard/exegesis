## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Actual merge candidate: current branch tip `HEAD`.
- Pre-fix branch tip reviewed by this packet: `af726ee0798cb210973489343693ba36be020429`.
- Reviewed branch-tip range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`.
- Post-`adfa8cda` implementation range included: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD`.
- Final HEAD SHA: reported in the fixer handoff after the metadata commit is created.
- Handoff classification: high-risk/shared because the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Canonical demo-path steps advanced: `retrieve relevant material` and `promote/gather context into the basket`.

## Required Fixes Addressed

1. This packet is regenerated against the actual merge candidate at branch tip. It no longer claims that the branch ends at `adfa8cdadd43747ffbcb612e4151e262b13e52ca` or that commits after that point are metadata-only.
2. The reviewed range includes all implementation commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, including retrieval payload, retrieval service, and shared regression test changes.
3. Scope, files changed, task count, risk, and gate evidence are stated for the actual branch-tip merge candidate.
4. Each completed task below names the canonical demo-path step it advances.

## Scope Completed

The branch delivers the cumulative Milestone 3 FTS-first retrieval slice for the MVP. SQLite FTS is the canonical retrieval and excerpt lookup path; PageIndex and embeddings remain compatibility/fallback surfaces rather than required paths. Retrieval query construction, payload normalization, provenance bundles, citation bundles, source bundles, excerpt bundles, cache snapshots, and downstream context bundles are deterministic for engine orchestration.

The post-`adfa8cda` implementation commits are included in this handoff. They carry basket-promotion context through the retrieval flow: `retrieval_context_refs` and citation refs are derived from FTS hits and preserved through source bundles, downstream payloads, sparse bundle reconstruction, and nested payload normalization. These refs include excerpt IDs, source strategy, FTS provenance, query/result fingerprints, span data, matched-term metadata, stable context-ref fingerprints, and citation identifiers.

## Tasks Completed

1. FTS-first retrieval contract. Canonical demo-path step: `retrieve relevant material`. SQLite FTS remains authoritative for retrieval and excerpt lookup, scoped queries fail closed, and PageIndex/embedding behavior stays fallback-only.
2. Deterministic retrieval payloads. Canonical demo-path step: `retrieve relevant material`. Queries, constraints, date ranges, cache keys, ranked IDs, hit snapshots, policy metadata, citation fields, provenance bundles, and source/context/excerpt bundles are normalized for repeatable engine use.
3. Basket promotion readiness. Canonical demo-path step: `promote/gather context into the basket`. Stable `retrieval_context_refs`, citation refs, context-ref fingerprints, source bundle aliases, sparse bundle rehydration, nested context-ref extraction, and downstream helper backfills preserve auditable promotion context.
4. Regression and packet coverage. Canonical demo-path steps: `retrieve relevant material` and `promote/gather context into the basket`. Shared canonical retrieval tests cover FTS-only excerpt lookup, citation/context ref propagation, defensive copies, and sparse payload rehydration; this packet records the branch-tip merge candidate truthfully.

## Files Changed

Reviewed branch-tip range `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Implementation files in the actual merge candidate:

- `src/qual/retrieval/service.py`: keeps FTS authoritative for retrieval and excerpt lookup; adds promotion-ready `retrieval_context_refs` and citation refs to retrieval results, source bundles, downstream payloads, and context bundles.
- `src/qual/engine/retrieval/payload.py`: preserves and rehydrates `retrieval_context_refs` from top-level and nested source/doc/excerpt/context snapshots.
- `tests/unit/test_unified_retrieval.py`: verifies FTS-only excerpt lookup, rejection of PageIndex-only excerpt IDs, context-ref fields/fingerprints, citation ref propagation, defensive copies, and sparse payload rehydration.

Post-`adfa8cda` implementation files explicitly included:

- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`.
- File budget: `6/8`.
- Size budget for `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` before this fixer commit: `6 files changed, 413 insertions(+), 118 deletions(-)`, net `295` LOC, within the high-risk `<=300` net LOC cap.
- Post-`adfa8cda` branch-tip delta before this fixer commit: `6 files changed, 385 insertions(+), 87 deletions(-)`, net `298` LOC, within the high-risk `<=300` net LOC cap.
- Integrator-locked files: none.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py`, used only for canonical retrieval regression coverage.
- Routing/provider impact: none. This branch does not change model routing, provider configuration, provider compatibility behavior, CLI entrypoints, or app entrypoints.

## FTS-First Alignment

`src/qual/retrieval/service.py` keeps SQLite FTS authoritative for retrieval and excerpt lookup. PageIndex-only excerpt IDs fail closed with `KeyError`, and regression tests cover that behavior. Context refs and citation refs are derived from FTS hits and retain FTS provenance so downstream basket/workflow consumers can audit retrieved source material.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 3: Real workflow loop, specifically FTS-first retrieval that can feed basket/workflow-ready context.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling: generation consumes retrieved chunks, SQLite FTS remains the MVP retrieval path, and PageIndex/embeddings are deferred.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation: retrieved sources carry deterministic provenance, citations, fingerprints, and promotion references.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh fixer pass on `2026-04-29`:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS (`124` tests).
- `./typecheck-test.sh` PASS.
- `make ci` PASS (`124` tests).

Gate verification note: this fixer pass re-ran the required gates against the actual branch-tip merge candidate after regenerating the packet to include post-`adfa8cda` implementation scope.

## Risks / Blockers

- No blockers remain in the packet metadata.
- The final fixer commit is metadata-only and keeps the reviewed branch-tip range as `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`; the final concrete HEAD SHA is reported in the fixer handoff.
