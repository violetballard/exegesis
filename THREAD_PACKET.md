## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet HEAD role: `reviewer-fix packet regeneration for the actual implementation tip`
- Current packet-refresh branch head before the final fixer commit: `226121095e4d889d79feabfb9966a84b756d5753`
- Reviewed implementation head: `226121095e4d889d79feabfb9966a84b756d5753`
- Reviewed implementation range: `bccc788cb555029e699628b2bd1549d4d283e714..226121095e4d889d79feabfb9966a84b756d5753`
- Handoff type: shared/high-risk retrieval handoff for the hardened FTS snapshot and source-bundle backfill slice
- Traceability rule: this packet is regenerated against the actual branch tip because commits `0d21c11e2a3866b6944c98240a2fe8f0678551bf` and `226121095e4d889d79feabfb9966a84b756d5753` both contain implementation changes and must remain inside the reviewed scope.
- Authoritative traceability for this re-review: current branch head before the final fixer commit is `226121095e4d889d79feabfb9966a84b756d5753`; reviewed implementation head and reviewed implementation range are intentionally aligned to that real implementation tip rather than described as metadata-only.

## Packet HEAD context
- The branch tip before this fixer commit is `226121095e4d889d79feabfb9966a84b756d5753`.
- The earlier packet trace anchor `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9` remains a metadata-only commit, but it is no longer used as the reviewed tip because later implementation commits changed retrieval behavior.
- Re-review should anchor retrieval implementation scope to `bccc788cb555029e699628b2bd1549d4d283e714..226121095e4d889d79feabfb9966a84b756d5753`, then use the final fixer handoff to identify the new branch tip created by this metadata correction commit.
- This file is the reviewer-facing source of truth for the regenerated handoff, and the `.codex` packet mirrors are refreshed alongside it in this fixer pass.

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in this reviewed slice.
- Retrieval snapshots, provenance payloads, and source bundles are hardened so sparse downstream payloads rehydrate deterministic `doc_hits`, `excerpt_hits`, and top-excerpt summary fields from canonical retrieval bundles instead of silently dropping them.
- The excerpt lookup surface stays on the canonical FTS-only path, so PageIndex-only excerpt IDs fail closed with `KeyError` under approved shared regression coverage.
- PageIndex and embeddings remain deferred compatibility strategies rather than required MVP paths.

## Traceability note
- Earlier packet refresh commits such as `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9` and `bccc788cb555029e699628b2bd1549d4d283e714` remain useful trace anchors for the handoff chain.
- The actual reviewed implementation changes for this packet are the two tip-side commits `0d21c11e2a3866b6944c98240a2fe8f0678551bf` and `226121095e4d889d79feabfb9966a84b756d5753`.
- This regenerated packet intentionally stops describing the branch tip as metadata-only.

## Reviewer fix reconciliation
- Required fix 1 is satisfied by regenerating the handoff against the actual branch tip instead of treating it as metadata-only.
- Required fix 2 is satisfied by updating the reviewed implementation range, scope summary, and file list to include the behavioral changes in `src/qual/engine/retrieval/payload.py` and its associated regression coverage.
- Required fix 3 is satisfied by removing the false metadata-only characterization from the current tip.
- Required fix 4 is satisfied by restating the roadmap and vision mapping for the sparse source-bundle backfill and snapshot-hardening work now included in scope.

## Required fixes addressed
1. Regenerated the packet against the actual implementation tip `226121095e4d889d79feabfb9966a84b756d5753`.
2. Updated `Reviewed implementation range`, `Scope completed`, and `Files changed` to include the source-bundle backfill and retrieval snapshot hardening work.
3. Removed the false claim that the current tip is metadata-only.
4. Re-stated roadmap and vision mapping so the `payload.py` normalization work is explicitly tied to Milestone 3 retrieval payload stability.

## Verification note
- The current implementation head before this fixer commit is `226121095e4d889d79feabfb9966a84b756d5753`.
- Required local gates are re-run on top of that implementation state before this handoff is refreshed.
- This fixer pass is metadata-only, but it corrects the packet to describe the real implementation tip instead of preserving the older narrowed slice.

## Packet trace note
- The packet trace anchor for the implementation under review is `226121095e4d889d79feabfb9966a84b756d5753`.
- This packet does not self-record the new fixer commit SHA because that value exists only after commit creation; use the final fixer handoff for the actual branch tip after this metadata correction lands.
- Read the file list and task summary against `bccc788cb555029e699628b2bd1549d4d283e714..226121095e4d889d79feabfb9966a84b756d5753`.

## Branch-head traceability
- Re-review should verify packet traceability against the reviewed implementation head `226121095e4d889d79feabfb9966a84b756d5753` and reviewed implementation range `bccc788cb555029e699628b2bd1549d4d283e714..226121095e4d889d79feabfb9966a84b756d5753`.
- If a later branch head changes retrieval code or the approved shared regression file, this packet must be regenerated before approval.

## Approved exception note
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Files changed

### Reviewed implementation files

These are the source files changed across the reviewed implementation range.

- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)

### Metadata-only handoff and tooling files

These files keep the branch-level handoff packet aligned. They are metadata-only alignment files outside the retrieval implementation scope and are listed separately so they are not read as lane-owned retrieval implementation changes.

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Tasks completed

1. Hardened retrieval snapshot normalization so canonical source bundles, citation bundles, and provenance payloads stay deterministic for downstream engine consumers.
2. Backfilled sparse source bundles from canonical doc and excerpt bundles so missing top-level hit lists still rehydrate stable retrieval payloads.
3. Kept `fetch_excerpt` on the FTS-only lookup path so PageIndex-only excerpt IDs fail closed with `KeyError`.
4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for snapshot hardening, sparse source-bundle backfill, and FTS-only excerpt lookup behavior.

## Budget alignment
- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap.
- The reviewed implementation range changes 7 files and remains within the high-risk file-count limit.
- The only shared-by-approval file in the reviewed range is `tests/unit/test_unified_retrieval.py`.
- No integrator-locked files were edited in the reviewed retrieval implementation.

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
- `ROADMAP.md`: `Milestone 3: Real workflow loop` by keeping retrieval structured and deterministic for basket promotion and downstream engine workflows.

## Vision capability affected
- 2. Retrieval-first context handling
- 3. Canonical engine contract
- 6. Auditable state and workflow

## Routing/provider impact note
- None

## Compatibility note
- PageIndex and embeddings remain non-required paths for this MVP. In this reviewed slice, excerpt lookup fails closed instead of falling back to PageIndex when the ID is not present in SQLite FTS, and sparse payload consumers rehydrate from canonical retrieval bundles rather than treating missing top-level hit lists as authoritative empties.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (approved `tests/unit/test_unified_retrieval.py` regression coverage only).
