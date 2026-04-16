# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Reviewed implementation commit: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh commit before this fixer pass: `6c9d5a40c6eb999e4ecb2e00c4a74f4822e98581`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in this narrowed slice.
- The reviewed implementation commit makes excerpt lookup fail closed on the canonical FTS-only path by removing the PageIndex fallback from `fetch_excerpt`.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now raise `KeyError`.
- PageIndex and embeddings remain non-required compatibility paths in this slice; excerpt lookup no longer promotes PageIndex as a runtime fallback path for the MVP contract.

## Canonical Demo-Path Step Advanced
- Canonical demo-path step advanced: `retrieve relevant material`
- The fail-closed FTS-only `fetch_excerpt` path makes retrieval output more deterministic and auditable for basket promotion and downstream workflow cards in Milestone 3.

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

## Roadmap item(s) affected
- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts - authoritative FTS-first retrieval feeding the engine loop`

## Vision capability affected
- `Retrieval-first context handling`
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
- The current branch tip for the reviewer packet is the metadata-only refresh commit `6c9d5a40c6eb999e4ecb2e00c4a74f4822e98581`.
- Review and re-review should anchor retrieval implementation scope to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Later packet-refresh commits remain metadata-only unless this handoff is explicitly regenerated.
