## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet refresh trace anchor: `60cc770ad9258f34f3625f3d8d9b26028c609390`
- Latest packet-refresh HEAD SHA before this fixer pass: `60cc770ad9258f34f3625f3d8d9b26028c609390`
- Reviewed implementation HEAD SHA: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Handoff type: branch-level cumulative full-thread retrieval handoff
- Traceability rule: later metadata-only packet refresh commits may advance the branch head, but they do not change the reviewed implementation head or reviewed implementation range unless this packet is explicitly regenerated to do so.

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- Branch-level cumulative handoff from `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`: SQLite FTS remains authoritative, the canonical retrieval query constructor and `retrieve_auto` helper are exported through both retrieval facades, retrieval payloads/provenance/hit snapshots are deterministic enough for downstream engine flows, sparse source and context bundles rehydrate deterministically, and the excerpt lookup surface now uses the canonical FTS-only path so PageIndex-only excerpt IDs fail closed under shared regression coverage. PageIndex and embeddings remain compatibility-only fallback shims that fail closed.
- The branch contains later metadata-only packet refresh commits. The only shared-by-approval edit in the reviewed implementation range is `tests/unit/test_unified_retrieval.py`, and those later packet-refresh commits, including `b172559ed0889b5793e150296fa4b8b6c9943931`, do not change that reviewed implementation range.

## Docs-only alignment commits
- Representative metadata-only packet refresh commits include `f13324d206b41c134a96ff837eea6427c31aa981`, `b172559ed0889b5793e150296fa4b8b6c9943931`, `a54d1824912cc75305acc7e96ad5ff2414d8001f`, `6b3a5ea6594c86584ff45b278b2ea220b7fdd4b0`, `20440c427b5ace39e78d8a421ba65cf51078bb3b`, `9f7206fff61ca5738c5fb751ebc551fe43f6cdba`, `2efda180cdfdaf6b347aec8f8c95179ddb0c0a12`, `77a66517457c9800649a4046b2d3e857ddbfd440`, `5665fb9f4f460918cdd33f1d914d5e7f948ba0c8`, `646582c8495e1b891ee0eedab939a22e2d19d694`, `e1b75e1e720d156d5f9fe6949ece93f19f9db798`, `ab88c80e0ebf18848839e98729c3bae5b0eca94b`, `c0edeec541d7a9b03d59b80ff8e98d08081cbdf7`, and `0a78066da152d81faa52b7b8214a439830ea64bf`.
- The latest packet-only traceability refresh before this fixer pass is `60cc770ad9258f34f3625f3d8d9b26028c609390`.
- Later packet-refresh commits on this branch remain metadata-only unless this handoff packet is regenerated to move the reviewed implementation head or reviewed implementation range.
- Those packet-refresh commits update handoff metadata only and must not be read as evidence that `src/qual/retrieval/service.py` or `tests/unit/test_unified_retrieval.py` changed at those SHAs.

## Reviewer fix reconciliation
- Required fix 1 is satisfied by the `Budget alignment` section below: this handoff is explicitly classified as shared/high-risk work with the 4-task cap.
- Required fix 2 is satisfied by separating the metadata-only packet refresh chain from the reviewed implementation range anchored to `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Required fix 3 is satisfied by the dedicated `Scope completed` section above, which states the FTS-first retrieval outcome independently of the packet-refresh commits.

## Verification note
- The current packet-refresh head preserves the reviewed implementation range above and does not expand retrieval scope beyond that range.
- Required local gates were re-run on the packet-refresh branch head before this handoff was refreshed.
- This fixer pass is metadata-only and exists to give the reviewer-required packet corrections their own packet-refresh commit without moving the reviewed implementation range.

## Packet trace note
- The packet refresh trace anchor is `60cc770ad9258f34f3625f3d8d9b26028c609390`; it is metadata-only and is not automatically the reviewed implementation head.
- The latest packet-refresh branch head before this fixer pass is `60cc770ad9258f34f3625f3d8d9b26028c609390`.
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
