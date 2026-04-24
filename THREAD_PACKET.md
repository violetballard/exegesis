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
- Demo-path sentence: this change advances the canonical demo-path step `retrieve relevant material` by ensuring excerpt lookup stays on the auditable FTS-only retrieval path, which also strengthens downstream basket promotion inputs.
- Reviewer-required packet fix: the handoff now states explicitly that this slice advances `retrieve relevant material` and frames the branch scope only as strengthening that Milestone 3 FTS-first retrieval step, not as general retrieval cleanup.
- FTS-first lane-gate confirmation: the reviewed implementation range remains FTS-first for the MVP. PageIndex and embeddings stay compatibility-only shims and are not required retrieval paths anywhere in this handoff.

## Scope Goal

- Return this lane for re-review with a truthful branch-tip packet that covers the full cumulative retrieval range currently on `codex/feat-retrieval-fts`.

## Scope Completed

- SQLite FTS remains the authoritative retrieval path across the cumulative reviewed range.
- The public and engine retrieval facades now export the canonical query builder, excerpt helpers, and `retrieve_auto` surfaces through the same normalized FTS-first path.
- Retrieval payloads, provenance snapshots, sparse source/context bundles, basket-promotion payloads, and excerpt metadata are normalized deterministically for downstream engine flows.
- Excerpt lookup stays fail-closed on the canonical FTS-first structured retrieval path required by Milestone 3, so basket promotion and downstream workflow consumers only receive canonical excerpt IDs, supported scopes, and normalized query metadata instead of silently widened runtime behavior.
- The packet planner and its regression test now understand cumulative reviewed ranges so emitted review packets disclose the real reviewed head and `Scope completed` summary instead of drifting to a later packet-only SHA.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: refresh the handoff against the actual branch-tip implementation range and keep the reviewer-facing packet aligned only to the Milestone 3 FTS-first `retrieve relevant material` step.
- Risk reason: the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so this remains shared/high-risk work under `AGENTS.md`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the packet to the real reviewed implementation head and cumulative reviewed range on this branch.
2. State explicitly that this lane advances `retrieve relevant material` and reconfirm the FTS-first gate against the full reviewed range.
3. Disclose every reviewed file currently in scope, including packet-planner support changes and shared regression coverage.
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

- `plan complete`: the handoff was re-scoped to the real cumulative reviewed range `d7fd5d200358287fa42a18d39e2b277463b9b69f..39550c18399a5cba2ffad3e23e5b0d5078b416df` and to the canonical demo-path step `retrieve relevant material`.
- `before risky/shared file edit`: the shared/high-risk boundary was called out before refreshing the packet because the reviewed range still includes the approved shared regression file `tests/unit/test_unified_retrieval.py`.
- `first green tests`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed on the refreshed handoff state.
- `ready for handoff`: `THREAD_PACKET.md` and `docs/gate_passed.txt` now agree on the same reviewed head, reviewed range, demo-path step, FTS-first gate, and cumulative file list. The `.codex` mirror files remain blocked by `operation not permitted`.

## Tasks Completed

1. Kept both retrieval facades aligned to the canonical SQLite FTS-first contract by exporting canonical query/excerpt helpers, tightening strategy gating, and preserving deterministic runtime type boundaries.
2. Normalized retrieval payloads, provenance, sparse source/context bundles, cache keys, and basket-promotion metadata so downstream engine flows receive deterministic reconstruction data.
3. Hardened excerpt lookup behavior to fail closed on unsupported or noncanonical paths, including PageIndex-only excerpt IDs and binary query metadata, while leaving PageIndex and embeddings compatibility-only.
4. Updated the packet planner, packet-planner regression coverage, and all reviewer-facing handoff artifacts so re-review is anchored to the real cumulative reviewed range instead of a stale metadata-only slice.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `docs/gate_passed.txt`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_packet_planner.py`
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
- The cumulative reviewed range is larger than the nominal high-risk size guidance; this fixer pass does not add feature scope, it corrects reviewer traceability for the existing branch state.
- Public excerpt lookup now intentionally fails closed on noncanonical/PageIndex-only or binary lookup inputs. Callers must stay on canonical FTS-backed excerpt IDs and normalized text query metadata.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are blocked in this sandboxed session; direct writes fail with `operation not permitted`.

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
- Packet artifacts and planner coverage are included in the reviewed range because the branch tip currently contains them.
