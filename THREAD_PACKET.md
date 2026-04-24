# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix handoff refresh`
- Current branch tip before fixer commit: `314d8021abfee6f50e728f8c550f16ca7a2393cc`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Scope goal: keep the re-review packet narrowed to the excerpt-only FTS contract fix so the handoff stays deterministic, auditable, and AGENTS-compliant without widening retrieval scope.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by forcing excerpt lookup to stay on the authoritative SQLite FTS path and fail closed for unsupported PageIndex-only excerpt identifiers.
- Direct handoff statement: this handoff remains intentionally narrowed to the single implementation commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` (`Make retrieval excerpts FTS-only`). Later branch-tip metadata commits do not widen the reviewed implementation range for this re-review.
- Approved exception surface: one approved shared test edit in `tests/unit/test_unified_retrieval.py` only; no integrator-locked files and no other shared-by-approval files are part of the reviewed implementation slice.

## Scope Completed

- The narrowed retrieval slice keeps SQLite FTS authoritative for excerpt lookup on the canonical engine retrieval surface.
- `src/qual/retrieval/service.py` removes the PageIndex fallback from `fetch_excerpt`, so excerpt lookup now resolves only through the canonical FTS path.
- `tests/unit/test_unified_retrieval.py` preserves the approved shared regression coverage and proves PageIndex-only excerpt identifiers fail closed with `KeyError`.
- The reviewed implementation range for this handoff stays `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: reissue the retrieval handoff against the reviewer-required narrowed excerpt slice and make the AGENTS packet explicitly shared/high-risk.
- Risk reason: the reviewed slice includes the approved shared regression edit in `tests/unit/test_unified_retrieval.py`, so the packet must follow the high-risk/shared budget class.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Reclassified the handoff as shared/high-risk because the narrowed slice includes the approved shared regression surface in `tests/unit/test_unified_retrieval.py`.
2. Made the packet internally consistent around the reviewer-required narrowed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. Preserved the FTS-first excerpt contract change in `src/qual/retrieval/service.py` and the fail-closed shared regression coverage in `tests/unit/test_unified_retrieval.py`.
4. Stated the canonical demo-path impact directly: this slice advances `retrieve relevant material` by making excerpt lookup fail closed on the FTS-first contract.

## Files Changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Metadata-only handoff files

- `THREAD_PACKET.md`
- `.codex/kickoff_packets/feat-retrieval-fts.md` (write-blocked in this environment)
- `.codex/lane_meta/feat-retrieval-fts.json` (write-blocked in this environment)

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- Blocker: writes to `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` fail with `Operation not permitted` in this worktree, so the visible handoff is corrected here but the hidden packet mirror remains stale.
- Budget note: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it remains shared/high-risk work under the `4`-task cap and outside the low-risk owned-path-only budget class.

## Required Handoff Fields

- Roadmap item(s) affected: `Milestone 3: Real workflow loop`, `feat-retrieval-fts`
- Vision capability affected: `Retrieval-first context handling`, `Auditable state and workflow`
- Routing/provider impact note: `None`
- Canonical demo-path step advanced: `retrieve relevant material`; this slice strengthens deterministic excerpt retrieval on that step without claiming broader workflow progress.
- Ownership/risk classification: `shared-by-approval only`; the reviewed slice includes one approved shared test edit in `tests/unit/test_unified_retrieval.py` and includes no integrator-locked edits.
- Proposed `README.md` patch text: `None`
