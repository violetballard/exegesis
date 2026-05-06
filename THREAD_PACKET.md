## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this finalization includes the approved shared-by-approval retrieval regression file `tests/unit/test_unified_retrieval.py`.
- Current base before this finalization: `f5952a2cd457abc5de0f47d8311efe533baeab73`
- Final branch tip: reported in the fixer handoff after commit creation.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this finalization.

## Scope Completed

This finalization adds the primary excerpt lookup fingerprint to the canonical FTS-first retrieval summary and provenance snapshots, then preserves that field when sparse downstream payloads are rehydrated from excerpt citations. That gives basket promotion and later revise/apply flows a direct, deterministic primary excerpt lookup handle without walking the full excerpt hit array.

Canonical demo-path step advanced: `retrieve relevant material` for basket/workflow promotion. The change preserves the FTS-only retrieval path and narrows the engine-facing payload contract around auditable primary excerpt lookup provenance for downstream basket, revise, patch, and apply flows.

## Tasks Completed

1. Added `primary_excerpt_lookup_fingerprint` to the retrieval summary and provenance snapshots produced by FTS-first results.
2. Backfilled `primary_excerpt_lookup_fingerprint` from excerpt citations when sparse downstream payloads rebuild retrieval provenance.
3. Added approved shared regression assertions for the primary excerpt lookup fingerprint in canonical payload and provenance output.
4. Re-ran focused local regression coverage and refreshed this handoff packet with current scope, commands, roadmap/vision mapping, and risk notes.

## Files Changed

- `src/qual/retrieval/service.py` - includes the primary excerpt lookup fingerprint in deterministic retrieval summary and provenance snapshots.
- `src/qual/engine/retrieval/payload.py` - rehydrates the primary excerpt lookup fingerprint from sparse payload summaries or excerpt citations.
- `tests/unit/test_unified_retrieval.py` - approved shared regression assertions for canonical payload/provenance primary excerpt lookup fingerprints.
- `THREAD_PACKET.md` - handoff packet refreshed for this finalization.

Integrator-locked files: none. Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File budget for this finalization: `4` files changed, within the high-risk `<=8 files` limit.
- Net LOC for code/test change before packet refresh: `24 insertions(+), 0 deletions(-)`, within the high-risk `<=300 net LOC` limit.
- Routing/provider impact: none.
- PageIndex/embeddings impact: no active retrieval behavior added; PageIndex and embeddings remain deferred compatibility-only paths.
- Remaining risk: low for this finalization; the change is intentionally narrow and covered by focused plus full local tests.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 workflow loop and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-first context handling and auditable generation/workflow state.
- Canonical demo-path mapping: strengthens `retrieve relevant material` by exposing a direct primary excerpt lookup fingerprint for basket promotion and later revise/apply provenance checks.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m pytest tests/unit/test_unified_retrieval.py` - blocked before running tests because the active `/opt/homebrew/opt/python@3.14/bin/python3.14` environment has no `pytest` module.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_downstream_payload_exposes_policy_and_diagnostics_snapshot tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_provenance_surfaces_query_context -v` - passed 2 focused tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke plus 141 unit tests.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, and quality tests.

## Risks/Blockers

No current blockers. The only non-passing command was the optional direct `pytest` attempt, which did not execute tests because `pytest` is not installed for that interpreter; the repo-required wrappers and `python3 -m unittest` coverage passed.
