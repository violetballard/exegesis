# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Current branch head before this fixer commit: `778eb5db8d5623d58a12051794ef720cb23ebd3a`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path in this narrowed slice.
- The reviewed implementation removes the PageIndex fallback from `fetch_excerpt`, so excerpt lookup now fails closed on the canonical FTS-only path.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt ids now raise `KeyError`.
- PageIndex and embeddings remain deferred, non-required compatibility paths in this slice rather than required runtime retrieval paths.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves only through the canonical FTS-backed lookup path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt ids fail closed with `KeyError`.

## Files changed

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `.codex/kickoff_packets/feat-retrieval-fts.md`
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
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` by keeping retrieval/search FTS-first and structured for the engine loop.
- `feat-retrieval-fts` by preserving the authoritative FTS-first retrieval path feeding the engine loop.

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Canonical demo-path step advanced

- `retrieve relevant material`
- Explicit AGENTS mapping: this narrowed slice makes the canonical `retrieve relevant material` step more real by forcing excerpt lookup through the FTS-backed contract and failing closed instead of accepting PageIndex-only excerpt ids.

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file in the reviewed implementation range.
- Metadata-only packet refresh edits do not expand the reviewed implementation range beyond `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
