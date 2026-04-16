## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `cumulative retrieval feature handoff for the current branch tip`
- Packet HEAD role: `current branch-tip re-review packet`
- Packet HEAD SHA: `1a6a3d650bfb31e4559bce33f4f8c2789aa29b6c`
- Reviewed implementation head: `1a6a3d650bfb31e4559bce33f4f8c2789aa29b6c`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..1a6a3d650bfb31e4559bce33f4f8c2789aa29b6c`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- This packet now reviews the actual current branch tip instead of a narrowed metadata-only descendant claim.
- Across `d7fd5d200358287fa42a18d39e2b277463b9b69f..1a6a3d650bfb31e4559bce33f4f8c2789aa29b6c`, SQLite FTS remains the authoritative MVP retrieval path, retrieval payloads and provenance snapshots are deterministic for downstream engine flows, sparse source/context bundles rehydrate deterministically, and excerpt lookup stays on the canonical FTS-only path.
- The current tip also exports a generic `fetch_excerpt` retrieval shim through both retrieval facades while still resolving through the canonical FTS-first retrieval surface.
- This packet includes the real changed-file set present on the current branch tip, including the packet/planner support files that landed on this branch and were previously omitted by the narrowed packet.

## Canonical demo-path step advanced
- `retrieve relevant material`: this branch makes that step more real by keeping excerpt lookup and retrieval bundles deterministic on the SQLite FTS path that downstream basket promotion and workflow actions consume.

## Reviewer-required fixes addressed
1. The handoff now reviews the actual branch tip `1a6a3d650bfb31e4559bce33f4f8c2789aa29b6c` instead of claiming a metadata-only descendant of `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. The old metadata-only packet-head claim has been removed; packet head and reviewed implementation head are the same SHA in this handoff.
3. The reviewed implementation range and the branch-tip changed-file set are stated directly in this packet.
4. The canonical demo-path step is stated explicitly as `retrieve relevant material`.

## AGENTS.md handoff packet
- Risk reason: shared/high-risk work because the reviewed range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Tasks completed:
  1. Kept SQLite FTS authoritative and deterministic across retrieval result, excerpt, provenance, and payload surfaces.
  2. Hardened retrieval payload/source/provenance normalization plus sparse bundle reconstruction for downstream engine flows.
  3. Preserved the FTS-first facade surface, including the current-tip generic `fetch_excerpt` shim that still resolves through the canonical retrieval service path.
  4. Maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` and packet/planner support so the handoff traces the actual branch tip.

## Files changed in reviewed range
### Retrieval implementation and approved shared regression coverage
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
### Packet and packet-planner support files present on this branch tip
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

## Commands run with results
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
- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts - authoritative FTS-first retrieval feeding the engine loop.`

## Vision capability affected
- `Retrieval-first context handling`
- `Auditable state and workflow`

## Routing/provider impact note
- None

## Proposed README.md patch text
- None

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- The reviewed range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- The current branch tip also contains packet/planner support files; they are listed here because this handoff now describes the real branch-tip contents instead of a narrower descendant claim.
- The mirrored `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` files are present but not writable in this worktree, so `THREAD_PACKET.md` is the source-of-truth packet for this fixer pass.
