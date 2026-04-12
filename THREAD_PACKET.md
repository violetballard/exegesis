## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet HEAD role: `metadata-only reviewer-fix finalization`
- Current packet-refresh branch head before the final fixer commit: `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Handoff type: narrowed shared/high-risk retrieval handoff for the FTS-only excerpt lookup slice
- Traceability rule: later metadata-only packet refresh commits may advance the branch head, but they do not change the reviewed implementation head or reviewed implementation range unless this packet is explicitly regenerated to do so.
- Authoritative traceability for this re-review: current packet-refresh commit before the final fixer commit is `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9`; reviewed implementation head remains `adfa8cdadd43747ffbcb612e4151e262b13e52ca`; reviewed implementation range remains `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`; metadata-only packet commits and handoff/tooling files are outside approved retrieval feature scope unless explicitly stated.

## Packet HEAD context
- The packet-refresh branch tip created by this fixer pass is intentionally reported in the final fixer handoff rather than hard-coded here, because this file is committed before that new SHA exists.
- The reviewer-referenced SHA `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9` is a metadata-only packet refresh commit, not the reviewed retrieval implementation head.
- Re-review should anchor retrieval implementation scope to `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, then use the final fixer handoff to identify the current packet-refresh branch tip.
- This file is the reviewer-facing source of truth for the narrowed handoff slice, and the `.codex` packet mirrors are refreshed alongside it in this fixer pass.

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in this narrowed slice. The reviewed implementation commit makes excerpt lookup fail closed on the canonical FTS-only path by removing the PageIndex fallback from `fetch_excerpt`, while keeping approved shared regression coverage in `tests/unit/test_unified_retrieval.py` to prove PageIndex-only excerpt IDs now raise `KeyError`.
- PageIndex and embeddings remain non-required compatibility paths in this slice; excerpt lookup no longer promotes PageIndex as a runtime fallback path for the MVP contract.
- This re-review deliberately narrows scope from the earlier over-budget cumulative branch summary to the single implementation commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, which stays within the high-risk size budget for shared-file work.

## Docs-only alignment commits
- Representative metadata-only packet refresh commits include `ce6967d1c32baff0d60aba1b983affcdd7524375`, `287461d4b811d01efcd9e690ccd63362b773fe6b`, `2026498d8644e5f9f4f13c68e03c68443cb045e9`, `bba460f378584ed873358ad6010a9c9f9a3b08b0`, `061eaecee61f53424555028c38ae2bf4854f57ad`, `9f26474a2264b38735726bcf4460664a4016097d`, `34a0b21ac12d1ec607deb95de7d484e041f4d42d`, `624409bac4b7805979931d9b8d0973e986580574`, and the current reviewer-cited `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9`.
- The immediately preceding packet-refresh head for this final fixer pass is `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9`.
- Those commits update handoff metadata only and must not be read as evidence that `src/qual/retrieval/service.py` or `tests/unit/test_unified_retrieval.py` changed at those SHAs.

## Reviewer fix reconciliation
- Required fix 1 is satisfied by the `Budget alignment` section below: this handoff is explicitly classified as shared/high-risk work with the 4-task cap.
- Required fix 2 is satisfied by separating the metadata-only packet refresh chain from the single reviewed code commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and its implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Required fix 3 is satisfied by narrowing the re-review scope to the single implementation commit that fits the high-risk size budget, rather than asking for unsupported over-budget approval.
- Required fix 4 is satisfied by the exact file list below, which matches the narrowed implementation slice and keeps metadata-only files separate.
- Required fix 5 is satisfied by the dedicated `Scope completed` section above, which states the FTS-first excerpt behavior and confirms PageIndex/embeddings remain non-required paths.

## Required fixes addressed
1. Reclassified the handoff as shared/high-risk work because `tests/unit/test_unified_retrieval.py` is a shared-by-approval file, and anchored the packet to the 4-task cap.
2. Separated metadata-only packet refresh commits from the reviewed retrieval implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and narrowed the reviewed implementation range to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. Tightened the re-review to the single FTS-only excerpt lookup commit so the reviewed slice fits the high-risk AGENTS size budget.
4. Corrected `Files changed` to match the narrowed reviewed implementation exactly and kept metadata-only handoff files separate.
5. Preserved a dedicated `Scope completed` section that summarizes the FTS-first excerpt behavior without relying on later metadata-only packet refreshes.

## Verification note
- The current packet-refresh head preserves the reviewed implementation range above and does not expand retrieval scope beyond that range.
- Required local gates are re-run on the packet-refresh branch head `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9` before this handoff is refreshed.
- This fixer pass is metadata-only and exists to carry the reviewer-required packet corrections forward into a fresh packet-refresh commit without moving the reviewed implementation range.
- This commit records the post-review fixer pass that re-ran all required local gates while preserving the same reviewed implementation range and updating the trace anchor from `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9`.

## Packet trace note
- The packet refresh trace anchor is `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9`; it is metadata-only and is not automatically the reviewed implementation head.
- This packet does not self-record the current branch head because doing so would become stale as soon as the fixer commit is created; use the final HEAD SHA reported with the fixer handoff for the actual branch tip.
- The reviewed implementation head for retrieval scope remains `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Metadata-only packet refresh commits after that reviewed implementation head, including `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9`, remain outside the reviewed implementation range unless this packet is regenerated to move the reviewed implementation head or reviewed implementation range.
- The packet-refresh head can continue to advance for handoff-only corrections without changing the reviewed implementation range.
- Read the file lists and task summary against the reviewed implementation range above, not against the later metadata-only packet refresh chain.

## Branch-head traceability
- Metadata-only packet refresh commits may continue to advance the branch head after this handoff packet is refreshed.
- Re-review should verify packet traceability against the reviewed implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- If a later branch head changes retrieval code or the approved shared regression file, this packet must be regenerated before approval.

## Approved exception note
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract. No other shared-by-approval files are part of the reviewed retrieval implementation range.

## Files changed

### Reviewed implementation files

These are the source files changed across the narrowed reviewed implementation range.

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)

### Metadata-only handoff and tooling files

These files keep the cumulative branch-level handoff packet and its generator aligned. They are metadata-only alignment files outside the approved retrieval feature scope and are listed separately so they are not read as lane-owned retrieval implementation changes.

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Budget alignment
- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap.
- The narrowed reviewed slice changes 2 files with 59 lines touched in `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, which fits the shared/high-risk size budget.
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
- PageIndex and embeddings remain non-required paths for this MVP. In this narrowed slice, excerpt lookup now fails closed instead of falling back to PageIndex when the ID is not present in SQLite FTS.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (approved `tests/unit/test_unified_retrieval.py` regression coverage only).
