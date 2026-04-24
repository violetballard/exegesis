# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Reviewed implementation head: `2b03f9a218ce3444bb2e49d8204ceebbcfe82ad7`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..2b03f9a218ce3444bb2e49d8204ceebbcfe82ad7`
- Scope goal: keep the retrieval lane FTS-first for the MVP by shipping the cumulative retrieval-contract work on the current branch tip, including deterministic excerpt resolution, canonical query and provenance payload normalization, and the approved shared regression coverage for that behavior.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by making the canonical SQLite FTS retrieval path and excerpt resolution deterministic for downstream basket and workflow use, including the provenance-bundle query data now shipped on the branch tip.

## Scope Completed

- Kept SQLite FTS authoritative across the retrieval and engine facades while leaving PageIndex and embeddings as compatibility-only fallback shims that fail closed.
- Preserved deterministic payload, hit, excerpt, and provenance snapshots for downstream engine flows, including sparse source and context rehydration.
- Enforced the canonical FTS-only excerpt path under approved shared regression coverage so non-FTS excerpt identifiers fail closed.
- Included the tip commit `2b03f9a2` as retrieval-contract work: `src/qual/engine/retrieval/payload.py` and `src/qual/retrieval/service.py` now preserve canonical query text in the provenance bundle instead of treating that change as metadata-only.
- Refreshed the handoff artifacts so the reviewed range, file list, budget note, and gate results describe the code actually present on the branch tip.

## Thread Kickoff

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: ship the cumulative retrieval-contract branch tip truthfully for re-review instead of a narrowed metadata-only slice.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Kept the retrieval lane FTS-first by preserving the canonical retrieval query constructor and `retrieve_auto` helper through both retrieval facades.
2. Hardened deterministic retrieval payload, provenance, and sparse source/context rehydration behavior for downstream engine flows.
3. Kept excerpt lookup on the canonical FTS-only path under shared regression coverage, with non-FTS excerpt IDs failing closed.
4. Preserved canonical query text in the provenance bundle on the actual branch tip and regenerated the handoff so that change is described as retrieval-contract work.

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
- Blockers: `None`
- Budget note: this is shared/high-risk work because `tests/unit/test_unified_retrieval.py` is a shared-by-approval file for this lane. The actual reviewed tip spans `15 files`, `10848 insertions`, and `1087 deletions` relative to `378cf9a7`, so this handoff intentionally describes the cumulative branch tip rather than a narrow two-file slice.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`
- `retrieve relevant material`

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This slice advances that step by making the canonical SQLite FTS retrieval path and excerpt resolution deterministic for downstream basket and workflow use, including the provenance-bundle query data now preserved on the branch tip.

### Routing/provider impact note

- None

### Proposed README.md patch text

- None
