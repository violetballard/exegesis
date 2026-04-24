# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Scope goal: narrow `fetch_excerpt()` to canonical FTS-only excerpt resolution and add regression coverage proving PageIndex-only excerpt IDs fail closed on the public excerpt lookup path.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by making the public `fetch_excerpt` surface resolve only through the canonical SQLite FTS path, so PageIndex-only excerpt IDs fail closed on the retrieval step itself.
- Direct handoff statement: this handoff advances the canonical demo-path step `retrieve relevant material` by narrowing public excerpt resolution to the canonical FTS-only lookup path and by adding approved shared regression coverage proving PageIndex-only excerpt IDs raise `KeyError`. It does not claim basket promotion, plan/revise behavior, or broader workflow progress.
- Approved exception surface: approved shared regression coverage in `tests/unit/test_unified_retrieval.py` only; no other shared-by-approval or integrator-locked files are part of the reviewed implementation range.

## Scope Completed

- `src/qual/retrieval/service.py::fetch_excerpt()` now resolves only through the canonical SQLite FTS lookup path in the reviewed implementation range.
- `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt identifiers fail closed with `KeyError` on `fetch_excerpt()` and both retrieval facades.
- This is a narrow Milestone 3 retrieval-contract slice for `retrieve relevant material`; it does not claim basket promotion, plan/revise behavior, or full-lane completion.
- No retrieval code changed after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`; later commits are metadata-only packet refreshes.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: re-emit the retrieval handoff packet so it matches the reviewed shared/high-risk slice exactly, preserves the reviewed implementation range above, and states plainly that `fetch_excerpt` now resolves only through the canonical FTS path and fails closed for PageIndex-only excerpt IDs.
- Risk reason: the reviewed slice includes the approved shared regression edit in `tests/unit/test_unified_retrieval.py`, so the packet must follow the high-risk/shared budget class.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Reclassified the reviewed slice as shared/high-risk work with `tests/unit/test_unified_retrieval.py` as the sole approved shared exception surface.
2. Aligned the handoff on the reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. Tightened the packet language so it describes deterministic FTS excerpt retrieval for `retrieve relevant material` rather than broader workflow steps.
4. Re-emitted the canonical handoff packet with the explicit `retrieve relevant material` plan-alignment sentence and the scope-tight retrieval-only wording requested in review.

## Files Changed

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PASS` (`[devex] scope-check: passed for branch 'codex/feat-retrieval-fts'`)
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS` (`216 tests`)
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`
- Current fixer pass note: reran the full required gate set on packet-refresh head `cfc97cf83cbe90bfabc4a0a182ce04538707a662` before the verification commit below.

## Risks / Blockers

- Risk: `HIGH`
- Residual risk: callers, persisted state, or fixtures outside the narrowed reviewed implementation range may still hold PageIndex-only excerpt IDs; those IDs now fail closed with `KeyError` on the public excerpt lookup surface until they are regenerated as canonical FTS excerpt IDs.
- Checked in narrowed review range: `src/qual/retrieval/service.py` and the approved shared regression surface `tests/unit/test_unified_retrieval.py` were updated to enforce and prove the fail-closed FTS-only contract, and no additional caller migrations were required inside that reviewed slice.
- Blockers: `None`
- Budget note: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it remains shared/high-risk work under the `4`-task cap and outside the low-risk owned-path-only budget class.

## Required Handoff Fields

- Roadmap item(s) affected: `Milestone 3: Real workflow loop`, `feat-retrieval-fts` as a narrow excerpt-resolution slice rather than as lane completion
- Vision capability affected: `2. Retrieval-first context handling`, `6. Auditable state and workflow`
- Routing/provider impact note: `None`
- Canonical demo-path step advanced: `retrieve relevant material`; narrowing public excerpt resolution to the authoritative FTS-first path strengthens deterministic excerpt retrieval on that step without claiming broader workflow progress.
- Ownership/risk classification: `shared-by-approval only`; the reviewed slice includes `tests/unit/test_unified_retrieval.py` as the sole approved shared file and includes no integrator-locked edits.
- Proposed README.md patch text: `None`
