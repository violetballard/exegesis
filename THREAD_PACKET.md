# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Current branch tip before this fixer pass: `7bd332628dddf1912710436094c2144cffa7ef21`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet traceability note: commit `206e37e3509c1e3331b45258c6e82ab31e52a82e` is a metadata-only packet refresh that changed only `THREAD_PACKET.md`, commit `412a3f777dcb7c1bb1ddf43e64b1fbce36d45982` is the latest metadata-only scope-wording refresh before the gate-rerun note, commit `0b6ed199b752d758c8e3d71433740274efd2b62c` recorded the passing gate rerun in `docs/gate_passed.txt`, commit `86e0f49aac171d1cfc4f461274c672233279cd64` added the explicit canonical demo-path step requested by review, and commit `7bd332628dddf1912710436094c2144cffa7ef21` is the latest metadata-only packet refresh before this re-review evidence pass. This fixer pass refreshes `THREAD_PACKET.md`, keeps this file as the authoritative re-review packet, records a fresh all-green gate rerun on `2026-04-23`, and does not move the reviewed implementation head or range.

## Scope goal

- Harden the canonical `fetch_excerpt()` contract so excerpt lookup stays on the canonical FTS-only path, removes the PageIndex fallback, and proves PageIndex-only excerpt IDs fail closed.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: keep retrieval/search FTS-first, deterministic, and auditable on the canonical engine surface.
- Risk reason: the reviewed implementation includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Remove the PageIndex fallback from `fetch_excerpt()` so canonical excerpt lookup is FTS-only.
2. Replace PageIndex-normalization expectations in shared retrieval tests with fail-closed `KeyError` assertions.
3. Add approved shared regression coverage proving a PageIndex-only excerpt ID cannot be fetched through the canonical retrieval surface.
4. Re-emit the authoritative handoff packet with the actual reviewed scope, the retained approval boundary, and the explicit canonical demo-path step advanced by this work.

### Checkpoint Status

- `plan complete`: the packet now anchors re-review to the narrowed implementation range from the reviewer packet.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` for this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in the reviewed range remains `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: this packet now separates reviewed implementation files from metadata-only packet refresh files, states the canonical demo-path step explicitly, and refreshes traceability for the latest metadata-only reviewer-fix commit.

## Scope completed

- `fetch_excerpt()` now resolves through the canonical FTS-only path and no longer falls back to PageIndex-backed excerpt payloads.
- Approved shared regression coverage now covers both previously indexed PageIndex excerpts and a synthetic PageIndex-only excerpt ID, and both paths fail closed with `KeyError`.
- SQLite FTS remains the authoritative MVP retrieval path; PageIndex and embeddings remain compatibility-only, non-required paths in this slice.

## Reviewed Scope Boundary

- The reviewed implementation range is exactly the single commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` (`378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`).
- That reviewed range changes only `src/qual/retrieval/service.py` and `tests/unit/test_unified_retrieval.py`.
- The reviewer-cited broader retrieval behaviors already present in the branch, including FTS-only hit normalization and constructor expectations, provenance bundle serialization surfaces, and helper/export contract coverage, predate `378cf9a74a3658058079a32f186fcd254c4a4034` and are not claimed as new work in this handoff.
- Re-review should judge this handoff against the narrow fail-closed excerpt change above, not against older branch context that remains unchanged in the reviewed range.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff advances `retrieve relevant material` by enforcing authoritative FTS-only excerpt lookup with deterministic fail-closed behavior for non-FTS excerpt IDs.
- Retained change 1: the `fetch_excerpt()` implementation change advances `retrieve relevant material` by making excerpt hydration depend only on canonical FTS hits.
- Retained change 2: the shared fail-closed regressions advance `retrieve relevant material` by proving non-FTS excerpt IDs cannot silently re-enter the MVP retrieval flow.
- This packet does not claim new basket-promotion or broader provenance-surface work; any downstream value remains indirect contract hardening from the stricter excerpt lookup surface.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt()` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Replaced the old shared test that normalized PageIndex excerpt payloads with a fail-closed assertion that `fetch_excerpt()` now raises `KeyError` for that path.
3. Added a second approved shared regression that constructs a PageIndex-only excerpt ID via `DocIndexService` and proves the canonical retrieval surface rejects it with `KeyError`.
4. Re-emitted the handoff packet so `Scope completed`, `Tasks completed`, shared-test approval, and the canonical demo-path mapping all describe the actual `adfa8cda` reviewed range.

## Files changed

- Reviewed implementation files in `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Broader retrieval APIs already present on the branch but outside this reviewed range:
  - `src/qual/retrieval/service.py` pre-existing hit/provenance helper surfaces remain branch context only and are not changed by `adfa8cda`.
  - `tests/unit/test_unified_retrieval.py` pre-existing export, provenance-bundle, and normalization assertions remain branch context only and are not changed by `adfa8cda`.
- Metadata-only packet refresh files in `206e37e3509c1e3331b45258c6e82ab31e52a82e`:
  - `THREAD_PACKET.md`
- Metadata-only reviewer-fix packet files in commit `86e0f49aac171d1cfc4f461274c672233279cd64`:
  - `THREAD_PACKET.md`
- Metadata-only packet refresh files in this fixer pass after the fresh all-green gate rerun:
  - `THREAD_PACKET.md`

## Commands run with results

- Gate rerun date: `2026-04-23`

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. `Scope completed` and `Tasks completed` now describe the actual `adfa8cda` reviewed implementation: the FTS-only `fetch_excerpt()` change plus the two shared fail-closed regressions.
2. The packet now explicitly distinguishes the reviewed range from older branch-context retrieval APIs and tests that the reviewer cited but that predate `378cf9a74a3658058079a32f186fcd254c4a4034`.
3. The retained changes are each mapped to the canonical demo-path step `retrieve relevant material`.
4. The shared-test approval scope is now explicit: `tests/unit/test_unified_retrieval.py` is approved only for the fail-closed excerpt regressions included in `adfa8cda`, not for unrelated broader API/export assertions that already existed in the file.
5. Packet traceability still matches git history and still separates reviewed implementation files from metadata-only packet refresh files.
6. This metadata-only fixer pass reran the required gate suite on `2026-04-23` and confirmed the all-`PASS` results listed in `Commands run with results`.

## Risks / blockers

- Risk: `HIGH`
- Residual risk: callers holding PageIndex-generated excerpt IDs now receive `KeyError` from canonical excerpt lookup surfaces instead of a fallback payload.
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits in the reviewed implementation range: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval implementation file in the reviewed retrieval scope, and the approved shared change is limited to the fail-closed `fetch_excerpt()` regressions included in `adfa8cda`.
- Packet-only fixer files are handoff metadata files and do not change reviewed retrieval runtime behavior.
