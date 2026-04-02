## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Final HEAD SHA (reviewed implementation head): `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Handoff type: branch-level cumulative full-thread retrieval handoff

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- Branch-level cumulative handoff from `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`: SQLite FTS remains authoritative, the canonical retrieval query constructor and `retrieve_auto` helper are exported through both retrieval facades, retrieval payloads/provenance/hit snapshots are deterministic enough for downstream engine flows, sparse source and context bundles rehydrate deterministically, and the excerpt lookup surface now uses the canonical FTS-only path so PageIndex-only excerpt IDs fail closed under shared regression coverage. PageIndex and embeddings remain compatibility-only fallback shims that fail closed.
- The branch contains later metadata-only packet refresh commits. The only shared-by-approval edit in the reviewed implementation range is `tests/unit/test_unified_retrieval.py`, and those later packet-refresh commits do not change that reviewed implementation range.

## Docs-only alignment commits
- `f13324d206b41c134a96ff837eea6427c31aa981`
- `edb36142cfe75ff8c65aee95865adb2de7ac19b0`
- `b172559ed0889b5793e150296fa4b8b6c9943931`
- `a164d042623b8d3fc52019c72c5be74bba18990b`
- `3cc3dc84b80a8a1983d5ab90da1ef290ac6117fe`
- `173ef4bebddcd460cbfbaf7f281ab145be9e25d8`
- `1435baa0fb0164b2972a512816fe680eb4710ee0`
- `25f2ae42256307bdd306c5216d3cfce438d30c37`
- `17177091ff7bc8231cd02a5e7bb05766c0963c50`
- `2188b405f32d8977703da90b4b560e53b99142bd`
- `194612f481860e466f4a55064999126df2f0371a`
- `93ea7d8771d6d2f6060dbdf76eb4dc7f0a2d395d`
- `5420c99a08df9bfb08f93b117b59e08fd6c86be3`
- `221c6806230a2ed3eec71c1d5ff458dd03bbdb4d`
- `be10c6b42d8aea5297c6db7da4c23ccb81185848`
- These packet-refresh commits are metadata-only and do not change the reviewed implementation range above.

## Reviewer fix reconciliation
- Required fix 1 is satisfied by the `Budget alignment` section below: this handoff is explicitly classified as shared/high-risk work with the 4-task cap.
- Required fix 2 is satisfied by separating the metadata-only packet refresh chain from the reviewed implementation range anchored to `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Required fix 3 is satisfied by the dedicated `Scope completed` section above, which states the FTS-first retrieval outcome independently of the packet-refresh commits.

## Packet trace note
- Current branch head metadata refreshes may continue after the reviewed implementation head.
- The reviewed implementation head for retrieval scope remains `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Any later packet-only commits on `codex/feat-retrieval-fts` are metadata-only follow-ups and are not part of the reviewed implementation range unless this packet is regenerated to say otherwise.

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
