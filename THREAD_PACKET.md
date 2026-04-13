## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet HEAD role: `reviewer-fix metadata refresh`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Handoff type: `shared/high-risk retrieval handoff`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Canonical demo-path step advanced
- `retrieve relevant material`
- This reviewed slice makes `retrieve relevant material` more real by making excerpt lookup fail closed on the canonical FTS-only path consumed by downstream engine flows.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in this reviewed slice.
- `src/qual/retrieval/service.py` removes the PageIndex fallback from `fetch_excerpt()`, so PageIndex-only excerpt IDs are no longer treated as a required runtime path.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves canonical FTS excerpt lookup still succeeds and PageIndex-only excerpt IDs now raise `KeyError`.

## Approved exception note
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Files changed
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `THREAD_PACKET.md`

## Tasks completed
1. Removed the PageIndex fallback from `fetch_excerpt()` so excerpt lookup resolves through the canonical FTS-only path.
2. Added approved shared regression coverage proving PageIndex-only excerpt IDs fail closed with `KeyError`.
3. Regenerated the handoff metadata with the explicit canonical demo-path step required by `AGENTS.md`.
4. Normalized the packet budget/risk framing so the reviewed slice is consistently treated as shared/high-risk work.

## Budget alignment
- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap.
- The reviewed implementation slice stays within lane-owned retrieval paths plus the approved shared regression file.
- No integrator-locked files were edited.

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
- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts` authoritative FTS-first retrieval feeding the engine loop

## Vision capability affected
- `Retrieval-first context handling`
- `Canonical engine contract`
- `Auditable state and workflow`

## Routing/provider impact note
- None

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (approved `tests/unit/test_unified_retrieval.py` regression coverage only)
