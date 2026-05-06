## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this handoff updates the approved shared-by-approval regression file `tests/unit/test_unified_retrieval.py`.
- Review boundary for this fixer handoff: `d0207fdf4bf431ed4ebb34f51e20f19b9c6298dd..FINAL_HEAD_REPORTED_IN_HANDOFF`.
- Source/test implementation base: `d0207fdf4bf431ed4ebb34f51e20f19b9c6298dd`.
- Final HEAD SHA: reported in the final response after the commit is created.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This focused fixer pass strengthens the FTS-first retrieval contract by adding ordered `excerpt_lookup_fingerprints` to the canonical retrieval manifest, retrieval summary, retrieval evidence, and result fingerprint input. Engine-side retrieval payload normalization now preserves that field for sparse source/summary/manifest snapshots.

Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. The change makes the full ordered excerpt lookup identity available beside excerpt IDs, excerpt fingerprints, text hashes, citations, and basket item fingerprints so downstream revise, patch, and apply flows can audit which FTS lookup identities were promoted or used without rehydrating PageIndex or embeddings.

## Tasks Completed

1. Canonical step `retrieve relevant material`: Added ordered excerpt lookup fingerprint lists to FTS retrieval manifest and summary snapshots.
2. Canonical step `promote or gather context into the basket`: Added the same ordered lookup identity list to retrieval evidence and result fingerprint inputs so basket/workflow promotion can audit stable excerpt lookup identity.
3. Engine payload compatibility: Updated retrieval payload normalization to preserve `excerpt_lookup_fingerprints` in sparse summary and manifest snapshots.
4. Shared regression coverage: Extended the approved shared retrieval test to assert manifest, summary, and evidence carry the ordered excerpt lookup fingerprints.

## Files Changed

- `THREAD_PACKET.md` - authoritative handoff packet for this focused fixer pass.
- `src/qual/engine/retrieval/payload.py` - normalizes `excerpt_lookup_fingerprints` in retrieval summary and manifest snapshots.
- `src/qual/retrieval/service.py` - emits ordered `excerpt_lookup_fingerprints` in canonical retrieval manifest, summary, evidence, and result fingerprint payload.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the new retrieval lookup identity field.

Integrator-locked files: none. Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- Actual source/test/packet delta before final commit: `4 files changed, 64 insertions(+), 30 deletions(-)`.
- AGENTS size/file status: within high-risk file budget `<=8 files`; net LOC decreases after replacing the stale packet.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain deferred compatibility metadata/fallback-only behavior; no active non-FTS retrieval path is introduced.
- Remaining risk: none known after local gates.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context and auditable state/workflow.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by surfacing stable FTS excerpt lookup identities alongside promotion-ready basket references.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m pytest tests/unit/test_unified_retrieval.py` - blocked because `/opt/homebrew/opt/python@3.14/bin/python3.14` has no `pytest` module.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed; 75 retrieval tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke plus 144 unit tests.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke, and 144 unit tests.

## Risks/Blockers

No blocker remains. The initial direct `pytest` invocation was not a repo gate and failed only because that interpreter does not provide `pytest`; the repo's `unittest` and required shell gates pass.

Final canonical demo-path statement: this work keeps SQLite FTS as the deterministic retrieval source of truth while making structured retrieval snapshots sufficient to audit basket promotion readiness and stable retrieved-item identity for downstream revise, patch, and apply flows.
