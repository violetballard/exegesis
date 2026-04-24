# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Scope goal: harden the Retrieval Layer MVP contract on the canonical retrieval surface by keeping SQLite FTS authoritative and by rejecting PageIndex-only excerpt IDs on the public excerpt lookup path.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by hardening the canonical FTS-first retrieval contract: SQLite FTS stays authoritative, `fetch_excerpt` resolves only through the canonical FTS path, PageIndex-only excerpt IDs fail closed, and the structured hit/provenance payloads remain deterministic for downstream engine flows.
- Direct handoff statement: this handoff advances the canonical demo-path step `retrieve relevant material` by preserving the FTS-first retrieval contract on the public excerpt lookup path and by keeping the approved shared regression surface narrowly scoped to `tests/unit/test_unified_retrieval.py`.
- Approved exception surface: approved shared regression coverage in `tests/unit/test_unified_retrieval.py` only; no other shared-by-approval or integrator-locked files are part of the reviewed implementation range.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in the reviewed implementation range.
- `fetch_excerpt` resolves only through the canonical FTS path and fails closed for PageIndex-only excerpt identifiers.
- Deterministic structured retrieval output remains available through the canonical engine surface for downstream workflow use.
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
2. Aligned the handoff on the reviewed implementation range `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. Removed stale fallback wording so the handoff now states that `fetch_excerpt` is FTS-only and that PageIndex-only excerpt IDs fail closed.
4. Re-emitted the canonical handoff packet with the explicit demo-path and ownership fields requested in review while preserving the narrowed shared/high-risk framing and the same FTS-only excerpt contract.

## Files Changed

- `THREAD_PACKET.md`

## Commands Run With Results

- `make scope-check`: `PASS` (`[devex] scope-check: no policy for branch 'codex/feat-retrieval-fts'; skipping` then `passed`)
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS` (`216 tests`)
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- Blockers: `None`
- Budget note: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it remains shared/high-risk work under the `4`-task cap and outside the low-risk owned-path-only budget class.

## Required Handoff Fields

- Roadmap item(s) affected: `Milestone 3: Real workflow loop`, `feat-retrieval-fts`
- Vision capability affected: `2. Retrieval-first context handling`, `6. Auditable state and workflow`
- Routing/provider impact note: `None`
- Canonical demo-path step advanced: `retrieve relevant material`; removing the PageIndex fallback from the public excerpt lookup path keeps excerpt resolution on the authoritative FTS-first path needed for basket promotion and downstream workflow use.
- Ownership/risk classification: `shared-by-approval only`; the reviewed slice includes `tests/unit/test_unified_retrieval.py` as the sole approved shared file and includes no integrator-locked edits.
- Proposed README.md patch text: `None`
