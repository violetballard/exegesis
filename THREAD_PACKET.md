## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Review target: final branch tip after this fixer commit.
- Pre-fix branch tip: `9a300194442dfc14d48dd3db053eadb7eebb7409`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..final fixer commit reported in response`
- Handoff type: high-risk retrieval re-review with retained FTS excerpt and basket-promotion runtime scope.

## Scope goal

Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt, provenance, and compact basket-promotion context output.

## Scope completed

This corrected handoff uses one review target: the actual branch tip. The retained runtime scope includes FTS-only excerpt lookup plus basket-promotion context bundles. `fetch_excerpt` now requires a canonical FTS lookup hit, PageIndex-only excerpt IDs fail closed under shared regression coverage, and PageIndex/embeddings remain compatibility-only deferred paths. Basket promotion adds deterministic `retrieval_basket_promotion` snapshots with stable IDs, fingerprints, citation status, query scope, intent, date range, and source-bundle fingerprints.

## Canonical demo-path step

- Step: `retrieve relevant material`
- Impact: excerpt retrieval is FTS-first/fail-closed, and retrieved context now exposes compact basket-promotion references for the next engine-side promotion step.

## Budget and ownership

- Risk: `HIGH`
- Task count: `4` of `4`
- Size accounting: computed from `378cf9a74a3658058079a32f186fcd254c4a4034..final fixer commit reported in response`; expected to remain within `<=8 files` and `<=300` net LOC after this metadata cleanup.
- Owned runtime paths touched: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Approved shared-by-approval edit: `tests/unit/test_unified_retrieval.py`
- Integrator-locked files touched: none

## Tasks completed

1. Made excerpt lookup FTS-first and fail-closed for PageIndex-only excerpt IDs, with shared regression coverage.
2. Added deterministic basket-promotion snapshots to retrieval context bundles, including stable promotion IDs, fingerprints, query scope, intent, date range, citation status, and source-bundle fingerprints.
3. Rehydrated basket-promotion context through engine retrieval payload helpers so downstream engine flows receive compact references from downstream payloads and source-bundle-only inputs.
4. Regenerated the handoff packet for the actual branch-tip merge candidate and reran all required gates against that candidate.

## Files changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Commands run and outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Roadmap item affected

- `ROADMAP.md`: Milestone 3 real workflow loop, specifically FTS-first retrieval evidence and context promotion for the canonical demo path.

## Vision capabilities affected

- `PRODUCT_VISION.md`: retrieval-first context handling.
- `PRODUCT_VISION.md`: auditable state and workflow through deterministic compact references.

## Routing/provider impact

None. This handoff does not touch model routing, provider configuration, or core provider entrypoints.

## Required fix reconciliation

1. The reviewed implementation range now ends at the actual branch tip instead of excluding post-`adfa8cd` runtime/test changes.
2. Basket-promotion runtime changes are retained and included in scope completed, tasks completed, files changed, roadmap mapping, vision mapping, risks, and tests.
3. High-risk budget accounting is recomputed from the actual reviewed range after this fixer commit; final shortstat is reported in the fixer response.
4. The stale metadata-only claim is removed for commits that changed runtime or test files.
5. Required gates are rerun against the corrected final review target in this fixer pass.

## Risks/blockers

- Risk: `HIGH`
- Blockers: none.
- Residual risk: basket-promotion snapshots are compact references only; expanded promotion behavior should be a separate high-risk handoff if it changes engine orchestration or public command contracts.
