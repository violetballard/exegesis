## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet HEAD role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before the final fixer commit: `4b0331ee770945443f870ba1eddf4d5df2d969e7`
- Final HEAD SHA (reviewed implementation head): `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Handoff type: branch-level cumulative full-thread retrieval handoff
- Traceability rule: later metadata-only packet refresh commits may advance the branch head, but they do not change the reviewed implementation head or reviewed implementation range unless this packet is explicitly regenerated to do so.

## Packet HEAD context
- The packet-refresh branch tip created by this fixer pass is intentionally reported in the final fixer handoff rather than hard-coded here, because this file is committed before that new SHA exists.
- The reviewer-referenced SHA `b172559ed0889b5793e150296fa4b8b6c9943931` is a metadata-only packet refresh commit, not the reviewed retrieval implementation head.
- Re-review should anchor retrieval implementation scope to `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, then use the final fixer handoff to identify the current packet-refresh branch tip.

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path. Across the reviewed implementation range, the retrieval lane exported the canonical retrieval query constructor and `retrieve_auto` helper through both facades, made payload/provenance/hit snapshots deterministic for downstream engine flows, rehydrated sparse source/context bundles deterministically, and kept excerpt lookup on the canonical FTS-only path so PageIndex-only excerpt IDs fail closed under approved shared regression coverage.
- The only shared-by-approval file in the reviewed implementation range is `tests/unit/test_unified_retrieval.py`. Later packet-refresh commits, including `b172559ed0889b5793e150296fa4b8b6c9943931`, are metadata-only and do not change that reviewed implementation range.

## Docs-only alignment commits
- Representative metadata-only packet refresh commits include `ce6967d1c32baff0d60aba1b983affcdd7524375`, `287461d4b811d01efcd9e690ccd63362b773fe6b`, `2026498d8644e5f9f4f13c68e03c68443cb045e9`, `bba460f378584ed873358ad6010a9c9f9a3b08b0`, `061eaecee61f53424555028c38ae2bf4854f57ad`, `9f26474a2264b38735726bcf4460664a4016097d`, `34a0b21ac12d1ec607deb95de7d484e041f4d42d`, `624409bac4b7805979931d9b8d0973e986580574`, and the reviewer-cited `b172559ed0889b5793e150296fa4b8b6c9943931`.
- The immediately preceding packet-refresh head for this final fixer pass is `4b0331ee770945443f870ba1eddf4d5df2d969e7`.
- Those commits update handoff metadata only and must not be read as evidence that `src/qual/retrieval/service.py` or `tests/unit/test_unified_retrieval.py` changed at those SHAs.

## Reviewer fix reconciliation
- Required fix 1 is satisfied by the `Budget alignment` section below: this handoff is explicitly classified as shared/high-risk work with the 4-task cap.
- Required fix 2 is satisfied by separating the metadata-only packet refresh chain from the reviewed implementation range anchored to `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Required fix 3 is satisfied by the dedicated `Scope completed` section above, which states the FTS-first retrieval outcome independently of the packet-refresh commits.

## Required fixes addressed
1. Reclassified the handoff as shared/high-risk work because `tests/unit/test_unified_retrieval.py` is a shared-by-approval file, and anchored the packet to the 4-task cap.
2. Separated metadata-only packet refresh commits from the reviewed retrieval implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and reviewed implementation range `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. Preserved a dedicated `Scope completed` section that summarizes the FTS-first retrieval outcome without relying on the later metadata-only packet refresh chain.

## Verification note
- The current packet-refresh head preserves the reviewed implementation range above and does not expand retrieval scope beyond that range.
- Required local gates are re-run on the packet-refresh branch head before this handoff is refreshed.
- This fixer pass is metadata-only and exists to carry the reviewer-required packet corrections forward into a fresh packet-refresh commit without moving the reviewed implementation range.
- This commit records the post-review fixer pass that re-ran all required local gates while preserving the same reviewed implementation range and updating the trace anchor from `4b0331ee770945443f870ba1eddf4d5df2d969e7`.

## Packet trace note
- The packet refresh trace anchor is `4b0331ee770945443f870ba1eddf4d5df2d969e7`; it is metadata-only and is not automatically the reviewed implementation head.
- This packet does not self-record the current branch head because doing so would become stale as soon as the fixer commit is created; use the final HEAD SHA reported with the fixer handoff for the actual branch tip.
- The reviewed implementation head for retrieval scope remains `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Metadata-only packet refresh commits after that reviewed implementation head, including `b172559ed0889b5793e150296fa4b8b6c9943931`, remain outside the reviewed implementation range unless this packet is regenerated to move the reviewed implementation head or reviewed implementation range.
- The packet-refresh head can continue to advance for handoff-only corrections without changing the reviewed implementation range.
- Read the file lists and task summary against the reviewed implementation range above, not against the later metadata-only packet refresh chain.

## Branch-head traceability
- Metadata-only packet refresh commits may continue to advance the branch head after this handoff packet is refreshed.
- Re-review should verify packet traceability against the reviewed implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and reviewed implementation range `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- If a later branch head changes retrieval code or the approved shared regression file, this packet must be regenerated before approval.

## Approved exception note
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract. No other shared-by-approval files are part of the reviewed retrieval implementation range.

## Files changed

### Reviewed implementation files

These are the source files changed across the reviewed cumulative range.

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)

### Reviewed handoff and tooling files

These files keep the cumulative branch-level handoff packet and its generator aligned.

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

## Tasks completed

1. Added FTS-only excerpt lookup support and deterministic excerpt/provenance output.
2. Canonicalized retrieval payload snapshots, provenance fingerprints, and sparse source/context rehydration for downstream engine flows.
3. Kept retrieval FTS-first, hardened FTS cache isolation, and exported the canonical retrieval query constructor and `retrieve_auto` helper through both retrieval facades while leaving PageIndex and embeddings fallback-only.
4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for normalized payload snapshots, facade exports, citation/provenance helpers, and the FTS-only excerpt backfill path.

## Budget alignment
- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap.
- The 4 tasks listed above describe the cumulative retrieval implementation thread across the branch; they are not an owned-path-only low-risk batch.
- The reviewed range includes the approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- No other shared or integrator-locked files were edited in the reviewed retrieval implementation.

## Commands run and outcomes
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks/blockers
- Risk: `HIGH`
- Blockers: none

## Roadmap item(s) affected
- `ROADMAP.md`: `Milestone 3: Real workflow loop`

## Vision capability affected
- 2. Retrieval-first context handling
- 6. Auditable state and workflow

## Routing/provider impact note
- None

## Compatibility note
- PageIndex and embeddings remain fallback-only plumbing behind the FTS-first policy for this MVP; they are not required retrieval paths.
- Constraint inputs remain mapping/dataclass-shaped, and iterable `doc_types`/`date_range` values are normalized deterministically by the public retrieval helpers.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (approved `tests/unit/test_unified_retrieval.py` regression coverage only).
