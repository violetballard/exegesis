# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix handoff refresh`
- Reviewed implementation head: `d08431dd4fe27a23b0c166f074eaf2ff5a0aeb9d`
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..d08431dd4fe27a23b0c166f074eaf2ff5a0aeb9d`
- Scope goal: keep the post-`adfa8cda` retrieval follow-up slice FTS-first, deterministic, and auditable on the canonical engine surface.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by keeping excerpt lookup, canonical query handling, query-constraint normalization, and downstream provenance payloads on the authoritative SQLite FTS path so later basket-promotion and workflow consumers receive deterministic retrieval state instead of PageIndex-backed fallback state.
- Direct handoff statement: this packet now matches the actual retrieval code that would merge after `adfa8cda`. The post-`adfa8cda` planner and packet-planner drift has been cleared from the branch tree, so the reviewed slice below is retrieval-only plus the approved shared regression file.
- Approved exception surface: one approved shared test edit in `tests/unit/test_unified_retrieval.py` only. No integrator-locked files and no other shared-by-approval files are part of the reviewed implementation slice.

## Scope Completed

- Kept SQLite FTS authoritative through the engine retrieval facade while restoring the fail-closed excerpt contract on canonical FTS-backed IDs.
- Stabilized deterministic payload, provenance, query-constraint, section-hint, and audit snapshots for sparse source/context bundle reconstruction and downstream basket-promotion use.
- Preserved basket-promotion-ready retrieval metadata, ranked IDs, policy aliases, and citation/provenance context without promoting PageIndex or embeddings to required runtime paths.
- Cleared the post-`adfa8cda` planner/test packet drift that the reviewer flagged, so this reviewed slice is now retrieval-only plus the approved shared regression coverage.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: regenerate the retrieval handoff against the actual post-`adfa8cda` branch state and remove the unrelated planner packet drift from that same branch tip.
- Risk reason: the reviewed slice still includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the handoff remains shared/high-risk work.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Kept the engine-facing retrieval facade FTS-first by tightening canonical query and excerpt lookup behavior after `adfa8cda`.
2. Hardened deterministic payload, provenance, audit, and sparse bundle reconstruction behavior needed by downstream retrieval consumers and basket promotion.
3. Preserved the approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the canonical retrieval contract.
4. Removed the reviewer-flagged post-`adfa8cda` planner drift so the branch tree now matches the reviewed retrieval-only scope.

## Files Changed

### Reviewed implementation files

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Metadata-only handoff files

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
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
- Residual risk: this is a large retrieval follow-up slice after `adfa8cda`, so re-review should use the exact reviewed implementation range above rather than the older narrowed packet.
- Blockers: none

## Required Handoff Fields

- Roadmap item(s) affected: `Milestone 3: Real workflow loop`, `feat-retrieval-fts` as the authoritative retrieval path feeding engine workflow state
- Vision capability affected: `2. Retrieval-first context handling`, `6. Auditable state and workflow`
- Routing/provider impact note: `None`
- Canonical demo-path step advanced: `retrieve relevant material`; this slice makes that step more real by keeping excerpt lookup, query normalization, and audit/provenance payloads on the canonical FTS path.
- Ownership/risk classification: `shared-by-approval only`; the reviewed slice includes one approved shared test edit in `tests/unit/test_unified_retrieval.py` and no integrator-locked edits.
- Proposed README.md patch text: `None`
