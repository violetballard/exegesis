## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Reviewed implementation range for re-review: `b402b065618b5ad383c527c30b677f03c03a8c88..HEAD`
- Current merge-base before this fixer pass: `b402b065618b5ad383c527c30b677f03c03a8c88`
- Final branch tip: created after this packet refresh; final SHA is reported in the fixer deliverable.
- Scope classification: high-risk fixer under the 4-task cap because this reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Handoff type: retrieval feature fixer handoff for the FTS-first retrieval lane.

## Scope Completed

This re-review packet covers every source-bearing commit from `b402b065618b5ad383c527c30b677f03c03a8c88..HEAD`, including the commits that expose excerpt bundle basket metadata and retrieval summary basket references. No source-bearing commit after `b402b065618b5ad383c527c30b677f03c03a8c88` is hidden behind metadata-only packet wording.

The reviewed implementation extends deterministic basket promotion metadata into the canonical FTS excerpt payload, compact retrieval summary, provenance snapshots, and engine payload normalization. Engine consumers that inspect excerpt, summary, or provenance payloads now get `basket_promotion_count`, `basket_item_ids`, and `basket_item_fingerprints` without having to traverse the full source bundle.

The engine payload helpers now preserve and recover those same promotion IDs, counts, and fingerprints from sparse retrieval-summary snapshots. This keeps basket promotion auditable for downstream drafting, revise, and apply flows when compact summary payloads survive independently from the full source bundle.

Focused regression coverage was updated and re-run against the existing unified retrieval contract to verify canonical FTS excerpt lookup, excerpt bundle metadata, retrieval summary metadata, and engine payload reconstruction.

The change keeps SQLite FTS as the authoritative retrieval path. PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Exposed canonical FTS excerpt lookup basket item lists and promotion counts in retrieval service payloads.
2. Propagated deterministic basket promotion IDs, fingerprints, and counts through canonical excerpt bundles, retrieval summaries, and provenance snapshots.
3. Added deterministic basket promotion ID/count/fingerprint recovery to engine payload normalization for sparse retrieval-summary snapshots.
4. Updated approved shared unified retrieval regression coverage and refreshed the handoff packet for the source-bearing reviewed range through branch tip.

## Files Changed

- `src/qual/retrieval/service.py` - carries deterministic basket promotion metadata on canonical retrieval summary and provenance snapshots.
- `src/qual/engine/retrieval/payload.py` - reconstructs and preserves deterministic basket promotion IDs, counts, and fingerprints from direct or sparse retrieval summary snapshots.
- `tests/unit/test_unified_retrieval.py` - verifies canonical FTS excerpt lookup, excerpt bundle basket metadata, retrieval summary basket references, and payload reconstruction.
- `THREAD_PACKET.md` - updates the handoff packet for this fixer pass.

Lane-owned source files:

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`

Shared-by-approval files:

- `tests/unit/test_unified_retrieval.py` - approved shared regression surface for the retrieval lane canonical contract.

Integrator-locked files: none.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `4/8` high-risk files.
- Source/test file count: `2` source files, `1` test file.
- Current pass net LOC before commit: focused source additions plus packet refresh.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is the approved shared-by-approval regression file for this lane.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; both remain deferred/compatibility-only.
- Remaining risk: low implementation risk; the change is additive to existing FTS-first basket promotion metadata and reuses normalized basket item helpers for deterministic reconstruction.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` active MVP focus for `feat-retrieval-fts`; Milestone 3/4 retrieval layer support for retrieving relevant material and promoting or gathering context into basket flows.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation/state.
- Canonical demo-path mapping: this work advances the AGENTS active MVP canonical demo-path step `retrieve relevant material` and supports basket/context promotion by making canonical FTS excerpt, summary, and provenance snapshots expose deterministic promotion counts, item IDs, and item fingerprints.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` PASS; no branch-specific policy, scope check passed for `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, including smoke and 133 unit tests.
- `./typecheck-test.sh` PASS.
- `make ci` PASS, including scope-check, format, lint, compile/typecheck, smoke, and 133 unit tests.

## Risks/Blockers

No blocker remains. Focused retrieval coverage and all required handoff gates passed.
