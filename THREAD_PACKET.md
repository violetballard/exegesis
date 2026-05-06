## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk branch-tip retrieval handoff for the FTS-first retrieval lane.
- Reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`.
- Reviewed implementation head: `HEAD` after this fixer commit; final SHA is reported in the fixer response.
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`.
- Scope classification: high-risk because this lane touches retrieval core/facade behavior and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.

## Scope Completed

This branch-tip handoff covers the full retrieval implementation currently present on `codex/feat-retrieval-fts`, including all production and test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`. SQLite FTS remains the authoritative retrieval path for MVP flows. PageIndex and embeddings remain compatibility-only/deferred surfaces that fail closed when they cannot be resolved through the canonical FTS path.

The branch hardens deterministic retrieval payloads, FTS candidate strategy identity, sparse-policy rehydration, sparse candidate-resolution rehydration, excerpt lookup provenance, bundle identity validation, final hit rank/score ordering, basket-promotion strategy aliases, basket-promotion match evidence, basket-promotion query-constraint snapshots, sparse basket-promotion query-context rehydration, direct excerpt lookup promotion-source markers, normalized query-constraint evidence/citation/provenance snapshots, and citation strategy aliases. Doc/excerpt hit provenance records `retrieval_source_strategy: fts` at provenance creation time, result-derived citation snapshots and basket promotion refs read that canonical alias directly while preserving the existing `source_strategy: fts` fallback, and direct FTS excerpt lookups expose `basket_promotion_source: fts_excerpt_lookup` on the canonical payload, provenance, promotion item, and compact audit event. Retrieval evidence, citation bundles, bundle context, provenance, and promoted basket refs also carry or rehydrate the canonical query constraint snapshot directly so basket, revise, and apply consumers can audit retrieval limits and filters without reconstructing them from the source query object. This fixer pass additionally surfaces the selected top excerpt's matched terms and match count on doc-hit snapshots so downstream basket/revise consumers can audit document selection evidence without digging into nested provenance.

Canonical demo-path step advanced: `retrieve relevant material`. This work makes that step more real by making FTS retrieval and excerpt lookup deterministic, provenance-backed, query-constraint-aware, and fail-closed for PageIndex-only IDs. It also supports later `promote or gather context into the basket` by keeping excerpt provenance, citation snapshots, matched-term evidence, and basket promotion metadata deterministic.

Canonical demo-path step advanced: retrieve relevant material, with deterministic excerpt/provenance output suitable for basket promotion.

## Tasks Completed

1. Canonical demo-path step advanced: `retrieve relevant material`. FTS-first retrieval and excerpt lookup: kept SQLite FTS authoritative, exported the canonical retrieval facades, removed PageIndex fallback from excerpt fetching, and enforced fail-closed behavior for PageIndex-only or non-FTS excerpt identifiers.
2. Canonical demo-path step advanced: `retrieve relevant material`; supports `promote or gather context into the basket`. Deterministic retrieval payloads and provenance: normalized query snapshots, constraints, query-constraint evidence/citation/provenance/basket-promotion snapshots, sparse basket-promotion query-context rehydration, candidate/document identities, candidate-resolution snapshots, source bundles, context bundles, citation backfills, lookup fingerprints, excerpt lookup audit hashes and promotion-source audit metadata, canonical provenance-level `retrieval_source_strategy` aliases, and basket promotion metadata, including direct excerpt lookup `basket_promotion_source` plus `matched_terms`/`match_count` evidence on result promotion refs and doc-hit top-excerpt snapshots.
3. Canonical demo-path step advanced: `retrieve relevant material`. Retrieval policy and strategy hardening: preserved sparse retrieval policy identity, guarded deferred backend policy, validated bundle identity, stabilized FTS merge strategy identity, and kept engine retrieval exports aligned with the canonical retrieval implementation.
4. Canonical demo-path step advanced: `retrieve relevant material`; validates readiness for `promote or gather context into the basket`. Final result ordering and regression coverage: re-ranked final deduplicated FTS hits after truncation so score/provenance rank match output order, and expanded approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for FTS-only behavior, payload identity, provenance, citation strategy aliases, and promotion-ready outputs.

## Files Changed

Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`.

- `.codex/kickoff_packets/feat-retrieval-fts.md` - lane kickoff metadata refreshed by earlier packet commits; root `THREAD_PACKET.md` is the authoritative packet for branch-tip re-review.
- `.codex/lane_meta/feat-retrieval-fts.json` - lane metadata refreshed by earlier packet commits; root `THREAD_PACKET.md` supersedes stale narrow-range wording.
- `THREAD_PACKET.md` - authoritative handoff packet regenerated for the actual branch-tip implementation scope through this fixer commit.
- `src/qual/engine/retrieval/__init__.py` - aligned engine retrieval exports and compatibility facade wiring with the FTS-first retrieval surface.
- `src/qual/engine/retrieval/fts_strategy.py` - hardened FTS strategy identity and candidate/provenance behavior.
- `src/qual/engine/retrieval/payload.py` - normalized retrieval payload snapshots, source/context bundles, query-constraint citation/provenance rehydration, sparse basket-promotion query-context rehydration, citation backfills, candidate-resolution rehydration, basket promotion metadata and fingerprints, FTS strategy aliases, matched-term promotion fingerprints, and identifier/fingerprint fields.
- `src/qual/retrieval/__init__.py` - exported canonical retrieval helpers through the public retrieval facade.
- `src/qual/retrieval/service.py` - implemented FTS-only excerpt fetching, deterministic query/constraint/cache handling, sparse policy reconstruction, final hit re-ranking, explicit FTS strategy aliases, provenance-level `retrieval_source_strategy` aliases, direct excerpt lookup promotion-source metadata, normalized query-constraint snapshots in retrieval evidence/citation/provenance bundles and basket promotion refs, matched-term evidence for basket promotion items and doc-hit top-excerpt snapshots, canonical `excerpt_text_hash` audit recording, and `basket_promotion_source` audit recording for excerpt lookups.
- `tests/unit/test_unified_retrieval.py` - expanded approved shared regression coverage for FTS-first retrieval, fail-closed fallback behavior, payload/provenance normalization, query-constraint citation bundle normalization, basket-promotion query-constraint snapshots, sparse basket-promotion query-context rehydration, candidate-resolution rehydration, branch-tip hardening, direct excerpt lookup promotion-source metadata, matched-term basket promotion evidence, doc-hit top-excerpt matched-term snapshots, citation strategy aliases, canonical excerpt lookup audit identity, and promotion-source audit metadata.


## Reviewer Required Fixes Addressed

Latest metadata-only reviewer fixes:

1. Updated each completed task so it explicitly names the canonical demo-path step it advances.
2. Added the final canonical demo-path sentence required by the reviewer: `Canonical demo-path step advanced: retrieve relevant material, with deterministic excerpt/provenance output suitable for basket promotion.`
3. This packet is ready for reviewer packet refresh after the metadata-only handoff fix.

Prior reviewer traceability fixes:

1. Regenerated the authoritative handoff packet so the reviewed implementation range is the branch-tip range `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`, covering all non-metadata code intended for merge.
2. Updated `Files Changed`, `Scope Completed`, and `Tasks Completed` to cover the actual branch-tip changes in `src/qual/engine/retrieval/**`, `src/qual/retrieval/**`, and `tests/unit/test_unified_retrieval.py`.
3. Re-evaluated AGENTS budget compliance against the corrected branch-tip range: `4/4` high-risk task groups, `9` files changed, and net `3621` LOC. The range exceeds high-risk file/size limits and still needs integrator acceptance or an explicit split plan before merge.
4. Re-ran the required gates on the corrected branch-tip content; outcomes are listed under `Commands Run`.
5. Kept the intended review target as the branch tip rather than moving the branch back to `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Traceability Corrections

- The reviewed implementation range is `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`; it includes all production/test changes present at the branch tip.
- `2ef3ec843860980ec7ab89ac769e5a37aaf0440f` is an implementation commit, not a metadata-only finalization commit.
- `2ef3ec843860980ec7ab89ac769e5a37aaf0440f` subject: `fix(retrieval): expose query constraints in evidence`.
- `2ef3ec843860980ec7ab89ac769e5a37aaf0440f` files changed: `THREAD_PACKET.md`, `src/qual/retrieval/service.py`.
- `2ef3ec843860980ec7ab89ac769e5a37aaf0440f` size: `2 files changed, 37 insertions(+), 30 deletions(-)`.
- Commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` that modify `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, or `tests/unit/test_unified_retrieval.py` are implementation commits and are inside the reviewed branch-tip range.
- This packet does not describe any production/test commit after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as metadata-only.

## Diff Evidence

Command: `git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 ++-
 THREAD_PACKET.md                             |  210 ++--
 src/qual/engine/retrieval/__init__.py        |   86 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1576 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  977 ++++++++++++++--
 tests/unit/test_unified_retrieval.py         | 1415 ++++++++++++++++++++++-
 9 files changed, 4073 insertions(+), 452 deletions(-)
```

Command: `git diff --name-status 378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`

```text
M	.codex/kickoff_packets/feat-retrieval-fts.md
M	.codex/lane_meta/feat-retrieval-fts.json
M	THREAD_PACKET.md
M	src/qual/engine/retrieval/__init__.py
M	src/qual/engine/retrieval/fts_strategy.py
M	src/qual/engine/retrieval/payload.py
M	src/qual/retrieval/__init__.py
M	src/qual/retrieval/service.py
M	tests/unit/test_unified_retrieval.py
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for reviewed implementation handoff: `9 files changed`.
- Size accounting for reviewed implementation handoff: `4073 insertions(+), 452 deletions(-)`, net `3621 LOC`.
- AGENTS file/size status: exceeds high-risk size limits of `<=8 files` and `<=300 net LOC`.
- Budget exception status: the worktree contains an approved shared-file exception for `tests/unit/test_unified_retrieval.py`; no explicit integrator-approved exception for the high-risk file/LOC overage is present in the writable worktree evidence. This packet discloses the overage for reviewer/integrator decision instead of hiding it behind metadata-only wording.
- Scope split status: not performed in this fixer pass because narrowing the branch to `<=300` net LOC would require removing already-reviewed retrieval implementation behavior rather than correcting packet traceability. If the integrator does not grant a size exception, this branch needs an explicit split plan before merge.
- Shared/integrator exception status: `tests/unit/test_unified_retrieval.py` is approved shared regression coverage for the retrieval lane; no integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only/deferred identifiers; no PageIndex, embeddings, hybrid, or alternate retrieval path was added.
- Remaining risks/blockers: the cumulative reviewed implementation change volume exceeds AGENTS high-risk size limits and still requires integrator acceptance or split before merge.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

Commands re-run for this corrected branch-tip packet on the exact worktree state committed by this fixer pass:

- `./quality-test.sh tests/unit/test_unified_retrieval.py` - passed smoke tests and 152 unit tests.
- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 152 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 152 unit tests.

## Metadata Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this fixer pass. The reviewed implementation range intentionally covers `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` so all production and test changes present at the branch tip are traceable. The protected `.codex` metadata files are listed in the actual changed files for the range, but this root packet supersedes stale narrow-range wording in those metadata files. During this fixer pass the local OS denied writes under `.codex` with `PermissionError: [Errno 1] Operation not permitted`, so stale `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` wording is explicitly non-authoritative for re-review.
