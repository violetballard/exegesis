# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix demo-path alignment`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation scope: `FTS-first excerpt lookup hardening in the accepted retrieval slice`
- Canonical demo-path step advanced: `retrieve relevant material`
- Demo-path sentence: This change makes `retrieve relevant material` more real by ensuring excerpt lookup resolves only through the canonical SQLite FTS path, so downstream basket/workflow consumers cannot silently fall back to PageIndex-only IDs.

## Scope Goal

- Refresh the handoff packet so it explicitly maps the accepted retrieval slice to the canonical demo path without broadening the reviewed narrative beyond the `adfa8cdadd43747ffbcb612e4151e262b13e52ca` scope anchor.

## Scope Completed

- Kept the handoff anchored to the accepted retrieval slice at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Added the explicit canonical demo-path mapping required by `AGENTS.md`.
- Preserved the FTS-first framing for excerpt lookup and avoided reframing this packet as PageIndex or embeddings compatibility work.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: refresh the handoff packet for the accepted retrieval slice and make the canonical demo-path advancement explicit in the packet itself.
- Risk reason: the accepted slice includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so this remains shared/high-risk packet work.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the handoff packet narrative to the accepted `adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice.
2. Add the explicit canonical demo-path statement naming `retrieve relevant material`.
3. Refresh writable handoff artifacts so the demo-path statement is present in the packet itself.
4. Re-run `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## AGENTS Checkpoint Evidence

- `plan complete`: the packet was narrowed to the accepted `adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval slice and the explicit demo-path statement was queued for the handoff itself.
- `before risky/shared file edit`: the shared/high-risk boundary was restated before editing packet files because the accepted slice includes `tests/unit/test_unified_retrieval.py`.
- `first green tests`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed after the packet refresh.
- `ready for handoff`: the writable handoff artifacts now explicitly name `retrieve relevant material` and explain the FTS-only excerpt lookup impact inside the packet itself.

## Tasks Completed

1. Re-anchored the handoff narrative to the accepted `adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval slice.
2. Added the explicit canonical demo-path statement required for `AGENTS.md` compliance.
3. Refreshed the writable handoff artifacts without broadening the packet into PageIndex or embeddings compatibility work.

## Files Changed

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` keeps this handoff under the `4`-task high-risk cap.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain blocked mirror targets in this sandbox and were not refreshed here.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: retrieval/search

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Approved shared test edit in accepted slice: `YES` (`tests/unit/test_unified_retrieval.py`)
- Integrator-locked edit in accepted slice: `NO`
- This packet is intentionally narrowed to the accepted `adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice and should be re-reviewed on that basis.
