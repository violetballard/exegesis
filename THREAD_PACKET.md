# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope Goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in this narrowed slice.
- `fetch_excerpt()` now fails closed unless the excerpt exists on the canonical FTS path, removing the PageIndex fallback from excerpt lookup.
- Approved shared regression coverage proves PageIndex-only excerpt IDs now raise `KeyError`.
- PageIndex and embeddings remain non-required compatibility paths in this slice; excerpt lookup no longer promotes PageIndex as a runtime fallback path for the MVP contract.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`
- This slice makes `retrieve relevant material` more real because `fetch_excerpt()` now fails closed unless the excerpt exists on the canonical FTS path, rejecting PageIndex-only IDs and hardening deterministic structured retrieval and provenance for downstream basket promotion and workflow use.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: close the FTS-only excerpt lookup gap without expanding retrieval scope beyond the MVP contract.
- Risk reason: approved shared regression coverage in `tests/unit/test_unified_retrieval.py` makes this shared/high-risk work.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Confirm the reviewed retrieval slice and the excerpt contract gap the reviewer narrowed to.
2. Refresh the handoff packet so it explicitly names the canonical demo-path step advanced.
3. Tighten roadmap and vision mapping to the exact FTS-only excerpt contract change.
4. Re-run the required gates on the current branch tip and hand off the refreshed packet.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## AGENTS Checkpoint Evidence

- `plan complete`: narrowed the fixer pass to the reviewer-requested packet refresh for the excerpt lookup slice.
- `first green tests`: prior lane gates were green on the reviewed slice; this fixer pass re-runs the required gates on the current branch tip.
- `before risky/shared file edit`: no new shared code edits were needed; this pass refreshes the handoff packet only.
- `ready for handoff`: the packet now names `retrieve relevant material` explicitly and maps the exact excerpt contract change to roadmap and vision language.

## Tasks Completed

1. Refreshed the packet so it explicitly names the canonical demo-path step advanced as `retrieve relevant material`.
2. Tightened the roadmap and vision mapping to the exact contract change: `fetch_excerpt()` now fails closed unless the excerpt exists on the canonical FTS path, rejecting PageIndex-only IDs.
3. Preserved the narrowed reviewed implementation head and range for the excerpt-lookup slice.
4. Re-ran the required local gates on the current fixer branch tip.

## Files Changed

- `THREAD_PACKET.md`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none
- This pass is metadata-only; no retrieval code changed.
- Packet-router metadata files under `.codex/` are not writable in this sandbox, so the tracked handoff packet is the source of truth refreshed here.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md: Milestone 3: Product Readiness`
- `ROADMAP.md: Milestone 4: Retrieval Layer`

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Exact contract impact

- This slice hardens the Milestone 3 retrieval/search surface and Milestone 4 retrieval contract because `fetch_excerpt()` now fails closed unless the excerpt exists on the canonical FTS path, rejecting PageIndex-only IDs and preserving deterministic structured retrieval and provenance for downstream basket promotion and workflow use.

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Approved exception note: approved shared regression coverage in `tests/unit/test_unified_retrieval.py` remains the sole shared-by-approval regression surface for this lane.
- Retrieval remains FTS-first; PageIndex and embeddings stay deferred or compatibility-only and are not promoted to required MVP paths.
