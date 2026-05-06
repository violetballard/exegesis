## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this handoff includes the approved shared-by-approval regression file `tests/unit/test_unified_retrieval.py`.
- Current implementation range: pending final commit SHA.
- Current implementation head: pending final commit SHA.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This handoff hardens sparse retrieval payload reconstruction so minimal downstream snapshots default back to the canonical FTS-first MVP policy. When source, citation, doc, or summary snapshots omit policy fields, payload normalization now fills `sqlite_fts`, `fts_first`, active strategy `fts`, and deferred `pageindex`/`embeddings` instead of leaving policy and strategy metadata empty. This keeps reconstructed source/context/provenance bundles deterministic and promotion-safe for later basket, revise, patch, and apply flows.

Canonical demo-path step advanced: `retrieve relevant material`, with support for `promote or gather context into the basket` because sparse reconstructed bundles now retain the same FTS-first policy contract used by basket-promotion references.

## Tasks Completed

1. Canonical step `retrieve relevant material`: Defaulted sparse retrieval policy normalization to the FTS-first MVP policy when minimal snapshots omit policy fields.
2. Canonical steps `retrieve relevant material` and `promote or gather context into the basket`: Added approved shared regression coverage proving sparse payload/source/provenance reconstruction preserves FTS-first policy and strategy metadata.

## Files Changed

- `src/qual/engine/retrieval/payload.py` - sparse policy, citation, doc, and summary snapshot normalization now defaults missing policy metadata to the canonical FTS-first MVP policy.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage added for sparse payload defaulting to FTS-first policy metadata.
- `THREAD_PACKET.md` - handoff packet refreshed for this implementation delta and gate results.

Integrator-locked files: none. Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.

## Budget/Risk

- Task budget: `2/4` high-risk task groups.
- Current delta stat before packet refresh: `2 files changed, 64 insertions(+), 15 deletions(-)`.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain deferred metadata only; no active non-FTS retrieval behavior added.
- Remaining risk: low. The change is confined to sparse retrieval snapshot normalization plus the approved shared regression.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-first context handling and auditable generation/workflow state.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by preserving FTS-first policy metadata in sparse reconstructed retrieval bundles.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_engine_retrieval_policy_snapshot_is_stable_and_copy_safe tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_payload_helpers_normalize_tuple_shaped_snapshots` - passed 2 focused baseline retrieval tests.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_sparse_retrieval_payload_defaults_to_fts_first_policy tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_payload_helpers_normalize_tuple_shaped_snapshots` - initially exposed missing sparse summary policy backfill, then passed after the fix.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 75 retrieval tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke plus 144 unit tests.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke, and 144 unit tests.

## Risks/Blockers

The `.codex` packet mirror files were previously observed as read-only in this sandbox. The committed handoff packet for this pass is therefore `THREAD_PACKET.md`, the mutable handoff packet in this worktree.

Final canonical demo-path statement: this work keeps SQLite FTS as the deterministic retrieval source of truth even when downstream consumers reconstruct sparse retrieval snapshots, so retrieved material remains auditable and basket/context promotion stays tied to the same FTS-first policy contract.
