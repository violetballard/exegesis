## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this finalization includes the approved shared-by-approval retrieval regression file `tests/unit/test_unified_retrieval.py`.
- Current base before this finalization: `5c3ec3d8e2200ed146a25d1377e0f2e189a19031`
- Final branch tip: reported in the final fixer handoff after commit creation.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this finalization.

## Scope Completed

This finalization hardens sparse downstream provenance rehydration so retained-but-empty identity fields are treated as missing and backfilled from the canonical retrieval summary, diagnostics, and query snapshot. That keeps query scope, intent, result fingerprint, backend/mode, candidate counts, and hit fingerprints deterministic for downstream basket promotion plus revise, patch, and apply flows that rebuild provenance from partial payload snapshots.

Canonical demo-path step advanced: `retrieve relevant material` for basket/workflow promotion. The change preserves the FTS-only retrieval path and narrows the engine-facing payload contract around auditable sparse provenance repair for downstream basket, revise, patch, and apply flows.

## Tasks Completed

1. Updated sparse retrieval provenance rebuild logic to backfill empty core identity fields, not only absent fields.
2. Added approved shared regression coverage for sparse provenance snapshots that retain empty query/result/backend identity fields.
3. Re-ran focused local regression coverage and all required handoff gates.
4. Refreshed this handoff packet with current scope, commands, roadmap/vision mapping, and risk notes.

## Files Changed

- `src/qual/engine/retrieval/payload.py` - treats empty sparse provenance identity fields as missing and backfills them from canonical FTS-first snapshots.
- `tests/unit/test_unified_retrieval.py` - approved shared regression asserting sparse provenance restores empty identity fields from summary/diagnostics.
- `THREAD_PACKET.md` - handoff packet refreshed for this finalization.

Integrator-locked files: none. Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File budget for this finalization: `3` files changed, within the high-risk `<=8 files` limit.
- Net LOC before packet refresh: `47 insertions(+), 9 deletions(-)`, within the high-risk `<=300 net LOC` limit.
- Routing/provider impact: none.
- PageIndex/embeddings impact: no active retrieval behavior added; PageIndex and embeddings remain deferred compatibility-only paths.
- Remaining risk: low for this finalization; the change is intentionally narrow and covered by focused plus full local tests.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 workflow loop and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-first context handling and auditable generation/workflow state.
- Canonical demo-path mapping: strengthens `retrieve relevant material` by keeping sparse retrieval provenance usable for basket promotion and later revise/apply steps.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_sparse_provenance_treats_empty_identity_fields_as_missing tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_sparse_provenance_backfills_primary_excerpt_lookup_when_id_survives -v` - passed 2 focused tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke plus 143 unit tests.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, and quality tests.

## Risks/Blockers

No current blockers.
