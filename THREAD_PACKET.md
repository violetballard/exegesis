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

This pass extends deterministic basket promotion metadata into the excerpt-focused retrieval bundle itself. Engine consumers that receive only the excerpt bundle now get `basket_promotion_items`, `basket_promotion_count`, `basket_item_ids`, and `basket_item_fingerprints` alongside the canonical excerpt hits and excerpt citations.

The engine payload helpers now reconstruct those same promotion fields from sparse excerpt-bundle snapshots, including snapshots that only preserve `excerpt_hits`. This keeps basket promotion ready for downstream drafting, revise, and apply flows without requiring callers to hold the full downstream payload or source bundle.

Focused regression coverage was re-run against the existing unified retrieval contract to verify the new excerpt-bundle promotion metadata does not drift from the canonical service result shape.

The change keeps SQLite FTS as the authoritative retrieval path. PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Added deterministic basket promotion refs, IDs, fingerprints, and count to canonical retrieval excerpt bundles.
2. Added deterministic basket promotion reconstruction to engine excerpt-bundle normalization for sparse snapshots.
3. Re-ran focused unified retrieval regression coverage and full local handoff gates.
4. Refreshed the handoff packet for this source-bearing fixer pass.

## Files Changed

- `src/qual/retrieval/service.py` - carries deterministic basket promotion metadata on canonical retrieval excerpt bundle snapshots.
- `src/qual/engine/retrieval/payload.py` - reconstructs and preserves deterministic basket promotion metadata when normalizing direct or sparse excerpt bundle snapshots.
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
- Remaining risk: low implementation risk; the change is additive to existing FTS-first basket promotion metadata and reuses normalized basket item helpers for deterministic reconstruction.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` active MVP focus for `feat-retrieval-fts`; Milestone 3/4 retrieval layer support for retrieving relevant material and promoting or gathering context into basket flows.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation/state.
- Canonical demo-path mapping: this work advances `retrieve relevant material` and supports basket/context promotion by making excerpt-focused retrieval snapshots expose deterministic promotion refs with the promotion item list, promotion count, item IDs, and item fingerprints.
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
