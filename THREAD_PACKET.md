# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Commit: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh commit: `69c8180f1903b2c5449bd391a8bd0a6e3b9c4f41`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in this narrowed reviewed implementation range.
- The reviewed implementation commit makes excerpt lookup fail closed on the canonical FTS-only path by removing the PageIndex fallback from `fetch_excerpt`.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now raise `KeyError`.
- PageIndex and embeddings remain non-required compatibility paths in this narrowed reviewed range and are not restored as required runtime retrieval paths.

## Canonical Demo-Path Step Advanced
- Canonical demo-path step advanced: `retrieve relevant material`
- This narrowed reviewed implementation range makes `retrieve relevant material` more real by making excerpt lookup fail closed unless the excerpt is backed by the canonical SQLite FTS path, which keeps retrieval structured, deterministic, and auditable for downstream basket and workflow use.

## AGENTS.md Handoff Packet
- Risk reason: shared/high-risk work because the reviewed implementation includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`
- Tasks completed:
  1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
  2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed
### Reviewed implementation files
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Metadata-only handoff files
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

## Required handoff fields
### Roadmap item(s) affected
- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts - authoritative FTS-first retrieval feeding the engine loop`

### Vision capability affected
- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note
- None

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`

## Traceability note
- This packet refresh stays metadata-only and does not move the reviewed retrieval implementation head.
- Re-review should anchor retrieval implementation scope to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- The packet-only fixer commit created after this edit does not change runtime scope; the final HEAD SHA for that commit is reported in the fixer handoff.
