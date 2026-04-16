# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Reviewed implementation head: `4a4c4fc2d7749405647490f0b0301b6330feee99`
- Prior rejected packet refresh commit: `6c9d5a40c6eb999e4ecb2e00c4a74f4822e98581`
- Packet refresh role: `reviewer-required branch-tip scope regeneration`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..4a4c4fc2d7749405647490f0b0301b6330feee99`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in this reviewed branch-tip range.
- Retrieval payloads, provenance snapshots, sparse source/context rehydration, and basket-promotion backfills stay deterministic for downstream engine flows.
- The excerpt lookup surface now fails closed on the canonical FTS-only path, and the branch-tip export in `src/qual/engine/retrieval/__init__.py` exposes `fetch_excerpt` through the engine retrieval facade as part of that canonical contract.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` covers the deterministic payload/backfill behavior, the FTS-only excerpt path, and the `fetch_excerpt` facade export.
- PageIndex and embeddings remain non-required compatibility paths in this reviewed range and are not restored as required runtime retrieval paths.

## Canonical Demo-Path Step Advanced
- Canonical demo-path step advanced: `retrieve relevant material`
- The reviewed range makes retrieval output more deterministic and auditable for basket promotion and downstream workflow cards in Milestone 3, including branch-tip access to the canonical `fetch_excerpt` lookup surface through the engine facade.

## AGENTS.md Handoff Packet
- Risk reason: shared/high-risk work because the reviewed implementation includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`
- Tasks completed:
  1. Canonicalized retrieval payload, provenance, and sparse source/context snapshots so downstream engine consumers get deterministic retrieval state.
  2. Hardened FTS-first retrieval behavior, shortlist/cache normalization, and basket-promotion backfills while leaving PageIndex and embeddings as compatibility-only fallback paths.
  3. Removed the PageIndex fallback from `fetch_excerpt`, added the generic `fetch_excerpt` helper to both retrieval facades, and kept excerpt lookup on the canonical FTS-only path.
  4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for deterministic payload rebuilding, bundle backfills, facade exports, and fail-closed FTS-only excerpt lookup.

## Files changed
### Reviewed implementation files
- `src/qual/retrieval/service.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `tests/unit/test_unified_retrieval.py`

### Packet/tooling files changed in the same reviewed range
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

## Risks / blockers
- Risk: `HIGH`
- Blockers: none

## Roadmap item(s) affected
- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts - authoritative FTS-first retrieval feeding the engine loop`

## Vision capability affected
- `Retrieval-first context handling`
- `Canonical engine contract`
- `Auditable state and workflow`

## Routing/provider impact note
- None

## Proposed README.md patch text
- None

## Scope-check / ownership note
- Shared-by-approval edits: `YES`
- Integrator-locked edits: `NO`
- Approved shared exception: `tests/unit/test_unified_retrieval.py`

## Traceability note
- This packet is regenerated because reviewer feedback correctly identified that branch tip `4a4c4fc2d7749405647490f0b0301b6330feee99` is real implementation work, not metadata-only refresh.
- Re-review should anchor retrieval implementation scope to `378cf9a74a3658058079a32f186fcd254c4a4034..4a4c4fc2d7749405647490f0b0301b6330feee99`.
- The tracked `.codex` mirror packet files are present in the reviewed range but are not writable in this sandboxed worktree; `THREAD_PACKET.md` is the authoritative packet refresh for this fixer pass.
- The packet-only fixer commit created after this edit does not change runtime scope; the final HEAD SHA for that commit is reported in the fixer handoff.
