# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `truthful branch-tip reviewer-fix handoff refresh`
- Current submitted tip before this packet refresh commit: `d0d89fe51d8d44a0cc798698c7b0354c7392d307`
- Truthful promoted implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..d0d89fe51d8d44a0cc798698c7b0354c7392d307`
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: this work makes `retrieve relevant material` more real by keeping excerpt lookup, retrieval payload rebuilds, source bundles, and engine-facing retrieval exports anchored to the authoritative SQLite FTS path with deterministic structured output for downstream consumers.

## Scope Goal

- Regenerate the retrieval handoff against the real branch tip instead of the narrowed `adfa8cda` slice so integration reviews the code that is actually present on the promotion branch.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: restate the handoff truthfully for the actual promoted branch tip, including post-`adfa8cda` retrieval/runtime commits and their gate results.
- Risk reason: this lane includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, and the truthful promoted range also spans runtime retrieval code plus packet artifacts.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Promote the truthful branch-tip range `378cf9a7..d0d89fe5` instead of the stale `378cf9a7..adfa8cda` slice.
2. Restate `Scope completed`, `Tasks completed`, and `Files changed` for the actual promoted code, including post-`adfa8cda` retrieval/runtime commits.
3. Re-run and record the required gates against the truthful promoted range.
4. Carry the canonical demo-path step directly in the review packet.

### Checkpoint Status

- `plan complete`: the handoff now targets the actual branch tip `d0d89fe5`, not the stale reviewed-slice head `adfa8cda`.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on the truthful promoted range.
- `before risky/shared file edit`: this lane still uses the approved shared regression file `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: packet, kickoff artifact, lane metadata, and gate summary all describe the same truthful branch-tip range.

## Scope Completed

- SQLite FTS remains the authoritative retrieval path across the promoted range.
- The public excerpt lookup surface is FTS-only and fails closed for PageIndex-only excerpt IDs.
- Retrieval payload rebuilds, provenance snapshots, source bundles, constraint normalization, and engine-facing exports are deterministic across the promoted range.
- The promoted branch tip also includes packet/planner updates needed to keep retrieval handoff traceability and planner expectations aligned with the branch-tip implementation.
- This handoff explicitly advances the canonical demo-path step `retrieve relevant material`.

## Reviewed Scope Boundary

- Truthful promoted implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..d0d89fe51d8d44a0cc798698c7b0354c7392d307`
- Files changed in that promoted range:
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

## Tasks Completed

1. Kept excerpt lookup and retrieval surfaces FTS-first, including fail-closed excerpt behavior plus aligned audit payloads on the public retrieval service.
2. Hardened retrieval payload rebuilds, source bundle/context rehydration, cache/query normalization, and deterministic provenance snapshots used by downstream engine flows.
3. Updated retrieval facades, engine exports, and planner-facing expectations so the canonical retrieval helpers and structured outputs stay consistent across runtime and packet tooling.
4. Regenerated the handoff artifacts truthfully for the real promoted branch tip and reran all required gates against that range.

## Budget Compliance

- Task cap: `PASS` as four meaningful high-risk tasks are reported.
- Shared-file approval: `PASS` because the only shared-by-approval test surface remains `tests/unit/test_unified_retrieval.py`.
- Size budget: `FAIL` for the truthful promoted range because it spans `15 files` and `10447 insertions(+), 1082 deletions(-)`, exceeding the high-risk limits of `<=8 files` and `<=300 net LOC`.
- Handoff implication: this packet is now truthful about the budget overrun instead of hiding the extra runtime work behind a narrowed slice.

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

- `make scope-check`: `PASS` (`no policy for branch 'codex/feat-retrieval-fts'; skipping`)
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The handoff now matches the real promoted branch tip instead of the stale `adfa8cda` slice.
2. `Scope completed`, `Tasks completed`, `Files changed`, and budget compliance are restated against the truthful promoted range.
3. The required gates are reported against the truthful promoted range.
4. The packet itself explicitly states the canonical demo-path step `retrieve relevant material`.
5. The packet no longer describes post-`adfa8cda` retrieval/runtime commits as metadata-only.

## Risks / Blockers

- Risk: the truthful promoted range exceeds the high-risk size budget and still includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Product Readiness`
- This promoted range supports the Milestone 3 retrieval outcome by keeping retrieval structured, deterministic, and FTS-first for downstream consumers.
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`
- Truthful branch-tip promotion keeps the actual retrieval implementation aligned with the canonical FTS-backed retrieval step instead of a narrower historical slice.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
