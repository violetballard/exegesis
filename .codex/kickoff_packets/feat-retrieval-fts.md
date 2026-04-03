# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Packet HEAD role: `metadata-only reviewer-fix refresh`
- Packet refresh trace anchor before the final fixer commit: `d2f02f019b5a38d79074ec871d2f284308abfe43`
- Final HEAD SHA (reviewed implementation head): `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Handoff type: retrieval feature handoff for the FTS-first retrieval lane.
- Approved exception note: Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract. No other shared-by-approval files are part of the reviewed retrieval implementation range.
- Traceability rule: later metadata-only packet refresh commits may advance the branch head, but they do not change the reviewed implementation head or reviewed implementation range unless this packet is explicitly regenerated to do so.

## Scope completed

The retrieval lane shipped an FTS-first retrieval MVP: SQLite FTS remains authoritative, the canonical retrieval query constructor is exported through both retrieval facades, retrieval payloads and provenance snapshots are deterministic for downstream engine flows, sparse source and context bundles rehydrate deterministically, and the excerpt lookup surface now uses the canonical FTS-only path so PageIndex-only excerpt IDs fail closed under shared regression coverage. PageIndex plus embeddings remain compatibility-only fallback shims that fail closed. The branch contains later metadata-only packet refresh commits; the only shared-by-approval edit in the reviewed implementation range is `tests/unit/test_unified_retrieval.py`, and those later packet-refresh commits, including `b172559ed0889b5793e150296fa4b8b6c9943931` and `d2f02f019b5a38d79074ec871d2f284308abfe43`, stay outside that reviewed implementation range.

## Budget note

This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work and should be read against the 4-task cap. The detailed task summary in `THREAD_PACKET.md` folds the cumulative retrieval thread into four meaningful items, and later metadata-only packet refresh commits do not change the reviewed implementation range.

## Reviewer fix reconciliation

This kickoff packet now matches the reviewer-required packet corrections: the handoff is classified as shared/high-risk work under the 4-task cap, the reviewed implementation range remains anchored to `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, and the dedicated `Scope completed` section describes the FTS-first retrieval outcome separately from later metadata-only packet refreshes.

## Required fixes addressed

1. The handoff is explicitly classified as shared/high-risk work because `tests/unit/test_unified_retrieval.py` is shared-by-approval, so the 4-task cap applies.
2. The metadata-only packet refresh chain is separated from the reviewed implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and the reviewed implementation range `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. The dedicated `Scope completed` section remains the short, standalone summary of the FTS-first retrieval outcome that the reviewer asked for.

## Packet trace note

The packet refresh trace anchor is `d2f02f019b5a38d79074ec871d2f284308abfe43`; it is metadata-only and is not automatically the reviewed implementation head. This packet does not self-record the current branch head because doing so would become stale as soon as the fixer commit is created; use the final HEAD SHA reported with the fixer handoff for the actual branch tip. The reviewed implementation head for retrieval scope remains `adfa8cdadd43747ffbcb612e4151e262b13e52ca`. Metadata-only packet refresh commits after that reviewed implementation head, including `b172559ed0889b5793e150296fa4b8b6c9943931`, remain outside the reviewed implementation range unless the packet is regenerated to move the reviewed implementation head or reviewed implementation range. Read the retrieval file list and completed-task summary against that reviewed implementation range, not against the later metadata-only packet refresh chain; the cited packet-refresh SHAs are representative rather than exhaustive.

## Packet HEAD context

This fixer pass creates another metadata-only packet refresh commit, so the packet-refresh branch tip is reported in the final fixer handoff rather than embedded here before the commit exists. The reviewer-referenced SHA `b172559ed0889b5793e150296fa4b8b6c9943931` remains a metadata-only packet refresh commit, not the reviewed retrieval implementation head. Re-review should anchor retrieval implementation scope to `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, then use the final fixer handoff for the current packet-refresh branch tip after `d2f02f019b5a38d79074ec871d2f284308abfe43`.

## Branch-head traceability

Metadata-only packet refresh commits may continue to advance the branch head after this handoff packet is refreshed without moving the reviewed retrieval implementation head. Re-review should anchor traceability to `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`; if a later branch head changes retrieval code or the approved shared regression file, the packet must be regenerated before approval.

## Verification note

The current packet-refresh head preserves the reviewed implementation range above and does not expand retrieval scope beyond that range. Required local gates were re-run on the packet-refresh branch head before this packet was refreshed. This fixer pass is metadata-only and gives the reviewer-required packet corrections their own packet-refresh commit without moving the reviewed implementation range.
This commit records the post-review fixer pass that re-ran all required local gates while preserving the same reviewed implementation range.

### Priority outcomes
1. Make SQLite FTS the primary retrieval path.
2. Return doc hits and excerpt hits with stable provenance.
3. Keep PageIndex and embeddings fallback-only behind the canonical retrieval facade.

### Source of truth
- Canonical retrieval logic remains in `src/qual/retrieval/**`.
- Engine-side retrieval exports, compatibility shims, and payload helpers remain in `src/qual/engine/retrieval/**`.
- Payload normalization keeps query, policy, provenance, and hit snapshots deterministic for downstream consumers.
- Constraint payloads stay mapping/dataclass-shaped; iterable `doc_types` and `date_range` values are normalized deterministically from those inputs.
- Approved shared regression coverage remains in `tests/unit/test_unified_retrieval.py`; no other shared or integrator-locked files are part of the reviewed retrieval implementation.

### Guardrails
- Keep retrieval deterministic.
- Avoid speculative future retrieval abstractions that do not help the MVP.
- Any engine integration should stay narrowly scoped to retrieval orchestration.
