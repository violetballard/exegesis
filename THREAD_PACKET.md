# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix packet regeneration`
- Current branch tip before this fixer pass: `49adae867a897af667a611e4dd401eba63609280`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..245ddb91b906caf392797830468606ec1101c3d2`
- Reviewed implementation head: `245ddb91b906caf392797830468606ec1101c3d2`
- Packet-only descendants above the reviewed implementation head: `cd42fd6c`, `bb3cd335`, `49adae86`
- Packet traceability note: the reviewed retrieval implementation for this handoff ends at `245ddb91b906caf392797830468606ec1101c3d2`. The later commits `cd42fd6c`, `bb3cd335`, and `49adae86` update handoff wording only and do not change retrieval implementation files.

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: keep the retrieval lane on the canonical FTS-first path with deterministic payload, provenance, and excerpt lookup behavior for engine flows.
- Risk reason: the reviewed implementation includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep excerpt lookup and retrieval hits on the canonical FTS-first runtime path.
2. Make retrieval payloads, provenance, citation bundles, and downstream snapshots deterministic.
3. Fail closed when deferred or sparse excerpt contexts cannot be resolved through the authoritative FTS path.
4. Keep the shared regression coverage aligned with the canonical retrieval contract.

### Checkpoint Status

- `plan complete`: the packet is regenerated against the actual branch-tip review state instead of the stale `adfa8cda` slice.
- `first green tests`: recorded after rerunning the required gates for this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in the reviewed range remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the handoff now distinguishes the reviewed implementation head `245ddb91...` from the later packet-only tip commits.

## Scope completed

- Kept SQLite FTS as the authoritative retrieval backend and `fts_first` as the required MVP retrieval mode.
- Expanded the canonical retrieval surface in `src/qual/retrieval/**` and `src/qual/engine/retrieval/**` so payload helpers, citation bundles, provenance bundles, and downstream snapshots stay deterministic and auditable.
- Hardened payload normalization, cache-key/query normalization, sparse hit/provenance backfill, and excerpt lookup so deferred/PageIndex-only paths fail closed instead of becoming required runtime behavior.
- Preserved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the canonical FTS-only excerpt contract and the broader deterministic retrieval payload surface.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff advances `retrieve relevant material` by keeping excerpt lookup, payload reconstruction, and provenance output on the authoritative FTS-first path that downstream basket promotion and engine workflow steps consume.

## Tasks completed

1. Kept excerpt lookup and public retrieval hits on the canonical FTS-first path, including fail-closed behavior for deferred/PageIndex-only resolution.
2. Normalized retrieval payloads, policy snapshots, citation/provenance/source bundles, and helper exports so downstream engine consumers receive deterministic structured output.
3. Hardened sparse excerpt/query-context recovery, cache isolation, and hit provenance backfill without reintroducing PageIndex or embeddings as required runtime paths.
4. Maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the canonical retrieval contract.

## Files changed

- Reviewed implementation files:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Reviewed metadata files inside the implementation range:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
- Packet-only descendant file above the reviewed implementation head:
  - `THREAD_PACKET.md`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. The handoff now matches the actual branch being reviewed: it names the current tip `49adae86...`, the true reviewed implementation range `378cf9a7..245ddb91`, and the packet-only commits that sit above that implementation head.
2. The packet now states the canonical demo-path step explicitly as `retrieve relevant material`, matching `AGENTS.md` and `ROADMAP.md`.
3. The roadmap and vision mapping now describe the true cumulative reviewed contents and reaffirm that SQLite FTS remains the required MVP path while PageIndex and embeddings stay deferred, compatibility-only paths.

## Risks / blockers

- Risk: `HIGH`
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval implementation file in the reviewed range.
- Ownership detail: no integrator-locked runtime files are part of the reviewed retrieval implementation range. Runtime edits remain in the lane-owned retrieval paths, and the only non-owned edit is the approved shared regression file `tests/unit/test_unified_retrieval.py`.
