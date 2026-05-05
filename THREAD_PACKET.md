## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Reviewed implementation range for re-review: `b402b065618b5ad383c527c30b677f03c03a8c88..HEAD`
- Current merge-base before this fixer pass: `b402b065618b5ad383c527c30b677f03c03a8c88`
- Final commit: created after this packet refresh; final SHA is reported in the fixer deliverable.
- Scope classification: high-risk fixer under the 4-task cap; implementation edits stay in retrieval lane-owned source paths and focused shared regression coverage.
- Handoff type: retrieval feature fixer handoff for the FTS-first retrieval lane.

## Scope Completed

This pass makes standalone FTS excerpt lookups more directly auditable for basket/context promotion by exposing a deterministic `basket_promotion_count` next to the existing singular and list-shaped basket promotion fields, and by carrying the same count into excerpt provenance. The count is derived only when the canonical FTS-only lookup can build the basket promotion item, so basket consumers can verify the one-excerpt promotion shape without re-counting optional fields or special-casing aliases.

Focused regression coverage now asserts the count on the canonical FTS excerpt lookup payload and provenance alongside the existing singular/list promotion fields, provenance propagation, and stable basket item fingerprints.

The change keeps SQLite FTS as the authoritative retrieval path. PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Added deterministic basket promotion count metadata to canonical FTS-only excerpt lookup payloads and provenance.
2. Added focused regression coverage for the promotion count on canonical FTS excerpt lookup payloads and provenance.
3. Refreshed the handoff packet for this source-bearing fixer pass.

## Files Changed

- `src/qual/retrieval/service.py` - adds deterministic `basket_promotion_count` metadata to normalized FTS excerpt lookup payloads and provenance.
- `tests/unit/test_unified_retrieval.py` - verifies the count on the canonical FTS excerpt lookup contract and provenance.
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
- Current pass net LOC before commit: `+2` source LOC, focused test assertions, plus packet refresh.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is touched only for focused regression coverage required by retrieval contract review.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; both remain deferred/compatibility-only.
- Remaining risk: low implementation risk; the change is additive to FTS excerpt lookup payloads and reuses the existing basket promotion item construction path.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` active MVP focus for `feat-retrieval-fts`; Milestone 3/4 retrieval layer support for retrieving relevant material and promoting or gathering context into basket flows.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation/state.
- Canonical demo-path mapping: this work advances `retrieve relevant material` and supports basket/context promotion by making standalone FTS excerpt lookups expose deterministic promotion cardinality with the promotion item list and excerpt provenance.
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
