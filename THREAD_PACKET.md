## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet HEAD role: `reviewer-fix packet refresh for the actual implementation tip`
- Current packet-refresh branch head before the final fixer commit: `712714c24f92cdfe43f21127c2de1d4ea0bd2599`
- Reviewed implementation head: `712714c24f92cdfe43f21127c2de1d4ea0bd2599`
- Reviewed implementation range: `bccc788cb555029e699628b2bd1549d4d283e714..712714c24f92cdfe43f21127c2de1d4ea0bd2599`
- Handoff type: shared/high-risk retrieval handoff regenerated against the actual implementation tip
- Traceability rule: this packet is regenerated against the real branch tip because commits `0d21c11e2a3866b6944c98240a2fe8f0678551bf`, `226121095e4d889d79feabfb9966a84b756d5753`, `2b32538cdaf7e00726607fbe11c6957de0d7d739`, `73ad9229b1a6c1d47a90a52f6a92dbc5fab0f64f`, and `91899af618c0d62461c1512db42f4466b962beb2` all contain implementation changes and remain inside the reviewed scope.
- Authoritative traceability for this re-review: current branch head before the final fixer commit is `712714c24f92cdfe43f21127c2de1d4ea0bd2599`; reviewed implementation head and reviewed implementation range are intentionally aligned to that real implementation tip rather than described as metadata-only.

## Packet HEAD context
- The branch tip before this fixer commit is `712714c24f92cdfe43f21127c2de1d4ea0bd2599`.
- The docs-only packet refresh commit inside this span is `b3d5fec4cc9c31aa2e184d4c8f6780d8f1b119c0`.
- Re-review should anchor retrieval implementation scope to `bccc788cb555029e699628b2bd1549d4d283e714..712714c24f92cdfe43f21127c2de1d4ea0bd2599`, then use the final fixer handoff to identify the new packet-refresh branch tip created by this metadata correction commit.
- This file is the reviewer-facing source of truth for the regenerated handoff, and the `.codex` packet mirrors are refreshed alongside it in this fixer pass.

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Canonical demo-path step advanced
- `retrieve relevant material`
- This reviewed slice makes that step more real by keeping SQLite FTS authoritative while improving ranking with section hints, preserving title hints on canonical excerpt lookups, normalizing date-range ordering for deterministic filtering, and ensuring downstream retrieval payloads rehydrate deterministic hits and provenance.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in this reviewed slice.
- Retrieval snapshots, citation payloads, provenance payloads, and source bundles are hardened so sparse downstream payloads rehydrate deterministic `doc_hits`, `excerpt_hits`, and top-excerpt summary fields from canonical retrieval bundles instead of silently dropping them.
- The excerpt lookup surface stays on the canonical FTS-only path, so PageIndex-only excerpt IDs fail closed with `KeyError`, while canonical excerpt lookups preserve stable title hints for downstream consumers.
- FTS ranking now honors section hints without introducing alternate required retrieval modes.
- Retrieval constraints now normalize reversed ISO-like date ranges so filtering and provenance stay deterministic even when callers supply end-before-start inputs.
- PageIndex and embeddings remain deferred compatibility strategies rather than required MVP paths.

## Traceability note
- Earlier packet refresh commits such as `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9` and `bccc788cb555029e699628b2bd1549d4d283e714` remain useful trace anchors for the handoff chain.
- The actual reviewed implementation changes for this packet are the six implementation commits `0d21c11e2a3866b6944c98240a2fe8f0678551bf`, `226121095e4d889d79feabfb9966a84b756d5753`, `2b32538cdaf7e00726607fbe11c6957de0d7d739`, `73ad9229b1a6c1d47a90a52f6a92dbc5fab0f64f`, `91899af618c0d62461c1512db42f4466b962beb2`, and `712714c24f92cdfe43f21127c2de1d4ea0bd2599`.
- The docs-only alignment commit in that range is `b3d5fec4cc9c31aa2e184d4c8f6780d8f1b119c0`.
- This regenerated packet stops describing the implementation tip as metadata-only.

## Reviewer fix reconciliation
- Required fix 1 is satisfied by regenerating the handoff against the actual branch tip instead of treating a later implementation commit as metadata-only.
- Required fix 2 is satisfied by updating the reviewed implementation range, scope summary, file list, tasks, and risk to include the retrieval payload, ranking, excerpt-lookup, and date-range normalization behavior now present at the real branch tip.
- Required fix 3 is satisfied by tightening scope to the canonical demo-path step `retrieve relevant material` and explaining how the post-`adfa8c...` retrieval work directly advances the Milestone 3 FTS-first retrieval lane.
- Required fix 4 is satisfied by adding the explicit AGENTS-required canonical demo-path step statement.

## Required fixes addressed
1. Regenerated the packet against the actual implementation tip `91899af618c0d62461c1512db42f4466b962beb2`.
2. Updated `Reviewed implementation range`, `Scope completed`, `Files changed`, `Tasks completed`, and `Risk` to include the real retrieval behavior changes now on branch.
3. Tightened scope explicitly to the canonical demo-path step `retrieve relevant material` and tied the later retrieval changes to the Milestone 3 FTS-first retrieval contract.
4. Added the missing AGENTS-required statement naming the canonical demo-path step made more real by this handoff.

## Verification note
- The current implementation head before this fixer commit is `712714c24f92cdfe43f21127c2de1d4ea0bd2599`.
- Required local gates are re-run on top of that implementation state before this handoff is refreshed.
- This fixer pass is metadata-only, but it corrects the packet to describe the real implementation tip instead of preserving the stale narrowed slice.

## Packet trace note
- The packet trace anchor for the implementation under review is `712714c24f92cdfe43f21127c2de1d4ea0bd2599`.
- This packet does not self-record the new fixer commit SHA because that value exists only after commit creation; use the final fixer handoff for the actual branch tip after this metadata correction lands.
- Read the file list and task summary against `bccc788cb555029e699628b2bd1549d4d283e714..712714c24f92cdfe43f21127c2de1d4ea0bd2599`.

## Branch-head traceability
- Re-review should verify packet traceability against the reviewed implementation head `712714c24f92cdfe43f21127c2de1d4ea0bd2599` and reviewed implementation range `bccc788cb555029e699628b2bd1549d4d283e714..712714c24f92cdfe43f21127c2de1d4ea0bd2599`.
- If a later branch head changes retrieval code or the approved shared regression file, this packet must be regenerated before approval.

## Approved exception note
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Files changed

### Reviewed implementation files

These are the files changed across the reviewed implementation range.

- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)

### Metadata-only handoff files

These files keep the branch-level handoff packet aligned and are outside the retrieval implementation scope.

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Tasks completed

1. Hardened retrieval snapshot, source-bundle, and citation payload normalization so canonical retrieval bundles rehydrate deterministic downstream state.
2. Kept excerpt lookup on the canonical FTS-only path, including stable title-hint preservation on canonical excerpt payloads.
3. Honored section hints in SQLite FTS ranking and normalized retrieval date-range ordering while keeping FTS authoritative for the MVP retrieval path.
4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for snapshot hardening, source/citation backfills, FTS-only excerpt lookup behavior, section-hint ranking, and title-hint preservation.

## Budget alignment
- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap.
- The reviewed implementation range changes 7 retrieval files plus this packet file, and the only shared-by-approval implementation file in the reviewed range is `tests/unit/test_unified_retrieval.py`.
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
- `ROADMAP.md`: `Milestone 3: Real workflow loop` by keeping retrieval structured, deterministic, and FTS-first for the engine loop.

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
