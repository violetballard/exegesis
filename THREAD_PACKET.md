## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Final branch tip: reported in the fixer deliverable after this packet commit is created.
- Scope classification: high-risk because this narrowed packet includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Packet type: narrowed re-review packet for the FTS-only excerpt lookup change.

## Scope Completed

This packet is intentionally narrowed to the implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

The reviewed change makes excerpt lookup use the canonical SQLite FTS path only. `fetch_excerpt()` resolves excerpt IDs through FTS-backed retrieval provenance and fails closed for PageIndex-only IDs. The regression coverage in `tests/unit/test_unified_retrieval.py` verifies that canonical FTS excerpt IDs still resolve and PageIndex-only excerpt IDs do not backfill through non-FTS paths.

This packet does not ask review to approve unrelated cumulative branch claims about facade exports, deterministic retrieval payload snapshots, sparse bundle rehydration, cache isolation, or compatibility shim behavior. Those topics are outside this narrowed review scope.

Canonical demo-path step advanced: this makes `retrieve relevant material` more real by ensuring excerpt lookup resolves only canonical FTS provenance and fails closed for PageIndex-only IDs.

## Tasks Completed

1. Updated `src/qual/retrieval/service.py` so excerpt lookup is FTS-only and no longer falls back through PageIndex-only excerpt normalization.
2. Updated `tests/unit/test_unified_retrieval.py` with approved shared regression coverage for canonical FTS excerpt lookup and fail-closed PageIndex-only IDs.

## Canonical Demo Path

- Primary canonical demo-path step advanced: `retrieve relevant material`.
- Basket promotion/gathering: not part of this narrowed review packet.

## Files Changed

Reviewed implementation files for `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:

- `src/qual/retrieval/service.py` - lane-owned retrieval service change for FTS-only excerpt lookup.
- `tests/unit/test_unified_retrieval.py` - shared-by-approval regression coverage for the canonical retrieval contract.

Reviewed implementation stat: `2 files changed, 28 insertions(+), 31 deletions(-)`, net `-3` LOC.

Lane-owned source/test files in the reviewed implementation range:

- `src/qual/retrieval/service.py`

Shared-by-approval files in the reviewed implementation range:

- `tests/unit/test_unified_retrieval.py`

Integrator-locked files in the reviewed implementation range:

- None.

## Budget/Risk

- Task budget: `2/4` high-risk tasks.
- File budget: `2/8` high-risk files.
- Net LOC budget: `-3` net LOC, within the `<=300` high-risk limit.
- Size exception required: no for this narrowed packet.
- Shared-file approval note: Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for this narrowed packet and exercises the canonical retrieval contract.
- Routing/provider impact: none.
- PageIndex/embeddings impact: PageIndex-only excerpt IDs now fail closed for this lookup path; embeddings are not involved.
- Merge risk: limited to the narrowed FTS excerpt lookup behavior and shared regression coverage described above.

## Roadmap/Vision

- Roadmap items affected: MVP focus for FTS-first retrieval.
- Vision capabilities affected: Retrieval-first context handling.
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

Remaining risk is limited to review risk around the approved shared test file. This packet does not widen retrieval strategy scope, does not make PageIndex or embeddings required paths, does not touch model routing/provider configuration, and does not include Textual UI console work.
