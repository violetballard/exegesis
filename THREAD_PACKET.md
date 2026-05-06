## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this handoff includes the approved shared-by-approval regression file `tests/unit/test_unified_retrieval.py`.
- Current implementation base for this pass: `a0387c70acd4dadad91c3f70178c8663c90bca96`.
- Final implementation head: reported in the final fixer handoff after the commit is created.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This handoff adds deterministic basket-promotion summary fields to the canonical retrieval citation bundle. Citation-only consumers can now audit whether retrieved FTS excerpts are promotable, and can compare stable basket item IDs/fingerprints without rehydrating the full downstream payload. SQLite FTS remains the only active retrieval path; PageIndex and embeddings remain deferred metadata only.

Canonical demo-path step advanced: `retrieve relevant material`, with support for `promote or gather context into the basket` because citation snapshots now expose deterministic promotion readiness and item identity metadata for later basket, revise, patch, and apply flows.

## Tasks Completed

1. Canonical steps `retrieve relevant material` and `promote or gather context into the basket`: Added basket promotion count/readiness plus stable item IDs/fingerprints to `RetrievalResult.citation_bundle()`.
2. Canonical steps `retrieve relevant material` and `promote or gather context into the basket`: Added approved shared regression coverage proving direct and payload-embedded citation bundles expose the same deterministic basket promotion summary.

## Files Changed

- `src/qual/retrieval/service.py` - citation bundles now include basket promotion count/readiness plus deterministic basket item IDs/fingerprints.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage added for citation-bundle basket promotion summary fields.
- `THREAD_PACKET.md` - handoff packet refreshed for this implementation delta and gate results.

Integrator-locked files: none. Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.

## Budget/Risk

- Task budget: `2/4` high-risk task groups.
- Current delta stat before final commit: `3 files changed, 43 insertions(+), 14 deletions(-)`.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain deferred metadata only; no active non-FTS retrieval behavior added.
- Remaining risk: low. The change is confined to the canonical retrieval result shape plus the approved shared regression.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-first context handling and auditable generation/workflow state.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by surfacing promotion readiness and stable item identity in citation snapshots.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_downstream_payload_includes_retrieval_contract tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_auto_citation_bundle_matches_result_snapshot tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_citation_bundle_matches_result_snapshot` - failed because the first test name was mistyped; the two citation-focused tests in the command passed.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_downstream_payload_exposes_policy_and_diagnostics_snapshot tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_auto_citation_bundle_matches_result_snapshot tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_citation_bundle_matches_result_snapshot` - passed 3 focused retrieval tests.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 75 retrieval tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke plus 144 unit tests.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke, and 144 unit tests.

## Risks/Blockers

The `.codex` packet mirror files were previously observed as read-only in this sandbox. The committed handoff packet for this pass is therefore `THREAD_PACKET.md`, the mutable handoff packet in this worktree.

Final canonical demo-path statement: this work keeps SQLite FTS as the deterministic retrieval source of truth while making citation snapshots sufficient to audit basket promotion readiness and stable retrieved-item identity for downstream revise, patch, and apply flows.
