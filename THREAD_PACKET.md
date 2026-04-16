# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed implementation head before final fixer commit: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in the reviewed implementation range.
- `fetch_excerpt` fails closed on the canonical FTS-only path and no longer falls back to PageIndex-only excerpt payloads.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now raise `KeyError`.
- PageIndex and embeddings remain non-required compatibility paths in this reviewed slice and are not restored as required runtime retrieval backends.
- This scope is explicitly limited to the canonical demo-path step `retrieve relevant material` and strengthens that engine-side retrieval path without expanding into alternate retrieval modes.

## Canonical Demo-Path Step Advanced
- Canonical demo-path step advanced: `retrieve relevant material`
- This reviewed implementation range makes `retrieve relevant material` more real by forcing excerpt lookup through the canonical FTS-only path and rejecting PageIndex-only excerpt IDs without expanding the lane into alternate retrieval modes.

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

### Handoff metadata files
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
- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts - authoritative FTS-first retrieval feeding the engine loop`

### Vision capability affected
- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note
- None

## Scope-check / ownership note
- Shared-by-approval edits: `YES` (Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.)
- Integrator-locked edits: `NO`

## Regression coverage note
- `tests/unit/test_unified_retrieval.py::test_fetch_excerpt_requires_an_fts_lookup_hit`
- `tests/unit/test_unified_retrieval.py::test_retrieval_service_rejects_pageindex_excerpt_payloads`

## Traceability note
- Re-review should anchor retrieval implementation scope to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- The current branch tip reported in the final fixer handoff is a metadata-only packet refresh commit unless a later regenerated packet says otherwise.
