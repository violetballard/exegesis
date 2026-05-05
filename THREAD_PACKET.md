## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`
- Current merge-base before this fixer pass: `b402b065618b5ad383c527c30b677f03c03a8c88`
- `b402b065618b5ad383c527c30b677f03c03a8c88` classification: source plus packet update, not metadata-only; it modifies `src/qual/retrieval/service.py` and `THREAD_PACKET.md`.
- Final commit: created after this packet refresh; final SHA is reported in the fixer deliverable.
- Scope classification: high-risk fixer under the 4-task cap; implementation edits stay in retrieval lane-owned source paths and focused shared regression coverage.
- Handoff type: retrieval feature fixer handoff for the FTS-first retrieval lane.

## Scope Completed

This pass makes standalone FTS excerpt lookups easier for basket/context consumers to promote without special-casing the single-excerpt lookup shape. The canonical FTS-only excerpt payload now includes deterministic list-shaped `basket_promotion_items`, `basket_item_ids`, and `basket_item_fingerprints` fields alongside the existing singular `basket_promotion_item`, `basket_item_id`, and `basket_item_fingerprint` fields, all built from the same excerpt provenance, source hash, policy snapshot, lookup fingerprint, and text hash already exposed for audited excerpt lookup.

Focused regression coverage now asserts the singular basket promotion fields, list-shaped aliases, basket item provenance, and basket item fingerprint stability on the canonical FTS excerpt lookup payload.

The change keeps SQLite FTS as the authoritative retrieval path. PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Added deterministic list-shaped basket promotion metadata to canonical FTS-only excerpt lookup payloads.
2. Added focused regression coverage for canonical FTS excerpt lookup basket promotion payload propagation and stability.
3. Refreshed the handoff packet so the reviewed range includes source-bearing branch-tip commits and `b402b065618b5ad383c527c30b677f03c03a8c88` is not described as metadata-only.

## Files Changed

- `src/qual/retrieval/service.py` - adds list-shaped deterministic basket promotion metadata to normalized FTS excerpt lookup payloads.
- `tests/unit/test_unified_retrieval.py` - verifies singular/list basket promotion fields, provenance propagation, and stable basket item fingerprints for canonical FTS excerpt lookups.
- `THREAD_PACKET.md` - updates the handoff packet for this fixer pass.

Lane-owned source files:

- `src/qual/retrieval/service.py`

Shared-by-approval files:

- `tests/unit/test_unified_retrieval.py` - focused regression coverage for retrieval lane behavior.

Integrator-locked files: none.

## Budget/Risk

- Task budget: `3/4` high-risk tasks.
- File budget: `3/8` high-risk files.
- Source/test file count: `1` source file, `1` test file.
- Current pass net LOC before commit: `+3` source LOC, focused test additions, plus packet refresh.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is touched only for focused regression coverage required by review.
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
- `make scope-check` PASS; no policy for branch `codex/feat-retrieval-fts`, skipped policy and passed branch check.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, including smoke and 133 unit tests.
- `./typecheck-test.sh` PASS.
- `make ci` PASS, including scope-check, format, lint, compile/typecheck, smoke, and 133 unit tests.

## Risks/Blockers

No blocker remains. Focused retrieval coverage and all required handoff gates passed.
