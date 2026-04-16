# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed implementation head before final handoff refresh: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `reviewer-fix handoff metadata refresh with final traceability anchor`
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

## Reviewer Fix Addressed
- Required fix satisfied: the handoff now states explicitly which canonical demo-path step this slice advances, instead of relying on roadmap and vision mapping alone.
- Re-review should evaluate this narrowed slice as advancing `retrieve relevant material`.
- Reviewer-required handoff correction satisfied here: this packet explicitly maps the slice to the canonical demo-path step `retrieve relevant material`.

## Reviewer-required fixes addressed
- Fix 1: The handoff packet now states explicitly that this slice advances the canonical demo-path step `retrieve relevant material`.
- Fix 2: The packet now names the exact approval reference for the shared regression coverage: the lane's `Approved exception note` in `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json`, which authorizes `tests/unit/test_unified_retrieval.py` as the sole shared-by-approval regression surface for this lane.
- Fix 3: The risks section now states the behavioral fail-closed contract directly and ties it to passing verification on the canonical FTS-only path.

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
- Merge risk detail: callers that still pass PageIndex-only excerpt IDs into `fetch_excerpt` now fail closed with `KeyError` by design because excerpt lookup is restricted to the canonical FTS-only path.
- Verification for canonical path: `tests/unit/test_unified_retrieval.py::test_retrieval_service_fetches_fts_excerpt_ids` and `tests/unit/test_unified_retrieval.py::test_retrieve_fts_excerpt_returns_canonical_fts_payload` continue to prove the engine-facing FTS excerpt path resolves valid excerpt IDs successfully.
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
- Shared-by-approval edits: `YES` (Approval reference: the lane `Approved exception note` recorded in `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` explicitly authorizes `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane as the sole shared-by-approval regression surface exercising the canonical retrieval contract.)
- Integrator-locked edits: `NO`

## Reviewer Fixer Note
- Reviewer packet source of truth applied here: this metadata refresh keeps the narrowed reviewed implementation range at `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, explicitly records the shared-file approval reference, and calls out the fail-closed `fetch_excerpt` contract risk for re-review.

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
- Pre-fix packet trace anchor for this metadata-only fixer pass: `a6c62cdf722baf631533e89d5a3270c00c2d6c99`
