# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix resubmission`
- Current branch tip before this fixer pass: `16684eda08b7e88cf8f72015d78297d9ca44a60b`
- Submitted implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..16684eda08b7e88cf8f72015d78297d9ca44a60b`
- Packet traceability note: this packet supersedes the rejected narrowed slice that stopped at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`. The submitted scope for re-review is the cumulative branch-tip implementation through `16684eda08b7e88cf8f72015d78297d9ca44a60b`; the fixer commit created from this pass refreshes packet metadata only after rerunning gates.

## Scope goal

- Advance `Milestone 3: Real workflow loop` by making the canonical demo-path step `retrieve relevant material` concretely FTS-first for engine flows, with deterministic excerpt, provenance, and basket-promotion payloads.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: keep retrieval FTS-first while making excerpt lookup, downstream payloads, and basket-promotion context deterministic and auditable.
- Risk reason: the submitted branch includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (folded cumulative branch scope)

1. Harden the canonical FTS retrieval path, ranking inputs, cache keys, and excerpt lookup behavior.
2. Normalize retrieval payloads, provenance, and snapshot reconstruction for deterministic downstream use.
3. Preserve basket-promotion and context-bundle data needed by the engine demo path.
4. Keep packet tooling and shared regression coverage aligned with the true submitted branch-tip scope.

### Checkpoint Status

- `plan complete`: this resubmission treats the cumulative branch-tip implementation through `16684eda08b7e88cf8f72015d78297d9ca44a60b` as the submitted scope.
- `first green tests`: recorded after rerunning the required gates for this fixer pass.
- `before risky/shared file edit`: the submitted branch still includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: packet scope, tasks, and file lists now match the submitted branch-tip implementation instead of the rejected `adfa8cda` slice.

## Scope completed

- Advanced `Milestone 3: Real workflow loop` by making the canonical demo-path step `retrieve relevant material` concretely FTS-first: SQLite FTS remains authoritative for the MVP retrieval path, with hardened ranking inputs, cache normalization, query normalization, shortlist behavior, and fail-closed excerpt lookup.
- Exported and aligned canonical retrieval helpers across the retrieval facades, including the generic excerpt fetch shim and canonical helper surfaces used by downstream engine flows.
- Normalized retrieval payloads, provenance, citation bundles, sparse snapshot rehydration, and excerpt metadata so downstream consumers receive deterministic structured hits and auditable context.
- Preserved basket-promotion, source-bundle, and context-bundle data needed to move retrieved material into later engine workflow steps.
- Updated packet tooling and packet metadata so the handoff reflects the true branch-tip scope instead of a stale narrowed range.

## Canonical Demo-Path Steps Advanced

- `retrieve relevant material`: FTS-first ranking, excerpt lookup, deterministic query/provenance snapshots, and auditable retrieval payloads.
- `promote or gather context into the basket`: basket-promotion payloads, source/context bundle reconstruction, retrieved-id tracking, and stable fingerprints for promoted excerpts.

## Tasks completed

1. Hardened the canonical FTS retrieval path across `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/fts_strategy.py`, and related facade exports so excerpt lookup, ranking inputs, and cache behavior stay deterministic and FTS-first.
2. Canonicalized retrieval payloads and provenance in `src/qual/engine/retrieval/payload.py` plus the retrieval facades so sparse snapshots, citations, and helper outputs rehydrate consistently for downstream engine consumers.
3. Preserved basket-promotion and context-bundle workflow data in the retrieval layer, including explicit retrieved IDs, fingerprints, and query constraints needed for the engine demo path.
4. Updated packet tooling and shared regression coverage in `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`, and `tests/unit/test_unified_retrieval.py` so the handoff and regression surface match the true submitted scope.

## Files changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
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

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. The handoff now treats the cumulative submitted branch-tip implementation through `16684eda08b7e88cf8f72015d78297d9ca44a60b` as the review target instead of isolating `adfa8cda`.
2. `Scope completed`, `Tasks completed`, and `Files changed` now include the non-metadata implementation work after `adfa8cda`, including retrieval payload, facade, basket-promotion, packet-tooling, and regression surfaces.
3. Roadmap and product mapping now state the concrete demo-path steps advanced by the submitted scope: `retrieve relevant material` and `promote or gather context into the basket`.
4. The required gates were rerun against the resubmitted content before this packet refresh.

## Risks / blockers

- Risk: `HIGH`
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` remains the approved shared regression surface for this lane.
- Ownership detail: runtime retrieval changes stay in the lane-owned retrieval paths. The submitted branch also carries packet-tooling and packet metadata updates needed to keep the handoff aligned with the true branch-tip scope.
