# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Current branch head before this fixer commit: `6c19e8754c660465ac6c54ff4b12f0e28225caba`
- Reviewed implementation head: `b3554ecae4c443d6a5a03d8a797fb350f5479043`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..b3554ecae4c443d6a5a03d8a797fb350f5479043`
- Packet refresh role: `reviewer-fix handoff regeneration`
- Packet-only commits after reviewed head:
  - `6ab81410`
  - `cfe1894e`
  - `5dbaee2a`
  - `6c19e875`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output on the canonical retrieval surface.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output on the canonical retrieval surface.
- Risk reason: the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so this handoff must satisfy the shared/high-risk packet requirements.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Checkpoint Status

- `plan complete`: regenerated the operative handoff so the reviewed implementation range now includes the real retrieval code/test head `b3554eca...` instead of the stale `adfa8cda...` anchor.
- `first green tests`: all required gates were re-run on the lane branch for this fixer pass.
- `before risky/shared file edit`: no new shared code edit was needed; the only shared implementation file in the reviewed range remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the operative packet now carries accurate traceability, explicit AGENTS demo-path mapping, and a scope statement tightened to the FTS-first retrieval step.

## Budget classification

- Shared/high-risk handoff under the `4`-task cap because the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Packet-only commits after `b3554eca...` do not change the reviewed implementation range.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path on the canonical retrieval surface.
- This reviewed range advances the canonical demo-path step `retrieve relevant material` by keeping retrieval FTS-first, deterministic, and auditable enough for downstream basket promotion without claiming broader workflow completion.
- The reviewed implementation range now accurately includes the post-`adfa8cda...` retrieval code and test changes through `b3554eca...`; later commits on the branch are packet-only refreshes.
- Retrieval payloads, provenance snapshots, source bundles, context bundles, shortlist provenance, ranked ids, and excerpt lookup metadata are normalized deterministically for downstream basket and workflow use.
- Public retrieval facades expose the canonical query constructor and FTS-first helpers while PageIndex and embeddings remain deferred, non-required paths for the MVP.
- Excerpt lookup and basket-promotion metadata are hardened on the FTS-first path so downstream consumers receive deterministic, auditable retrieval payloads.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This reviewed range makes `retrieve relevant material` more real by keeping retrieval FTS-first, structured, and auditable enough for downstream basket promotion and later workflow use.
- This packet does not claim completion of basket promotion, workflow actions, or alternate retrieval paths beyond that FTS-first retrieval step.

## Required reviewer fixes addressed

1. Regenerated the handoff so review traceability matches the actual branch state: retrieval code/test changes after `adfa8cda...` are now included in the reviewed implementation head `b3554eca...` and range `d7fd5d20..b3554eca`.
2. Added an explicit AGENTS plan-alignment statement that this lane advances the canonical demo-path step `retrieve relevant material`.
3. Tightened scope wording so this handoff stays framed as authoritative FTS retrieval, deterministic excerpt payloads, and auditable provenance on the `retrieve relevant material` step, not broader excerpt API expansion or PageIndex/embeddings as required paths.

## Tasks completed

1. Kept retrieval FTS-first and authoritative across the canonical retrieval facade, including query construction and helper exports.
2. Hardened deterministic retrieval payloads, provenance snapshots, source/context bundles, shortlist provenance, and basket-promotion metadata for downstream engine flows.
3. Tightened excerpt lookup and audit payload handling on the FTS-first path so canonical retrieval payloads fail closed where required and remain auditable.
4. Added and maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the canonical retrieval contract.

## Files changed

- Reviewed implementation files:
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
- Packet-only files after reviewed head:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

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
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file in the reviewed implementation range.
