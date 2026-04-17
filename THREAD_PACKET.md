# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh role: `reviewer-fix handoff metadata refresh`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path in this narrowed reviewed implementation range.
- The reviewed implementation commit removes the PageIndex fallback from `fetch_excerpt`, so the public excerpt lookup surface now resolves through the canonical FTS-only path.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs fail closed with `KeyError`.
- PageIndex and embeddings remain compatibility-only paths in this slice and are not restored as required runtime retrieval backends.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This slice advances `retrieve relevant material` by ensuring excerpt lookup only resolves through the authoritative SQLite FTS path and rejects PageIndex-only excerpt IDs, keeping retrieval provenance deterministic for downstream basket and workflow use.

## AGENTS.md handoff packet

- Risk reason: shared/high-risk work because this narrowed reviewed implementation includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`
- Tasks completed:
  1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
  2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / blockers

- Risk: `HIGH`
- Merge risk detail: callers that still pass PageIndex-only excerpt IDs into `fetch_excerpt` now fail closed with `KeyError` by design because excerpt lookup is restricted to the canonical FTS-only path.
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

- Shared-by-approval edits: `YES`
- Approved shared regression surface: `tests/unit/test_unified_retrieval.py`
- Integrator-locked edits: `NO`

## Traceability note

- Later metadata-only packet refresh commits may advance the branch head, but they do not change the reviewed implementation range unless the packet is explicitly regenerated.
- Reviewer-fix rerun date: `2026-04-16`; this metadata-only fixer pass revalidated the narrowed packet against the required gate set without changing runtime retrieval code.
