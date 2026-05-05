## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Reviewed implementation range for re-review: `b402b065618b5ad383c527c30b677f03c03a8c88..HEAD`
- Current merge-base before this fixer pass: `b402b065618b5ad383c527c30b677f03c03a8c88`
- Final commit: created after this packet refresh; final SHA is reported in the fixer deliverable.
- Scope classification: high-risk fixer under the 4-task cap; implementation edits stay in retrieval lane-owned source paths. No shared regression files are touched by this pass.
- Handoff type: retrieval feature fixer handoff for the FTS-first retrieval lane.

## Scope Completed

This pass extends deterministic basket promotion cardinality from standalone FTS excerpt lookups into the canonical retrieval result, downstream payload, source bundle, and context bundle surfaces. Engine consumers now receive `basket_promotion_count` alongside `basket_promotion_items`, `basket_item_ids`, and `basket_item_fingerprints` whether they hold a full result, a sparse downstream payload, a source bundle, or a context bundle.

Focused regression coverage was re-run against the existing unified retrieval contract to verify the new source-level count propagation does not drift from the canonical service result shape.

The change keeps SQLite FTS as the authoritative retrieval path. PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Added deterministic basket promotion count propagation to canonical retrieval result context/source bundle snapshots.
2. Added deterministic basket promotion count reconstruction to engine payload/source/context bundle helpers for sparse retrieval snapshots.
3. Re-ran focused unified retrieval regression coverage.
4. Refreshed the handoff packet for this source-bearing fixer pass.

## Files Changed

- `src/qual/retrieval/service.py` - carries deterministic `basket_promotion_count` metadata on canonical retrieval context and source bundle snapshots.
- `src/qual/engine/retrieval/payload.py` - reconstructs and preserves deterministic `basket_promotion_count` metadata across downstream payload, source bundle, and context bundle helper paths.
- `THREAD_PACKET.md` - updates the handoff packet for this fixer pass.

Lane-owned source files:

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`

Shared-by-approval files:

- none in this pass.

Integrator-locked files: none.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `3/8` high-risk files.
- Source/test file count: `2` source files, `0` test files.
- Current pass net LOC before commit: focused source additions plus packet refresh.
- Shared-file approval note: no shared-by-approval files are touched by this pass.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; both remain deferred/compatibility-only.
- Remaining risk: low implementation risk; the change is additive to existing FTS-first basket promotion metadata and reuses normalized basket item IDs for deterministic counts.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` active MVP focus for `feat-retrieval-fts`; Milestone 3/4 retrieval layer support for retrieving relevant material and promoting or gathering context into basket flows.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation/state.
- Canonical demo-path mapping: this work advances `retrieve relevant material` and supports basket/context promotion by making full and sparse retrieval snapshots expose deterministic promotion cardinality with the promotion item list, item IDs, and item fingerprints.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m unittest tests.unit.test_unified_retrieval -q` PASS, 64 tests.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, including smoke and 133 unit tests.
- `./typecheck-test.sh` PASS.
- `make ci` PASS, including scope-check, format, lint, compile/typecheck, smoke, and 133 unit tests.

## Risks/Blockers

No blocker remains. Focused retrieval coverage and all required handoff gates passed.
