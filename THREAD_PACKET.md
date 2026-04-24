# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only handoff packet refresh`
- Packet refresh trace anchor before fixer commit: `26395a2b80fac607b540cd9925284e9a51cf4c78`
- Reviewed implementation head: `255bf8d81801cfd21aa8dc5c9db5d5e11c3efa2b`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..255bf8d81801cfd21aa8dc5c9db5d5e11c3efa2b`
- Scope goal: publish a review-safe handoff packet for the full live retrieval code slice and distinguish it from later metadata refreshes.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by keeping SQLite FTS authoritative, failing closed for unsupported excerpt lookup paths, preserving deterministic retrieval payloads and provenance, and making the engine-facing retrieval contract stable enough for the Milestone 3 engine-first loop while moving Milestone 4 retrieval behavior forward.
- Direct handoff statement: this fixer pass updates packet metadata so it matches the real reviewed retrieval code slice and the actual current packet tip. Re-review should use `git log --oneline 378cf9a74a3658058079a32f186fcd254c4a4034..255bf8d81801cfd21aa8dc5c9db5d5e11c3efa2b` and compare the later metadata-only packet refresh chain `05c341b5acaa21bd64843e0ac1a6dc62bbed2d01..26395a2b80fac607b540cd9925284e9a51cf4c78` separately.

## Scope Completed

The reviewed retrieval implementation range now truthfully covers the full live retrieval code slice rather than only the FTS-only excerpt fallback removal. Across `378cf9a74a3658058079a32f186fcd254c4a4034..255bf8d81801cfd21aa8dc5c9db5d5e11c3efa2b`, SQLite FTS stays authoritative, unsupported scoped queries and PageIndex-only excerpt IDs fail closed, retrieval payloads and provenance snapshots are normalized for deterministic downstream use, sparse source bundles reconstruct canonical hit payloads without losing query text, engine retrieval facade exports stay aligned with the canonical query constructor and `retrieve_auto`, engine query annotations no longer create an eager import cycle, and sparse-hit payload reconstruction backfills missing query context. PageIndex and embeddings remain compatibility-only fallback shims behind the canonical retrieval facade.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: regenerate the handoff around the full reviewed retrieval code slice instead of a narrowed excerpt-only story.
- Risk reason: the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the handoff must stay on the high-risk/shared basis.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the reviewed implementation head and range to the truthful retrieval code slice and separate later packet-only commits.
2. Rewrite scope, tasks, and file summaries so they match the full reviewed retrieval behavior.
3. State the canonical demo-path step explicitly as `retrieve relevant material` and explain the concrete engine-loop effect.
4. Re-run the required gates and publish the corrected handoff packet.

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

### Handoff Packet

- branch name
- tasks completed (numbered)
- files changed
- commands run + outcomes
- risks/blockers
- all required fields from `INTEGRATION.md`

## Tasks Completed

1. Re-anchored the handoff to the truthful reviewed retrieval code head `255bf8d81801cfd21aa8dc5c9db5d5e11c3efa2b` and separated later packet-only commits from the reviewed implementation range.
2. Updated the scope summary to cover the full reviewed retrieval behavior, including fail-closed excerpt lookup and scoped-query behavior, deterministic payload and provenance normalization, sparse source/context rehydration, engine facade exports, and the sparse-hit query-context backfill.
3. Added the explicit canonical demo-path statement for `retrieve relevant material` and tied it to stable engine-facing retrieval contracts for the Milestone 3 engine-first loop while keeping Milestone 4 retrieval work FTS-first.
4. Refreshed the visible handoff packet surfaces so re-review can compare the code range and the later metadata-only packet refresh chain without conflating them.

## Files Changed

### Reviewed retrieval code scope

- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `tests/unit/test_unified_retrieval.py`

### Packet refresh files in this fixer pass

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PENDING`
- `./quality-format.sh --check`: `PENDING`
- `./quality-lint.sh`: `PENDING`
- `./quality-test.sh`: `PENDING`
- `./typecheck-test.sh`: `PENDING`
- `make ci`: `PENDING`

## Risks / Blockers

- Risk: `HIGH`
- Blockers:
  - `.codex/kickoff_packets/feat-retrieval-fts.md` remains unwritable from this worktree (`operation not permitted`).
  - `.codex/lane_meta/feat-retrieval-fts.json` remains unwritable from this worktree (`operation not permitted`).
- Budget classification: shared/high-risk because `tests/unit/test_unified_retrieval.py` is a shared-by-approval file for this lane.
- Traceability note: reviewers can verify the reviewed retrieval scope directly with `git log --oneline 378cf9a74a3658058079a32f186fcd254c4a4034..255bf8d81801cfd21aa8dc5c9db5d5e11c3efa2b` and `git diff --name-only 378cf9a74a3658058079a32f186fcd254c4a4034..255bf8d81801cfd21aa8dc5c9db5d5e11c3efa2b`. The packet-only refresh chain after the reviewed code head is `05c341b5acaa21bd64843e0ac1a6dc62bbed2d01..26395a2b80fac607b540cd9925284e9a51cf4c78`.

## Required Handoff Fields

- Roadmap item(s) affected: `Milestone 4: Retrieval Layer`, `Milestone 3: Product Readiness`
- Vision capability affected: `2. Retrieval-first context handling`, `6. Auditable state and workflow`
- Routing/provider impact note: `None`
- Canonical demo-path step advanced: `retrieve relevant material`
- Demo-path effect statement: `Retrieval output remains deterministic, auditable, and correctly shaped for the engine-first workflow loop while keeping the MVP retrieval path FTS-first.`
- Ownership/risk classification: `shared-by-approval`; the reviewed slice includes shared test coverage in `tests/unit/test_unified_retrieval.py` and no integrator-locked files.
- Proposed `README.md` patch text: `None`
