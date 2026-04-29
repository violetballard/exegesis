# Thread Handoff Packet

- Branch: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Review target: final fixer commit reported in the fixer response.
- Pre-fix branch tip: `ba2f81e91f6d2fd05a0c8a6cd0d803c0d016e4f3`
- Actual merge candidate: final fixer commit reported in the fixer response.
- Reviewed range: `378cf9a74a3658058079a32f186fcd254c4a4034..final fixer commit reported in response`
- `a28ccf520ea0983f538106f1bd418670d9cea73b` scope: not metadata-only; it changed shared regression tests and packet text, and its retained effects are accounted for or reverted in the final reviewed range.
- `ba2f81e91f6d2fd05a0c8a6cd0d803c0d016e4f3` scope: the pre-fix branch tip whose retained effects are accounted for or reverted by the final fixer commit.
- Handoff type: high-risk retrieval fixer re-review.

## Scope completed

This handoff is narrowed back to the reviewed FTS-only excerpt fix against the actual branch state. Post-`adfa8cda` runtime/test changes in `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py` are removed from the final merge candidate, so later basket-promotion runtime work is not submitted as metadata-only.

The branch history includes basket-promotion provenance/fingerprint commits after `adfa8cda`, including `a28ccf520ea0983f538106f1bd418670d9cea73b`; those commits are not described as metadata-only here. The final reviewed diff range above is the authoritative merge candidate and does not retain basket-promotion runtime behavior.

The remaining implementation makes excerpt lookup FTS-first and fail-closed for PageIndex-only excerpt IDs, with shared regression coverage. PageIndex and embeddings stay compatibility-only/deferred paths and are not required runtime paths for the canonical retrieval flow.

## Canonical demo-path step

- Step: `retrieve relevant material`
- Impact: excerpt retrieval now requires an FTS lookup hit, preserving the MVP retrieval contract.

## Budget and ownership

- Risk: `HIGH`
- Task count: `1` of `4`
- Actual merge-candidate size before final commit: `5 files changed, 264 insertions(+), 114 deletions(-)` for `378cf9a74a3658058079a32f186fcd254c4a4034..working tree`; net LOC `+150`.
- Budget result: within high-risk limits (`<=8 files`, `<=300 net LOC`).
- Owned runtime paths touched: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Approved shared-by-approval edit: `tests/unit/test_unified_retrieval.py`
- Integrator-locked files touched: none

## Tasks completed

1. Made excerpt lookup FTS-first and fail-closed for PageIndex-only excerpt IDs, with shared regression coverage.

## Files changed

```text
.codex/kickoff_packets/feat-retrieval-fts.md
.codex/lane_meta/feat-retrieval-fts.json
THREAD_PACKET.md
src/qual/retrieval/service.py
tests/unit/test_unified_retrieval.py
```

`src/qual/engine/retrieval/payload.py` had post-`adfa8cda` basket-promotion drift on the pre-fix branch tip, but its retained changes are removed from the final reviewed range from `378cf9a`.

`.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain in the actual diff because this sandbox cannot rewrite those Box-backed packet mirrors (`Operation not permitted`). They are included in accounting above.

## Commands run

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS (`124` unit tests plus smoke).
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.

## Roadmap items affected

- `ROADMAP.md`: MVP focus on `feat-retrieval-fts`.
- `ROADMAP.md`: Milestone 3 product readiness item for retrieval evidence in the real workflow loop.

## Vision capabilities affected

- `PRODUCT_VISION.md`: retrieval-backed context, FTS-first for the current MVP.
- `PRODUCT_VISION.md`: auditable state and workflow.

## Routing/provider impact

None. This handoff does not touch model routing, provider configuration, or core provider entrypoints.

## Metadata-only claim correction

The previous metadata-only claim for `a28ccf520ea0983f538106f1bd418670d9cea73b` was false. That commit changed `tests/unit/test_unified_retrieval.py` as well as `THREAD_PACKET.md`. This fixer does not rely on that claim: `a28ccf5` and the previous branch tip `ba2f81e9` are treated as part of the pre-fix branch history, and the final reviewed range above is the authoritative merge candidate after the source/test narrowing.

## Risks/blockers

- Later basket-promotion provenance/fingerprint runtime work is intentionally excluded and needs a separate high-risk handoff if still wanted.
- Box-backed packet mirrors could not be edited in this sandbox, so `THREAD_PACKET.md` is the authoritative corrected handoff packet.
