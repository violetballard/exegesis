# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix reissue`
- Current submitted implementation tip before this packet refresh commit: `416d3293d064b6e7fb05a7e8997d91bddbef443f`
- Reviewed implementation head: `416d3293d064b6e7fb05a7e8997d91bddbef443f`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..416d3293d064b6e7fb05a7e8997d91bddbef443f`
- Packet traceability note: review this lane against the cumulative implementation range above. That range includes the substantive post-`adfa8cda` retrieval commits `206ee919c0bb7a1736e07a86a5cba5aff314a785`, `a96043fee95c3be1b69fba0148e6fdbb5d1d51a9`, `9d9e11a1929dc56e44f5a4d459aa385e7a6ce1e5`, `2a136e56b78470a1a579f3cca73397a58b08622a`, `18f0ab0960c6d07920de212785c9517e8688418c`, `7fb9b3cb389e424fcbc0d54cb2087421fe8c6727`, and `416d3293d064b6e7fb05a7e8997d91bddbef443f`. This fixer commit is metadata-only and does not broaden retrieval scope beyond `378cf9a7..416d3293`.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: This change makes the `retrieve relevant material` step more real by keeping excerpt lookup on the canonical FTS-only contract and by making sparse-hit provenance and citation ordering deterministic for downstream basket and workflow use.
- Approved shared regression exception: `tests/unit/test_unified_retrieval.py` remains the only shared-by-approval regression surface in the reviewed implementation range.
- Packet authority note: the authoritative re-review artifacts for this fixer pass are `THREAD_PACKET.md` and `docs/gate_passed.txt`. The tracked `.codex/*` mirror files remain stale because this worktree rejects writes to those paths with `operation not permitted`.

## Scope Goal

- Reissue the retrieval handoff truthfully against the real reviewed implementation range through the current substantive branch tip `416d3293`, while keeping this fixer commit metadata-only.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct reviewer-facing packet traceability without widening the lane beyond the retrieval implementation already on the branch.
- Risk reason: the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so this handoff is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Move the reviewed implementation head and range to the real substantive branch tip.
2. Remove the stale metadata-only story and replace it with truthful cumulative traceability.
3. State the canonical demo-path step explicitly as `retrieve relevant material`.
4. Re-run the required gates and record results against the corrected reviewed range.

## Scope Completed

- Kept excerpt lookup on the canonical FTS-only path so PageIndex-only excerpt IDs fail closed.
- Preserved mirrored query constraints, sparse-hit provenance, and primary citation ordering in deterministic retrieval payloads for downstream engine flows.
- Exposed the canonical retrieval provenance bundle alias and hardened sparse FTS excerpt query rehydration so excerpt payloads preserve stable query metadata when looked up after retrieval.
- Kept retrieval FTS-first, with PageIndex and embeddings remaining compatibility-only fallback shims rather than required runtime paths.
- Regenerated the handoff against the real cumulative implementation range through `416d3293` instead of the stale `adfa8cda`-anchored slice.

## Reviewed Scope Boundary

- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..416d3293d064b6e7fb05a7e8997d91bddbef443f`
- Reviewed implementation files:
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
- Metadata-only packet refresh files in this fixer commit:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Corrected the reviewed implementation head and range so the packet now includes the substantive post-`adfa8cda` retrieval commits through `416d3293`.
2. Replaced the false metadata-only branch-history claim with truthful cumulative traceability and the real reviewed file list.
3. Added the explicit canonical demo-path statement naming `retrieve relevant material`.
4. Re-ran the required gate suite on top of this metadata-only packet refresh and recorded results against the corrected range.

## Files Changed

- Reviewed implementation files in `378cf9a74a3658058079a32f186fcd254c4a4034..416d3293d064b6e7fb05a7e8997d91bddbef443f`:
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
- Metadata-only packet refresh files in this commit:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Validation Refresh Note

- Re-ran the full required gate suite on `2026-04-24` after the reviewer-requested demo-path alignment check.
- Confirmed this packet remains metadata-only and keeps the reviewed implementation range anchored to `378cf9a74a3658058079a32f186fcd254c4a4034..416d3293d064b6e7fb05a7e8997d91bddbef443f`.

## Reviewer Fix Closure

1. The packet now includes the real substantive history after `adfa8cda`, including `2a136e56`, `18f0ab09`, `7fb9b3cb`, and `416d3293`.
2. The reviewed file list is the real cumulative file set for `378cf9a7..416d3293`; the false metadata-only implementation story is gone.
3. The packet names the canonical demo-path step directly as `retrieve relevant material` and explains how this range makes that step more real.
4. The shared-file exception remains limited to `tests/unit/test_unified_retrieval.py`.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: authoritative FTS-first retrieval feeding the engine loop

### Canonical demo-path step advanced

- `retrieve relevant material`
- This change makes the `retrieve relevant material` step more real by keeping excerpt lookup on the canonical FTS-only contract and by making sparse-hit provenance and citation ordering deterministic for downstream basket and workflow use.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
