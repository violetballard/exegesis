# Thread Handoff Packet

- Branch: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Review target: final fixer commit reported in the fixer response.
- Pre-fix branch tip: `0e934aa2f1743d360e3f0f5f97ff48731785f98f`
- Actual merge candidate: final fixer commit reported in the fixer response.
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..final fixer commit reported in response`
- Handoff type: high-risk retrieval fixer re-review with retained basket-promotion runtime scope.

## Scope completed

This handoff includes the actual branch-tip retrieval runtime changes: FTS-only excerpt lookup plus basket-promotion context bundles.
`fetch_excerpt` now uses the canonical FTS lookup path, PageIndex-only excerpt IDs fail closed under shared regression coverage, and PageIndex/embeddings remain compatibility-only deferred paths. Basket promotion adds a compact deterministic `retrieval_basket_promotion` snapshot with stable IDs, fingerprints, citation status, query scope/intent/date range, and source-bundle fingerprint.

## Canonical demo-path step

- Step: `retrieve relevant material`
- Impact: excerpt retrieval now requires an FTS lookup hit, while retrieved context exposes stable basket-promotion references for the next engine-side promotion step.

## Budget and ownership

- Risk: `HIGH`
- Task count: `2` of `4`
- Actual merge-candidate size after final commit: `6 files changed, 406 insertions(+), 113 deletions(-)` for `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`; net LOC `+293`.
- Budget result: within high-risk limits (`<=8 files`, `<=300 net LOC`).
- Owned runtime paths touched: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Approved shared-by-approval edit: `tests/unit/test_unified_retrieval.py`
- Integrator-locked files touched: none

## Tasks completed

1. Made excerpt lookup FTS-first and fail-closed for PageIndex-only excerpt IDs, with shared regression coverage.
2. Added deterministic basket-promotion snapshots to retrieval context bundles and engine payload rehydration, including stable promotion fingerprints and query/context reference fields.

## Files changed

```text
.codex/kickoff_packets/feat-retrieval-fts.md
.codex/lane_meta/feat-retrieval-fts.json
THREAD_PACKET.md
src/qual/engine/retrieval/payload.py
src/qual/retrieval/service.py
tests/unit/test_unified_retrieval.py
```

The Box-backed `.codex` packet mirrors remain changed in the cumulative reviewed range but rejected writes from this sandbox during this fixer pass, so `THREAD_PACKET.md` is the authoritative corrected handoff packet.

## Commands run

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.

## Roadmap items affected

- `ROADMAP.md`: MVP focus on `feat-retrieval-fts`.
- `ROADMAP.md`: Milestone 3 retrieval evidence and context promotion for the real workflow loop.

## Vision capabilities affected

- `PRODUCT_VISION.md`: retrieval-backed context and durable context promotion using compact references.
- `PRODUCT_VISION.md`: auditable state and workflow.

## Routing/provider impact

None. This handoff does not touch model routing, provider configuration, or core provider entrypoints.

## Required Fix Reconciliation

1. The reviewed implementation range now matches the actual merge candidate: `378cf9a74a3658058079a32f186fcd254c4a4034..final fixer commit reported in response`.
2. Basket-promotion runtime changes are retained and included in scope completed, tasks completed, files changed, roadmap mapping, and vision mapping.
3. `src/qual/engine/retrieval/payload.py` is included in reviewed implementation files.
4. Required gates are rerun against the corrected final branch tip in this fixer pass.
5. High-risk budget accounting includes the approved shared test exception and true changed-file/net-LOC counts.

## Risks/blockers

- Basket-promotion snapshots are intentionally compact references. Further promotion behavior should be implemented in a separate high-risk handoff if it expands engine orchestration or public command contracts.
