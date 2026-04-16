# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed implementation head before final handoff refresh: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `reviewer-fix handoff metadata refresh`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in this narrowed reviewed implementation range.
- The reviewed implementation commit removes the PageIndex fallback from `fetch_excerpt`, so the public excerpt lookup surface now resolves through the canonical FTS-only path.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs fail closed with `KeyError`.
- PageIndex and embeddings remain compatibility-only paths in this slice and are not restored as required runtime retrieval backends.

## Canonical Demo-Path Step Advanced
- Canonical demo-path step advanced: `retrieve relevant material`
- This reviewed implementation range makes `retrieve relevant material` more real by keeping retrieval output deterministic and auditable while forcing excerpt lookup through the canonical FTS-only path.
- Concretely, `src/qual/retrieval/service.py` now resolves `fetch_excerpt` through the canonical FTS-only lookup path, and the approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs fail closed with `KeyError`.
- This metadata-only fixer refresh exists to keep that canonical demo-path mapping explicit in the handoff packet for re-review.

## Reviewer-required fixes addressed
- Fix 1: The handoff packet now states explicitly that this slice advances the canonical demo-path step `retrieve relevant material`.
- Fix 2: The packet remains narrowed to the reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`; this metadata-only refresh does not change executable retrieval code.

## AGENTS.md Handoff Packet
- Risk reason: shared/high-risk work because this narrowed reviewed implementation includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
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
- The reviewed implementation range ends at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, and later packet-refresh commits remain metadata-only unless this handoff is regenerated.
- The current branch tip reported in the final fixer handoff is a metadata-only packet refresh commit.
- No post-reviewed commit changes executable code outside the retrieval lane.
- This packet refresh exists specifically to satisfy the reviewer-required handoff correction for explicit canonical demo-path mapping.
- Re-review should treat the canonical demo-path mapping above as the explicit `AGENTS.md` handoff answer for this narrowed retrieval slice.
- Fixer refresh date: `2026-04-16`
