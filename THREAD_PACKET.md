## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Packet HEAD role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before the fixer commit: `2918379deb41cbf327dad0891d61acda5c401393`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in the reviewed slice.
- The reviewed implementation range removes the PageIndex fallback from `fetch_excerpt`, keeping excerpt lookup on the canonical FTS-only path.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves that PageIndex-only excerpt IDs now raise `KeyError`.
- PageIndex and embeddings remain deferred compatibility identifiers, not required runtime paths for the MVP retrieval contract.
- Re-review should stay narrowed to the existing two-file implementation slice: `src/qual/retrieval/service.py` and `tests/unit/test_unified_retrieval.py`.

## Canonical demo-path step advanced
- `retrieve relevant material`: this reviewed slice explicitly advances that canonical demo-path step by forcing public excerpt lookup to resolve only through the deterministic SQLite FTS path before basket promotion.

## Reviewer-required fixes addressed
1. The handoff is classified as shared/high-risk work because the reviewed implementation slice includes the approved shared regression file `tests/unit/test_unified_retrieval.py`, so the 4-task cap applies.
2. The packet explicitly states that this work advances the canonical `retrieve relevant material` step and explains that excerpt lookup now fails closed to the canonical SQLite FTS path.
3. The reviewed implementation scope remains narrowed to the existing two-file slice and is not broadened back into cumulative branch work.
4. This handoff packet treats the reviewer packet as the source-of-truth traceability anchor for the reviewed slice.

## AGENTS.md handoff packet
- Risk reason: shared/high-risk work because the reviewed implementation range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Tasks completed:
  1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
  2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.
- Files changed in reviewed implementation:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Metadata-only files refreshed for this fixer pass:
  - `THREAD_PACKET.md`

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
- The only reviewed non-owned file in the implementation slice is the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Re-review should stay narrowed to `src/qual/retrieval/service.py` plus that approved shared test file; later metadata-only packet refresh commits do not expand the reviewed implementation range unless the packet is explicitly regenerated to do so.
