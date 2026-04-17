# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet refresh role: `reviewer-fix canonical-step correction`
- Current branch head before this fixer commit: `4ca63c1d5095b298f8e50669261eb99d6b5d8a13`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed

- The reviewed implementation range keeps SQLite FTS authoritative for this MVP lane.
- The excerpt lookup surface now stays on the canonical FTS-only path, so PageIndex-only excerpt IDs fail closed instead of promoting a non-canonical runtime fallback.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now raise `KeyError` through the canonical retrieval surface.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This reviewed slice makes that step more real by ensuring excerpt lookup resolves only through the authoritative FTS-backed path and fails closed for PageIndex-only excerpt IDs.
- The immediate downstream step it supports is `promote or gather context into the basket`, but this packet remains scoped to the retrieval step itself.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Packet / handoff files

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

- `Milestone 3: Real workflow loop` because this reviewed slice keeps the engine retrieval path FTS-first, deterministic, and auditable.
- `feat-retrieval-fts - retrieval/search` because this reviewed slice preserves the lane's authoritative excerpt lookup contract.

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

- Re-review should anchor to the reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- This packet intentionally keeps the scope narrow to the reviewer-requested implementation slice rather than broadening back into cumulative branch-summary language.
- Reviewer fix status: the canonical demo-path step is stated explicitly as `retrieve relevant material`, and the narrowed scope text is limited to the fail-closed FTS excerpt lookup slice.
- Use the final HEAD SHA reported with this fixer handoff for the post-fix branch tip.
