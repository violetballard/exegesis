## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Merge candidate for re-review: branch tip `HEAD` on `codex/feat-retrieval-fts`; pre-commit tip for this pass was `0a0b05709`.
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk under the 4-task cap because this pass updates approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is the sole approved shared-by-approval regression surface for this retrieval lane pass.

## Scope Completed

This pass closes a doc-hit provenance gap in the FTS-first retrieval contract. Excerpt hits already carried the canonical FTS `excerpt_lookup_fingerprint`; doc hits now carry the matching `top_excerpt_lookup_fingerprint` for their top-ranked excerpt. That fingerprint is exposed through doc-hit dictionaries, doc citation snapshots, retrieval evidence, retrieval summaries, retrieval manifests, result fingerprints, and sparse payload normalization.

The change keeps SQLite FTS as the only active retrieval path. PageIndex and embeddings remain deferred compatibility identifiers only; this pass does not add alternate retrieval modes, provider routing, UI behavior, or Textual console work.

This supports the demo-path step `retrieve relevant material` by making the doc-level hit point at the exact FTS lookup identity for its promoted top excerpt. It also supports `promote or gather context into the basket` because downstream engine flows can audit a doc hit, its top excerpt citation, and the eventual basket promotion reference against the same deterministic FTS lookup fingerprint.

## Tasks Completed

1. Added `top_excerpt_lookup_fingerprint` to `RetrievalDocHit.as_dict()` when present in provenance.
2. Propagated the top excerpt lookup fingerprint through doc citation snapshots, retrieval evidence, retrieval summary snapshots, retrieval manifests, and result fingerprint inputs.
3. Preserved the new manifest/summary list in engine-side sparse retrieval payload normalization.
4. Updated the approved unified retrieval regression coverage to verify doc-hit, manifest, evidence/provenance, and engine payload exposure.

## Files Changed

- `src/qual/retrieval/service.py` - carries the top excerpt lookup fingerprint through doc-hit provenance, doc citations, summaries, manifests, evidence, and result fingerprints.
- `src/qual/engine/retrieval/payload.py` - normalizes `top_excerpt_lookup_fingerprints` in sparse summary and manifest snapshots.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage for the canonical retrieval contract.
- `THREAD_PACKET.md` - current handoff packet.

Integrator-locked files: none.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `4` files changed, within the high-risk `<=8 files` limit.
- Net LOC: small contract propagation and focused regression update, within the high-risk `<=300 net LOC` limit.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; both remain deferred/compatibility-only and are not active retrieval paths.
- Remaining risk: downstream consumers that compare full result fingerprints will see a new fingerprint because the doc manifest now includes the top excerpt lookup fingerprint. That is intentional provenance tightening for the FTS-first contract.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation.
- Canonical demo-path mapping: advances `retrieve relevant material` and `promote or gather context into the basket` by tying doc-level hits to the canonical FTS lookup identity used for excerpt lookup and basket promotion.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m pytest tests/unit/test_unified_retrieval.py` - blocked because the active Python 3.14 interpreter does not have `pytest` installed.
- `./quality-test.sh` - passed; ran smoke plus 140 unit tests, including the unified retrieval suite.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed; reran setup, scope-check, format, lint, typecheck, and quality tests. Scope-check reported no explicit policy for branch `codex/feat-retrieval-fts` and exited green.

## Risks/Blockers

No active blockers. Re-review should inspect the current branch tip and confirm the new doc-level `top_excerpt_lookup_fingerprint` remains FTS-only and deterministic.
