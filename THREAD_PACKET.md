# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix handoff refresh`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Scope goal: keep retrieval FTS-first by narrowing `fetch_excerpt()` to canonical FTS-only excerpt resolution and preserving approved shared regression coverage proving PageIndex-only excerpt IDs fail closed on the public excerpt lookup path.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by making the public `fetch_excerpt` surface resolve only through the canonical SQLite FTS path, so PageIndex-only excerpt IDs fail closed on the retrieval step itself.
- Direct handoff statement: this handoff advances the canonical demo-path step `retrieve relevant material` by narrowing public excerpt resolution to the canonical FTS-only lookup path and by keeping approved shared regression coverage proving PageIndex-only excerpt IDs raise `KeyError`. That FTS-only `fetch_excerpt` contract makes downstream basket promotion and workflow consumers more reliable because excerpt lookup now fails closed before non-canonical PageIndex-only IDs can leak past retrieval. It does not promote PageIndex or embeddings to required runtime paths, and it does not claim basket promotion, plan/revise behavior, or broader workflow progress.
- Approved exception surface: one approved shared test edit in `tests/unit/test_unified_retrieval.py` only; no integrator-locked files and no other shared-by-approval files are part of the reviewed implementation slice.

## Scope Completed

- `src/qual/retrieval/service.py::fetch_excerpt()` now resolves only through the canonical SQLite FTS lookup path in the reviewed implementation range.
- `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt identifiers fail closed with `KeyError` on `fetch_excerpt()`.
- This is a narrow Milestone 3 retrieval-contract slice for `retrieve relevant material`; it does not claim basket promotion, plan/revise behavior, or full-lane completion.
- The reviewed implementation slice remains fixed at `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: re-emit the retrieval handoff metadata so it truthfully classifies the reviewed slice as shared/high-risk work, cites the approved shared exception up front, and preserves the narrowed reviewed implementation range above.
- Risk reason: the reviewed slice includes the approved shared regression edit in `tests/unit/test_unified_retrieval.py`, so the packet must follow the high-risk/shared budget class.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Classified the reviewed slice as shared/high-risk work with `tests/unit/test_unified_retrieval.py` as the sole approved shared exception surface.
2. Restated the narrowed reviewed implementation range as `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. Updated the visible handoff artifacts so the budget note, approved exception note, and scope summary match the reviewer-requested framing.

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

## Risks / Blockers

- Risk: `HIGH`
- Residual risk: later branch commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` remain outside this reviewed slice unless a new packet explicitly regenerates the reviewed implementation range.
- Blocker: the sandbox rejects writes under `.codex/`, so `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` could not be updated in this fixer pass even though they are the remaining stale packet mirrors.
- Budget note: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it remains shared/high-risk work under the `4`-task cap and outside the low-risk owned-path-only budget class.

## Required Handoff Fields

- Roadmap item(s) affected: `Milestone 3: Real workflow loop`, `feat-retrieval-fts` as a narrow retrieval-contract slice rather than as lane completion
- Vision capability affected: `2. Retrieval-first context handling`, `6. Auditable state and workflow`
- Routing/provider impact note: `None`
- Canonical demo-path step advanced: `retrieve relevant material`; narrowing public excerpt resolution to the authoritative FTS-first path strengthens deterministic excerpt retrieval on that step without claiming broader workflow progress.
- Ownership/risk classification: `shared-by-approval only`; the reviewed slice includes one approved shared test edit in `tests/unit/test_unified_retrieval.py` and includes no integrator-locked edits.
- Proposed README.md patch text: `None`
