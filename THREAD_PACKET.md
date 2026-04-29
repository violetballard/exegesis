## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: reviewer-fix re-review packet for the actual branch tip proposed for merge.
- Review baseline from reviewer packet: `378cf9a74a3658058079a32f186fcd254c4a4034`
- Actual branch tip reviewed before this metadata-only fixer commit: `f81b95e8f837bead6df9444e6891cc7cbbf64903`
- Reviewed branch-tip range: `378cf9a74a3658058079a32f186fcd254c4a4034..f81b95e8f837bead6df9444e6891cc7cbbf64903`
- Final proposed merge HEAD after this metadata-only fixer commit: reported in the fixer response.
- Canonical demo-path step advanced: retrieve relevant material for basket/workflow use.

## Scope Completed

This handoff covers the actual branch-tip Milestone 3 retrieval objective: FTS-first structured retrieval for basket and workflow use. It keeps SQLite FTS as the authoritative path for document and excerpt lookup, returns deterministic source/context/citation bundles for workflow promotion, and rehydrates sparse retrieval payloads for downstream engine flows. PageIndex-only and noncanonical excerpt inputs fail closed, and PageIndex/embeddings remain deferred compatibility paths rather than required retrieval paths. No Textual/UI work, provider routing, or speculative alternate retrieval-mode expansion is included.

## Tasks Completed

1. Added FTS-only excerpt lookup/backfill behavior and fail-closed handling for PageIndex-only excerpt IDs.
2. Added deterministic source/context/citation bundle snapshots for basket promotion, including stable source IDs, fingerprints, citation status, query scope, intent, doc type, section hints, and date range.
3. Added engine payload rehydration from compact source/context bundles so sparse downstream inputs recover deterministic retrieval payloads.
4. Added shared regression coverage for excerpt backfill, facade exports, payload normalization, provenance helpers, and basket-promotion snapshots.

## Files Changed

The actual reviewed range `378cf9a74a3658058079a32f186fcd254c4a4034..f81b95e8f837bead6df9444e6891cc7cbbf64903` changes:

- `.codex/kickoff_packets/feat-retrieval-fts.md` (`34` insertions, `2` deletions)
- `.codex/lane_meta/feat-retrieval-fts.json` (`141` insertions, `14` deletions)
- `THREAD_PACKET.md` (`55` insertions, `64` deletions)
- `src/qual/engine/retrieval/payload.py` (`58` insertions, `0` deletions)
- `src/qual/retrieval/service.py` (`85` insertions, `19` deletions)
- `tests/unit/test_unified_retrieval.py` (`102` insertions, `12` deletions)

Range total before this metadata-only fixer commit: `6 files changed, 475 insertions(+), 111 deletions(-)`.

## Budget

- Risk: high, because the actual branch-tip range touches shared-by-approval regression file `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4` under AGENTS high-risk rules.
- File budget before this metadata-only fixer commit: `6/8`.
- Strict AGENTS size accounting before this metadata-only fixer commit: `475 insertions, 111 deletions` (`+364` net LOC), which exceeds the high-risk `<=300` net LOC guideline.
- Implementation-only size accounting if packet metadata is excluded: runtime/test files are `245 insertions, 31 deletions` (`+214` net LOC), within the high-risk `<=300` net LOC guideline. This exclusion covers only handoff metadata files (`.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, and `THREAD_PACKET.md`) because they do not change runtime behavior or tests. Reviewer should use strict AGENTS accounting if metadata exclusions are not accepted.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is included as approved shared regression coverage for the retrieval lane; no integrator-locked files are edited in the reviewed range.

## Roadmap / Vision

- Roadmap item: `ROADMAP.md` Milestone 3 Product Readiness, specifically generation provenance and retrieval evidence attached to workflow outputs.
- Vision capabilities: `PRODUCT_VISION.md` retrieval-backed context (FTS-first for the current MVP), auditable state/workflow.
- Routing/provider impact: none.
- Proposed `README.md` patch text: none.

## Canonical Demo Path

This branch makes the canonical demo-path step `retrieve relevant material` more real by letting FTS-backed retrieval produce deterministic material bundles that can be promoted into basket/workflow state with provenance and citations. It does not add UI, Textual, provider routing, or alternate retrieval-mode behavior.

## Traceability Correction

Earlier packet text incorrectly treated commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as metadata-only. That claim is withdrawn. The actual branch tip presented to this fixer was `f81b95e8f837bead6df9444e6891cc7cbbf64903`, and the truthful reviewed range is `378cf9a74a3658058079a32f186fcd254c4a4034..f81b95e8f837bead6df9444e6891cc7cbbf64903`.

That range includes runtime and test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` in `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`. This fixer pass changes packet metadata only; it does not narrow, split, reset, or modify the reviewed runtime/test implementation.

## Commands Run

Required gates rerun in this fixer pass against the corrected packet state:

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
- Packet mirror status: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain older packet mirror text from prior refreshes. The authoritative corrected handoff packet for this fixer commit is `THREAD_PACKET.md`.
