## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: reviewer-fix re-review packet for the actual branch tip proposed for merge.
- Review baseline from reviewer packet: `378cf9a74a3658058079a32f186fcd254c4a4034`
- Actual branch tip reviewed before this metadata-only fixer commit: `662069cf53967e9507d19a8433a72182d98e706a`
- Reviewed branch-tip range: `378cf9a74a3658058079a32f186fcd254c4a4034..662069cf53967e9507d19a8433a72182d98e706a`
- Final proposed merge HEAD after this metadata-only fixer commit: reported in the fixer response.
- Canonical demo-path step advanced: retrieve relevant material and promote or gather context into the basket.

## Scope Completed

This handoff covers the real branch-tip Milestone 3 retrieval objective: FTS-first structured retrieval for basket and workflow use. SQLite FTS remains the authoritative path for document and excerpt lookup, PageIndex-only excerpt IDs fail closed, sparse source/context bundles rehydrate deterministic retrieval payloads, and retrieval responses now include compact basket-promotion snapshots with stable source IDs, fingerprints, query scope, citation status, section hints, and date-range metadata. PageIndex and embeddings remain compatibility-only fallback shims. No Textual/UI work, provider routing, or speculative alternate retrieval-mode expansion is included.

## Tasks Completed

1. Added FTS-only excerpt lookup/backfill behavior and fail-closed handling for PageIndex-only excerpt IDs.
2. Added deterministic source/context/citation bundle snapshots for basket promotion, including stable source IDs, fingerprints, citation status, query scope, intent, doc type, section hints, and date range.
3. Added engine payload rehydration from compact source/context bundles so sparse downstream inputs recover deterministic retrieval payloads.
4. Added shared regression coverage for excerpt backfill, facade exports, payload normalization, provenance helpers, and basket-promotion snapshots.

## Files Changed

The actual reviewed range `378cf9a74a3658058079a32f186fcd254c4a4034..662069cf53967e9507d19a8433a72182d98e706a` changes:

- `.codex/kickoff_packets/feat-retrieval-fts.md` (`34` insertions, `2` deletions)
- `.codex/lane_meta/feat-retrieval-fts.json` (`141` insertions, `14` deletions)
- `THREAD_PACKET.md` (`63` insertions, `64` deletions)
- `src/qual/engine/retrieval/payload.py` (`58` insertions, `0` deletions)
- `src/qual/retrieval/service.py` (`85` insertions, `19` deletions)
- `tests/unit/test_unified_retrieval.py` (`102` insertions, `12` deletions)

Range total before this metadata-only fixer commit: `6 files changed, 483 insertions(+), 111 deletions(-)`.

Implementation/test files in the reviewed range:

- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Budget

- Risk: high, because the reviewed range touches shared retrieval payload behavior and the shared-by-approval regression file `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4` under AGENTS high-risk rules.
- File budget before this metadata-only fixer commit: `6/8`.
- Strict AGENTS size accounting before this metadata-only fixer commit: `483 insertions, 111 deletions` (`+372` net LOC), which exceeds the high-risk `<=300` net LOC guideline.
- Implementation/test size accounting if packet metadata is excluded: runtime/test files are `245 insertions, 31 deletions` (`+214` net LOC), within the high-risk `<=300` net LOC guideline. This exclusion covers only handoff metadata files because they do not change runtime behavior or tests.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is included as approved shared regression coverage for the retrieval lane; no integrator-locked files are edited in the reviewed range.

## Roadmap / Vision

- Roadmap item: `ROADMAP.md` Milestone 3 Product Readiness, specifically generation provenance and retrieval evidence attached to workflow outputs.
- Vision capabilities: `PRODUCT_VISION.md` retrieval-backed context, context basket support, and auditable state/workflow.
- Canonical demo-path mapping: the basket-promotion snapshots explicitly support the step "promote or gather context into the basket."
- Routing/provider impact: none.
- Proposed `README.md` patch text: none.

## Traceability Correction

Earlier packet text incorrectly treated commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as metadata-only. That claim is withdrawn. The actual branch tip presented to this fixer was `662069cf53967e9507d19a8433a72182d98e706a`, and the truthful reviewed range is `378cf9a74a3658058079a32f186fcd254c4a4034..662069cf53967e9507d19a8433a72182d98e706a`.

That range includes runtime and test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` in `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`. This fixer pass changes packet metadata only; it does not narrow, split, reset, or modify the reviewed runtime/test implementation.

## Reviewer Required Fixes Addressed

1. The reviewed range is regenerated against the actual merge candidate that existed when this fixer started: `378cf9a74a3658058079a32f186fcd254c4a4034..662069cf53967e9507d19a8433a72182d98e706a`.
2. The basket-promotion behavior is listed as a completed high-risk task and mapped to the canonical demo-path step "promote or gather context into the basket."
3. All changed production/test files are included in the handoff, with high-risk budget compliance restated against the actual diff.
4. Required gates are rerun in this fixer pass and reported below.

## Commands Run

Required gates rerun in this fixer pass against the exact merge candidate after the metadata update:

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS, including smoke plus 126 unit tests
- `./typecheck-test.sh`: PASS
- `make ci`: PASS, including scope-check, format, lint, compileall, and smoke plus 126 unit tests

## Risks / Blockers

- Residual risk: broader retrieval orchestration beyond deterministic source/context bundles remains separate high-risk work.
- Budget risk: the actual base-to-tip range exceeds the high-risk net LOC guideline when packet metadata is counted; reviewer should evaluate that explicitly instead of relying on a narrowed packet slice.
- Shared-file note: `tests/unit/test_unified_retrieval.py` is the only shared-by-approval file in this slice.
