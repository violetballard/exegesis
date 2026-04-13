## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet HEAD role: `metadata-only reviewer-fix refresh`
- Current branch head before this fixer commit: `00becda9e2d05badd2ed25d0073c81c24482aec8`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Handoff type: `shared/high-risk retrieval handoff with explicit canonical demo-path alignment`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## High-risk kickoff alignment
- Risk reason: approved shared regression coverage in `tests/unit/test_unified_retrieval.py` makes this shared/high-risk work under `AGENTS.md`.
- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

## Canonical demo-path step advanced
- `retrieve relevant material`
- This reviewed slice makes `retrieve relevant material` more real by keeping excerpt lookup on the canonical FTS-backed path so PageIndex-only excerpt IDs fail closed and downstream engine flows consume deterministic retrieval provenance.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in this narrowed reviewed slice.
- `RetrievalService.fetch_excerpt()` now resolves through the canonical FTS-only lookup path, so PageIndex-only excerpt IDs fail closed instead of reviving PageIndex as a required runtime path.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves canonical FTS excerpt lookup still succeeds and PageIndex-only excerpt IDs raise `KeyError`.
- PageIndex and embeddings remain deferred compatibility paths rather than required MVP retrieval strategies.

## Reviewer fix reconciliation
- Required fix 1 is satisfied by explicitly naming the canonical demo-path step advanced: `retrieve relevant material`.
- Required fix 2 is satisfied by explicitly classifying this handoff under the AGENTS.md high-risk/shared kickoff rules: approved shared coverage in `tests/unit/test_unified_retrieval.py` makes this a shared/high-risk packet reviewed against the `4`-task / `30m` template.
- Required fix 3 is satisfied by refreshing this handoff packet so roadmap alignment, budget framing, and reviewed implementation traceability read cleanly in one place for re-review.

## Approved exception note
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Tasks completed
1. Removed the PageIndex fallback from `fetch_excerpt()` so excerpt lookup stays on the canonical FTS-only path.
2. Added approved shared regression coverage proving PageIndex-only excerpt IDs fail closed with `KeyError`.
3. Refreshed the handoff packet to state the explicit canonical demo-path step advanced by this slice.
4. Normalized the handoff budget framing to shared/high-risk work under the 4-task cap for re-review.

## Files changed
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)
- `THREAD_PACKET.md`

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
- `feat-retrieval-fts`: authoritative FTS-first retrieval feeding the engine loop

## Vision capability affected
- `2. Retrieval-first context handling`
- `3. Canonical engine contract`
- `6. Auditable state and workflow`

## Routing/provider impact note
- None

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (approved `tests/unit/test_unified_retrieval.py` regression coverage only)
