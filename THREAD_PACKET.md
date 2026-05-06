## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this finalization includes the approved shared-by-approval retrieval regression file `tests/unit/test_unified_retrieval.py`.
- Current base before this finalization: `c787c4476d855f7b6ffce750e69e9a3a00a8a3b7`
- Final branch tip: reported in the final fixer handoff after commit creation.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this finalization.

## Scope Completed

This finalization fixes sparse downstream provenance rehydration so `primary_excerpt_lookup_fingerprint` is restored from excerpt citations even when `primary_excerpt_id` survived payload pruning. That keeps the FTS-first basket promotion handle deterministic for downstream revise, patch, and apply flows that rebuild provenance from partial payload snapshots.

Canonical demo-path step advanced: `retrieve relevant material` for basket/workflow promotion. The change preserves the FTS-only retrieval path and narrows the engine-facing payload contract around auditable primary excerpt lookup provenance for downstream basket, revise, patch, and apply flows.

## Tasks Completed

1. Updated sparse retrieval provenance rebuild logic to backfill missing primary excerpt fingerprint fields independently of `primary_excerpt_id`.
2. Added approved shared regression coverage for the sparse case where `primary_excerpt_id` survives but `primary_excerpt_lookup_fingerprint` is removed.
3. Re-ran focused local regression coverage and all required handoff gates.
4. Refreshed this handoff packet with current scope, commands, roadmap/vision mapping, and risk notes.

## Files Changed

- `src/qual/engine/retrieval/payload.py` - rehydrates missing primary excerpt lookup provenance from excerpt citations even when the primary excerpt id is already present.
- `tests/unit/test_unified_retrieval.py` - approved shared regression asserting sparse provenance restores the primary excerpt lookup fingerprint.
- `THREAD_PACKET.md` - handoff packet refreshed for this finalization.

Integrator-locked files: none. Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File budget for this finalization: `3` files changed, within the high-risk `<=8 files` limit.
- Net LOC before packet refresh: `30 insertions(+), 2 deletions(-)`, within the high-risk `<=300 net LOC` limit.
- Routing/provider impact: none.
- PageIndex/embeddings impact: no active retrieval behavior added; PageIndex and embeddings remain deferred compatibility-only paths.
- Remaining risk: low for this finalization; the change is intentionally narrow and covered by focused plus full local tests.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 workflow loop and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-first context handling and auditable generation/workflow state.
- Canonical demo-path mapping: strengthens `retrieve relevant material` by keeping the direct primary excerpt lookup fingerprint available after sparse payload rehydration.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_sparse_provenance_backfills_primary_excerpt_lookup_when_id_survives tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_provenance_surfaces_query_context -v` - passed 2 focused tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke plus 142 unit tests.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, and quality tests.

## Risks/Blockers

No current blockers.
