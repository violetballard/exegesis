## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..cc084f05c9cd4bfb6207c49f5dd275e3ac49489a`
- Reviewed implementation head: `cc084f05c9cd4bfb6207c49f5dd275e3ac49489a`
- Final branch tip: reported in the fixer deliverable after this packet commit is created.
- Scope classification: high-risk because this branch-tip packet includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Packet type: branch-tip re-review packet for the FTS-first retrieval lane.

## Scope Completed

This packet has been regenerated for the actual branch-tip implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..cc084f05c9cd4bfb6207c49f5dd275e3ac49489a`.

The reviewed branch-tip work strengthens the active MVP target of FTS-first retrieval. SQLite FTS remains the canonical retrieval path; engine and service facades expose canonical query construction, `retrieve_auto`, and excerpt lookup; retrieval payload snapshots, sparse source/context bundles, provenance, fingerprints, and basket-promotion references are normalized deterministically for downstream engine flows; and PageIndex-only excerpt IDs fail closed instead of backfilling through non-FTS paths.

Canonical demo-path step advanced: this makes `retrieve relevant material` more real by ensuring the demo path gathers relevant material through the canonical FTS-first retrieval surface with stable provenance, excerpt lookup, and context-promotion metadata. Basket promotion/gathering is represented only as retrieval-owned payload/context metadata in this branch-tip packet; Textual console work remains out of scope.

## Tasks Completed

1. Exported the canonical FTS retrieval surface through the service and engine facades, including query construction, `retrieve_auto`, excerpt lookup, rank fields, and query type exports.
2. Hardened deterministic retrieval payloads by normalizing query snapshots, constraints, dates, booleans, sparse source/context bundles, citation backfills, provenance fingerprints, and copy-safe snapshot reconstruction.
3. Kept retrieval FTS-first by tightening cache scope invalidation, candidate document handling, section/date/confidentiality filtering, FTS-only excerpt resolution, and fail-closed PageIndex/embedding compatibility behavior.
4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for facade exports, normalized payload snapshots, source/context bundle rehydration, citation/provenance helpers, basket-promotion/context references, cache behavior, and FTS-only excerpt lookup.

## Canonical Demo Path

- Primary canonical demo-path step advanced: `retrieve relevant material`.
- AGENTS.md narrowing language: this work targets the active MVP note for `FTS-first retrieval`.
- Basket promotion/gathering: limited to retrieval-owned payload/context metadata that supports later engine/demo gathering; no `feat-console` work is included.

## Files Changed

Reviewed implementation files for `378cf9a74a3658058079a32f186fcd254c4a4034..cc084f05c9cd4bfb6207c49f5dd275e3ac49489a`:

- `src/qual/engine/retrieval/__init__.py` - engine retrieval facade exports for canonical query, auto retrieval, excerpt lookup, payload, and ranking surfaces.
- `src/qual/engine/retrieval/fts_strategy.py` - FTS strategy snapshot normalization and deterministic hit/ranking behavior.
- `src/qual/engine/retrieval/payload.py` - deterministic payload, provenance, sparse bundle, citation, fingerprint, and basket-promotion/context reference helpers.
- `src/qual/retrieval/service.py` - canonical FTS-first retrieval service behavior, excerpt lookup, cache scope normalization, filtering, and fail-closed compatibility paths.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the branch-tip retrieval contract.

Reviewed source/test stat: `5 files changed, 492 insertions(+), 119 deletions(-)`.

Full reviewed packet stat, including packet metadata files: `8 files changed, 739 insertions(+), 210 deletions(-)`.

Lane-owned source/test files in the reviewed implementation range:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`

Shared-by-approval files in the reviewed implementation range:

- `tests/unit/test_unified_retrieval.py`

Integrator-locked files in the reviewed implementation range:

- None.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `5/8` high-risk source/test files.
- Net source/test LOC budget: `+373` net LOC, above the default `<=300` high-risk size guideline because this packet now truthfully covers all branch-tip retrieval implementation work requested by the reviewer.
- Size exception required: yes; this branch-tip re-review packet corrects prior traceability drift instead of narrowing away source/test changes that are already present on the branch tip.
- Shared-file approval note: Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it exercises the canonical retrieval contract.
- Routing/provider impact: none.
- PageIndex/embeddings impact: PageIndex and embeddings remain compatibility-only fallback shims; PageIndex-only excerpt IDs fail closed for the canonical excerpt lookup path.
- Merge risk: high because the corrected packet now exposes all branch-tip retrieval source/test changes for re-review.

## Roadmap/Vision

- Roadmap items affected: MVP focus for FTS-first retrieval.
- Vision capabilities affected: Retrieval-first context handling; auditable state and workflow.
- Proposed `README.md` patch text: none.

## Commands Run

Required gates for this fixer pass:

- `make scope-check` PASS for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 125 tests.
- `./typecheck-test.sh` PASS, Python sources under `src/` compile.
- `make ci` PASS, 125 tests; includes scope-check, format, lint, typecheck, and test gates.

## Risks/Blockers

Remaining risk is review scope size: this corrected packet intentionally includes every branch-tip source/test change through `cc084f05c9cd4bfb6207c49f5dd275e3ac49489a`. It does not touch model routing/provider configuration and does not include Textual UI console work.
