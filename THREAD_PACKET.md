# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Current branch tip before this fixer pass: `057623be3ea8887e47c25debb4403247c4d94c9f`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet traceability note: commit `206e37e3509c1e3331b45258c6e82ab31e52a82e` is a metadata-only packet refresh that changed only `THREAD_PACKET.md`, commit `412a3f777dcb7c1bb1ddf43e64b1fbce36d45982` is the latest metadata-only scope-wording refresh before the gate-rerun note, commit `0b6ed199b752d758c8e3d71433740274efd2b62c` recorded the first passing gate rerun in `docs/gate_passed.txt`, commit `86e0f49aac171d1cfc4f461274c672233279cd64` added the explicit canonical demo-path step requested by review, commit `39b1a1d5421b2d18b5a09aaaa3f517884da82672` refreshed the packet after that reviewer-fix pass, commit `4748167a2b68834ee90f430c072a8564b9f3bd45` refreshed handoff traceability, commit `3ce9b5d10defb43c8d180a73505804858614de60` refreshed the authoritative packet, and commit `057623be3ea8887e47c25debb4403247c4d94c9f` is the latest metadata-only packet refresh before this fixer pass. This fixer pass refreshes `THREAD_PACKET.md`, keeps the authoritative re-review packet aligned to the narrowed FTS-only excerpt-contract scope, records the exact canonical demo-path mapping the reviewer asked for, and does not move the reviewed implementation head or range.

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

### Early Review Triggers

- before first edit to the shared-by-approval regression file `tests/unit/test_unified_retrieval.py`
- before changing public retrieval command or contract wording in the handoff packet
- before touching provider routing/config behavior

### Checkpoint Status

- `plan complete`: the packet remains anchored to the narrowed implementation range from the reviewer packet and this fixer pass only refreshes packet evidence.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` for this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in the reviewed range remains `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: this packet separates reviewed implementation files from metadata-only packet refresh files, states the canonical demo-path step explicitly, and refreshes traceability for the latest metadata-only reviewer-fix commit.

## Scope completed

- Canonical demo-path step advanced in this reviewed scope: `retrieve relevant material`.
- This reviewed slice advances `retrieve relevant material` by making FTS-only excerpt lookup fail closed on PageIndex-only IDs.
- This handoff is a Milestone 3 retrieval/search hardening change for the canonical engine retrieval surface.
- `fetch_excerpt()` now resolves through the authoritative FTS-only path and no longer falls back to PageIndex-backed excerpt payloads, which makes `retrieve relevant material` depend on structured FTS results only.
- Approved shared regression coverage proves PageIndex-backed excerpt IDs fail closed with `KeyError`, which keeps `retrieve relevant material` aligned to the FTS-first roadmap contract instead of silently reopening a non-FTS excerpt path.
- SQLite FTS remains the authoritative MVP retrieval path; PageIndex and embeddings remain compatibility-only, non-required paths in this slice.

## Reviewed Scope Boundary

- The reviewed implementation range is exactly the single commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` (`378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`).
- That reviewed range changes only `src/qual/retrieval/service.py` and `tests/unit/test_unified_retrieval.py`.
- The reviewer-cited broader retrieval behaviors already present in the branch, including FTS-only hit normalization and constructor expectations, provenance bundle serialization surfaces, and helper/export contract coverage, predate `378cf9a74a3658058079a32f186fcd254c4a4034` and are not claimed as new work in this handoff.
- Re-review should judge this handoff against the narrow fail-closed excerpt change above, not against older branch context that remains unchanged in the reviewed range.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff advances `retrieve relevant material` by enforcing authoritative FTS-only excerpt lookup with deterministic fail-closed behavior for non-FTS excerpt IDs before basket promotion or downstream workflow use.
- Retained change 1: the `fetch_excerpt()` implementation change advances `retrieve relevant material` by making excerpt hydration depend only on canonical FTS hits.
- Retained change 2: the shared fail-closed regressions advance `retrieve relevant material` by proving non-FTS excerpt IDs cannot silently re-enter the MVP retrieval flow.
- This packet does not claim new basket-promotion or broader provenance-surface work; any downstream value remains indirect contract hardening from the stricter excerpt lookup surface.

## Tasks completed

1. Advanced `retrieve relevant material` by removing the PageIndex fallback from `fetch_excerpt()` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Advanced `retrieve relevant material` by replacing the old shared test that normalized PageIndex excerpt payloads with a fail-closed assertion that `fetch_excerpt()` now raises `KeyError` for that path.
3. Advanced `retrieve relevant material` by adding a second approved shared regression that constructs a PageIndex-only excerpt ID via `DocIndexService` and proves the canonical retrieval surface rejects it with `KeyError`.
4. Re-emitted the handoff packet so `Scope completed`, `Tasks completed`, and the dedicated `Canonical demo-path step advanced` field all state that this `adfa8cda` reviewed range advances Milestone 3 retrieval/search by making `retrieve relevant material` more real.

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

## Fresh gate evidence for this fixer pass

- Branch head under test before this fixer commit: `057623be3ea8887e47c25debb4403247c4d94c9f`
- Gate rerun timestamp: `2026-04-23`
- `make scope-check`: passed with branch-policy skip notice for `codex/feat-retrieval-fts`
- `./quality-format.sh --check`: passed
- `./quality-lint.sh`: passed
- `./quality-test.sh`: passed, `199` tests run, `OK`
- `./typecheck-test.sh`: passed via `python3 -m compileall -q src`
- `make ci`: passed and completed the same gate sequence end-to-end

## Reviewer fix closure

1. `Scope completed` and `Tasks completed` now describe the actual `adfa8cda` reviewed implementation: the FTS-only `fetch_excerpt()` change plus the two shared fail-closed regressions.
2. The packet now explicitly distinguishes the reviewed range from older branch-context retrieval APIs and tests that the reviewer cited but that predate `378cf9a74a3658058079a32f186fcd254c4a4034`.
3. The retained changes are each mapped to the canonical demo-path step `retrieve relevant material`.
4. The shared-test approval scope is now explicit: `tests/unit/test_unified_retrieval.py` is approved only for the fail-closed excerpt regressions included in `adfa8cda`, not for unrelated broader API/export assertions that already existed in the file.
5. Packet traceability still matches git history and still separates reviewed implementation files from metadata-only packet refresh files.
6. This metadata-only fixer pass reran the required gate suite on `2026-04-23` from branch head `057623be3ea8887e47c25debb4403247c4d94c9f` before creating the new fixer commit and confirmed the all-`PASS` results listed in `Commands run with results`.
7. The mirrored `.codex` kickoff packet and lane metadata remain stale because writes under those paths are permission-blocked in this worktree, so this authoritative packet carries the corrected narrowed excerpt-only review slice for re-review.
8. `Tasks completed` now names `retrieve relevant material` on each retained implementation item so the Milestone 3 / FTS-first mapping is explicit in the numbered handoff summary, not inferred from surrounding sections.

## Risks / blockers

- Risk: `HIGH`
- Residual risk: callers holding PageIndex-generated excerpt IDs now receive `KeyError` from canonical excerpt lookup surfaces instead of a fallback payload.
- Blockers: worktree denied writes under `.codex/kickoff_packets/` and `.codex/lane_meta/`, so those mirrored metadata files remain stale even though this authoritative handoff packet is corrected.

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` because this change makes the `retrieve relevant material` step fail closed to the canonical SQLite FTS excerpt path and keeps retrieval output structured and auditable for downstream engine flows.
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Vision capability affected

- `2. Retrieval-first context handling` by enforcing canonical SQLite FTS excerpt hydration for `retrieve relevant material`
- `6. Auditable state and workflow` by making non-FTS excerpt IDs fail closed instead of silently falling back

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits in the reviewed implementation range: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval implementation file in the reviewed retrieval scope, and the approved shared change is limited to the fail-closed `fetch_excerpt()` regressions included in `adfa8cda`.
- Packet-only fixer files are handoff metadata files and do not change reviewed retrieval runtime behavior.
