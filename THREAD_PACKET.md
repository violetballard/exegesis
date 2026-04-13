## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet HEAD role: `metadata-only reviewer-fix finalization`
- Current packet-refresh branch head before the final fixer commit: `b008fe29758f55182ad0a704d26e8490605c5dbb`
- Reviewed implementation head: `712714c24f92cdfe43f21127c2de1d4ea0bd2599`
- Reviewed implementation range: `bccc788cb555029e699628b2bd1549d4d283e714..712714c24f92cdfe43f21127c2de1d4ea0bd2599`
- Handoff type: shared/high-risk retrieval handoff regenerated against the actual implementation tip
- Traceability rule: later metadata-only packet refresh commits may advance the branch head, but they do not change the reviewed implementation head or reviewed implementation range unless this packet is explicitly regenerated.

## Packet HEAD context
- The branch tip before this fixer commit is `b008fe29758f55182ad0a704d26e8490605c5dbb`.
- The latest reviewed implementation commit remains `712714c24f92cdfe43f21127c2de1d4ea0bd2599`.
- The metadata-only packet refresh commits inside this handoff chain are `b3d5fec4cc9c31aa2e184d4c8f6780d8f1b119c0` and `b008fe29758f55182ad0a704d26e8490605c5dbb`.
- Re-review should anchor retrieval implementation scope to `bccc788cb555029e699628b2bd1549d4d283e714..712714c24f92cdfe43f21127c2de1d4ea0bd2599`, then use the final fixer handoff for the new packet-refresh branch tip created by this commit.

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Canonical demo-path step advanced
- `retrieve relevant material`
- This reviewed slice makes that step more real by keeping SQLite FTS authoritative while hardening deterministic downstream retrieval payloads, keeping excerpt lookup on the canonical FTS-only path, honoring section hints in FTS ranking, preserving title hints on excerpt lookup, and normalizing reversed date ranges for deterministic filtering.

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
- The docs-only alignment commits inside that reviewed span are `b3d5fec4cc9c31aa2e184d4c8f6780d8f1b119c0` and `b008fe29758f55182ad0a704d26e8490605c5dbb`.

## Reviewer fix reconciliation
- Required fix 1 is satisfied by making every packet file anchor to the same reviewed implementation head `712714c24f92cdfe43f21127c2de1d4ea0bd2599` and reviewed implementation range `bccc788cb555029e699628b2bd1549d4d283e714..712714c24f92cdfe43f21127c2de1d4ea0bd2599`.
- Required fix 2 is satisfied by limiting the metadata-only handoff file list to the actual packet files edited in this fixer pass.
- Required fix 3 is satisfied by naming the AGENTS-required canonical demo-path step `retrieve relevant material`.
- Required fix 4 is satisfied by keeping scope explicit to Milestone 3 FTS-first retrieval work and tying the included post-`adfa8c...` retrieval changes directly to that engine demo path.

## Required fixes addressed
1. Regenerated the handoff metadata so the reviewed implementation head/range is authoritative and consistent across packet files.
2. Reconciled the metadata-only handoff files with the actual packet files edited in this fixer pass.
3. Added the explicit AGENTS-required canonical demo-path step advanced by this lane.
4. Kept scope tightened to Milestone 3 / FTS-first retrieval and explained how the included post-`adfa8c...` changes still directly advance the canonical engine retrieval step.

## Verification note
- The current implementation head before this fixer commit is `712714c24f92cdfe43f21127c2de1d4ea0bd2599`.
- Required local gates are re-run on top of the current packet-refresh branch head before this handoff is finalized.
- This fixer pass is metadata-only and does not change the reviewed implementation range.

## Packet trace note
- The packet trace anchor before this fixer commit is `b008fe29758f55182ad0a704d26e8490605c5dbb`.
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

These are the packet files edited in this fixer pass.

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
- The reviewed implementation range changes 7 retrieval files, and the only shared-by-approval implementation file in the reviewed range is `tests/unit/test_unified_retrieval.py`.
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
