## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Base branch HEAD before this pass: `b402b065618b5ad383c527c30b677f03c03a8c88`
- Final commit: created after this packet refresh; final SHA is reported in the fixer deliverable.
- Scope classification: high-risk packet refresh under the 4-task cap; implementation edits stay in retrieval lane-owned source paths.
- Handoff type: retrieval feature fixer handoff for the FTS-first retrieval lane.

## Scope Completed

This pass makes standalone FTS excerpt lookups easier for basket/context consumers to promote without special-casing the single-excerpt lookup shape. The canonical FTS-only excerpt payload now includes deterministic list-shaped `basket_promotion_items`, `basket_item_ids`, and `basket_item_fingerprints` fields alongside the existing singular `basket_promotion_item`, `basket_item_id`, and `basket_item_fingerprint` fields, all built from the same excerpt provenance, source hash, policy snapshot, lookup fingerprint, and text hash already exposed for audited excerpt lookup.

The change keeps SQLite FTS as the authoritative retrieval path. PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Added deterministic list-shaped basket promotion metadata to canonical FTS-only excerpt lookup payloads.

## Files Changed

- `src/qual/retrieval/service.py` - adds list-shaped deterministic basket promotion metadata to normalized FTS excerpt lookup payloads.
- `THREAD_PACKET.md` - updates the handoff packet for this fixer pass.

Lane-owned source files:

- `src/qual/retrieval/service.py`

Shared-by-approval files: none changed in this pass.

Integrator-locked files: none.

## Budget/Risk

- Task budget: `1/4` high-risk tasks.
- File budget: `2/8` high-risk files.
- Source/test file count: `1` source file.
- Current pass net LOC before commit: `+3` source LOC plus packet refresh.
- Shared-file approval note: no shared-by-approval file changed in this pass; existing approved shared regression coverage remains in `tests/unit/test_unified_retrieval.py`.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; both remain deferred/compatibility-only.
- Remaining risk: low implementation risk; the change is additive to FTS excerpt lookup payloads and reuses the existing basket item fingerprint builder.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` active MVP focus for `feat-retrieval-fts`; Milestone 3/4 retrieval layer support for retrieving relevant material and promoting or gathering context into basket flows.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation/state.
- Canonical demo-path mapping: this work advances `retrieve relevant material` and supports basket/context promotion by making standalone FTS excerpt lookups carry deterministic promotion item lists without requiring a full retrieval result reassembly.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m unittest tests.unit.test_unified_retrieval -q` PASS, 64 tests.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 133 tests.
- `./typecheck-test.sh` PASS.
- `make ci` PASS, including scope-check for `codex/feat-retrieval-fts` and 133 tests.

## Risks/Blockers

No blocker remains. Focused retrieval coverage and all required handoff gates passed.
