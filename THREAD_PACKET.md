# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix handoff refresh`
- Packet refresh trace anchor before fixer commit: `bdbf1eeaa4dcec296f17ad2f3639b18a37a3ea6d`
- Reviewed implementation head: `9bd108298e82f2ba9cc1a6ab97d2f20f7dc622fe`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..9bd108298e82f2ba9cc1a6ab97d2f20f7dc622fe`
- Scope goal: publish a review-safe handoff packet for the live retrieval branch tip after the cumulative FTS-first retrieval fixes through `9bd10829` landed.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by keeping SQLite FTS authoritative while normalizing the retrieval query, payload, provenance, and engine-facing retrieval surface that later context-gathering and basket-promotion steps consume.
- Direct handoff statement: this fixer pass refreshes packet metadata only. It does not change the reviewed implementation head or the reviewed implementation range.

## Scope Completed

The reviewed implementation range now truthfully covers the cumulative retrieval implementation through `9bd10829`. Across `d7fd5d200358287fa42a18d39e2b277463b9b69f..9bd108298e82f2ba9cc1a6ab97d2f20f7dc622fe`, SQLite FTS remains authoritative, retrieval helpers and strategy metadata stay exported through the canonical retrieval and engine facades, payload and provenance reconstruction remain deterministic, excerpt lookup continues to fail closed for deferred strategies, normalized query text is mirrored onto hit payloads and provenance, and the engine-facing `build_retrieval_query` surface binds runtime types without introducing an eager import cycle. PageIndex and embeddings remain compatibility-only fallback shims that fail closed.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: regenerate the handoff around the real cumulative retrieval implementation tip instead of the stale pre-`9bd10829` trace, while preserving the FTS-first Milestone 3 scope.
- Risk reason: the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py` and `tests/unit/test_packet_planner.py`, so the handoff must stay on the high-risk/shared basis.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the reviewed implementation head and range to the live cumulative retrieval code tip.
2. Update scope, task, and file summaries so they match the cumulative implementation now ending at `9bd10829`.
3. State the canonical demo-path step explicitly as `retrieve relevant material` and explain the downstream contract effect.
4. Re-run the required gates on the current metadata-only branch tip and publish the corrected handoff packet.

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

1. Re-anchored the reviewed implementation to the cumulative retrieval range `d7fd5d200358287fa42a18d39e2b277463b9b69f..9bd108298e82f2ba9cc1a6ab97d2f20f7dc622fe` so the packet covers the real live implementation tip instead of stopping at `adfa8cda`.
2. Updated the scope summary and file list to include the retrieval facade, strategy, payload, planner, and regression-test surfaces touched in that cumulative reviewed range.
3. Stated explicitly that this lane advances the canonical demo-path step `retrieve relevant material`, with deterministic FTS-first query, payload, and provenance output for the engine loop.
4. Re-ran the required local gates on the current metadata-only branch tip `bdbf1eeaa4dcec296f17ad2f3639b18a37a3ea6d` after refreshing the packet metadata.

## Files Changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_unified_retrieval.py`

### Metadata-only packet artifacts refreshed in this fixer pass

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

### Metadata-only packet artifacts blocked by filesystem policy in this fixer pass

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- Blocker: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain unwritable from this worktree (`operation not permitted`).
- Budget classification: shared/high-risk because `tests/unit/test_unified_retrieval.py` and `tests/unit/test_packet_planner.py` are approved shared regression surfaces for this lane.
- Traceability note: the current branch tip before this fixer commit is metadata-only (`bdbf1eeaa4dcec296f17ad2f3639b18a37a3ea6d`), but the reviewed retrieval implementation head for re-review remains `9bd108298e82f2ba9cc1a6ab97d2f20f7dc622fe`.

## Required Handoff Fields

- Roadmap item(s) affected: `Milestone 3: Real workflow loop`, `feat-retrieval-fts`
- Vision capability affected: `Retrieval-first context handling`, `Auditable state and workflow`
- Routing/provider impact note: `None`
- Canonical demo-path step advanced: `retrieve relevant material`
- Demo-path effect statement: `The retrieval surface now returns deterministic, FTS-first query, payload, and provenance data that makes the canonical retrieval step believable for the engine loop and ready for later context gathering.`
- Ownership/risk classification: `shared-by-approval`; the reviewed slice includes shared test coverage in `tests/unit/test_unified_retrieval.py` and `tests/unit/test_packet_planner.py` and no integrator-locked files.
- Proposed `README.md` patch text: `None`
