# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `shared high-risk branch-tip handoff refresh`
- Reviewed implementation head before this fixer commit: `39550c18399a5cba2ffad3e23e5b0d5078b416df`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..39550c18399a5cba2ffad3e23e5b0d5078b416df`
- Writable reviewer-facing packet sources refreshed in this fixer pass: `THREAD_PACKET.md`, `docs/gate_passed.txt`
- Blocked packet mirror files in this fixer pass: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`
- Mirror write attempt result in this session: `operation not permitted`
- Companion fixer-commit note: this fixer pass refreshes only handoff metadata on top of the reviewed implementation head above; it does not change retrieval runtime behavior.
- Canonical demo-path step advanced: `retrieve relevant material`
- Demo-path sentence: This work makes the "retrieve relevant material" step more real by enforcing FTS-only excerpt lookup on the canonical retrieval surface and failing closed for PageIndex-only IDs.
- Reviewer-required packet fix: the handoff now uses the exact reviewer-required demo-path sentence and keeps the packet scoped only to the FTS-only excerpt lookup contract covered by `src/qual/retrieval/service.py` and `tests/unit/test_unified_retrieval.py`.
- FTS-first lane-gate confirmation: the reviewed implementation range remains FTS-first for the MVP. PageIndex and embeddings stay compatibility-only shims and are not required retrieval paths anywhere in this handoff.

## Scope Goal

- Return this lane for re-review with a truthful packet that is explicitly scoped to the reviewed FTS-only excerpt lookup slice on `codex/feat-retrieval-fts`.

## Scope Completed

- `fetch_excerpt` resolves excerpt IDs only through the canonical FTS lookup path in `src/qual/retrieval/service.py`.
- PageIndex-only excerpt IDs fail closed instead of widening lookup behavior outside the canonical FTS retrieval surface.
- Regression coverage in `tests/unit/test_unified_retrieval.py` proves the fail-closed contract for noncanonical excerpt IDs and keeps the handoff anchored to that retrieval slice only.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: refresh the handoff so it states exactly which canonical demo-path step this slice advances and keeps the reviewer-facing claims limited to the FTS-only excerpt lookup contract.
- Risk reason: the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so this remains shared/high-risk work under `AGENTS.md`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Replace the demo-path statement with the exact reviewer-required sentence for the retrieval excerpt lookup slice.
2. Remove broader branch-level claims so the handoff stays limited to the FTS-only excerpt lookup contract.
3. Keep the reviewer-facing file scope anchored only to `src/qual/retrieval/service.py` and `tests/unit/test_unified_retrieval.py`.
4. Re-run the required local gates against the current branch state and record the outcomes.

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

- `plan complete`: the handoff was re-scoped to the exact reviewer-required demo-path sentence and to the FTS-only excerpt lookup slice in `src/qual/retrieval/service.py` plus `tests/unit/test_unified_retrieval.py`.
- `before risky/shared file edit`: the shared/high-risk boundary was called out before refreshing the packet because the reviewed range still includes the approved shared regression file `tests/unit/test_unified_retrieval.py`.
- `first green tests`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed on the refreshed handoff state.
- `ready for handoff`: `THREAD_PACKET.md` and `docs/gate_passed.txt` agree on the same canonical demo-path step, exact plan-alignment sentence, and narrowed excerpt-lookup scope. The `.codex` mirror files remain blocked by `operation not permitted`.

## Tasks Completed

1. Mapped this slice directly to the canonical demo-path step `retrieve relevant material` and recorded the exact reviewer-required sentence across the writable handoff sources.
2. Tied the completed retrieval work back to that step by keeping the reviewer-facing scope limited to the FTS-only excerpt lookup contract enforced in `src/qual/retrieval/service.py`.
3. Tied the shared regression story back to that same step by keeping the regression reference limited to fail-closed excerpt-ID coverage in `tests/unit/test_unified_retrieval.py`.
4. Re-ran the required local gates and recorded the outcomes on the refreshed handoff state.

## Files Changed

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- This fixer pass does not add feature scope; it corrects reviewer traceability and narrows the packet to the excerpt lookup contract already implemented and tested.
- Public excerpt lookup intentionally fails closed on noncanonical/PageIndex-only IDs. Callers must stay on canonical FTS-backed excerpt IDs.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain blocked in this sandboxed session; direct writes fail with `operation not permitted`.

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

- Shared-by-approval edits in reviewed range: `YES` (`tests/unit/test_unified_retrieval.py`)
- Integrator-locked edits in reviewed range: `NO`
- This packet is intentionally narrowed to the excerpt lookup slice even though the branch contains other reviewed changes.
