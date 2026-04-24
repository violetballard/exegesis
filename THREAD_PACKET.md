# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix canonical demo-path mapping`
- Current submitted tip before this packet refresh commit: `059b68f366a2a67814e68f0baf9eb740600099bb`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet traceability note: review this lane against the narrowed implementation range above. The current packet refresh commit is metadata-only and does not broaden retrieval scope beyond `378cf9a7..adfa8cda`.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: This work advances `retrieve relevant material` by making the public excerpt lookup surface resolve through the authoritative SQLite FTS path, so PageIndex-only excerpt IDs fail closed under shared regression coverage.
- Scope-tight statement: basket promotion is only a downstream consumer of the structured FTS result from this slice; this handoff does not broaden the lane beyond the FTS-only excerpt fail-closed contract.

## Scope Goal

- Regenerate the retrieval-specific handoff packet so it stays narrowed to reviewed commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and states explicitly that this work advances `retrieve relevant material`.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the reviewer packet against the reviewed retrieval implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` without widening the lane beyond the approved FTS-only excerpt fail-closed slice.
- Risk reason: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep the handoff anchored to reviewed implementation head `adfa8cda` and reviewed range `378cf9a7..adfa8cda`.
2. State the canonical demo-path step explicitly as `retrieve relevant material`.
3. Reconcile the handoff artifacts so `THREAD_PACKET.md` and `docs/gate_passed.txt` carry the same narrowed traceability.
4. Re-run the required gates and record results against the narrowed reviewed implementation head/range.

### Checkpoint Status

- `plan complete`: the packet is anchored to the reviewer-approved retrieval implementation range `378cf9a7..adfa8cda`.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- `fixer gate rerun`: all required gates passed again on metadata-only packet tip `059b68f366a2a67814e68f0baf9eb740600099bb` immediately before this commit.
- `before risky/shared file edit`: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the top-level packet and gate summary agree on the same reviewed implementation head, reviewed range, and canonical-step wording.

## Scope Completed

- SQLite FTS remains the authoritative retrieval path for the reviewed implementation range.
- The public excerpt lookup surface resolves through the canonical FTS path, so PageIndex-only excerpt IDs fail closed with no PageIndex runtime fallback on that surface.
- The reviewed evidence is intentionally narrow: it hardens the excerpt lookup contract and its public FTS helper surface rather than re-proving broader lane claims.
- This handoff explicitly states that the reviewed slice advances the canonical demo-path step `retrieve relevant material`.

## Reviewed Scope Boundary

- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation files:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Current metadata-only handoff files in this packet refresh:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Kept `fetch_excerpt` on the canonical FTS-only lookup path so PageIndex-only excerpt IDs fail closed.
2. Kept the reviewed scope anchored to commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. Re-emitted retrieval-specific handoff artifacts so the completed packet is no longer stale or lane-mismatched.
4. Regenerated the top-level handoff artifacts so `THREAD_PACKET.md` and `docs/gate_passed.txt` match the same narrowed story.

## Files Changed

- Reviewed implementation files in `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Current metadata-only packet refresh files:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_fetch_excerpt_requires_an_fts_lookup_hit tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_source_bundle_matches_result_snapshot`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The packet stays narrowed to reviewed implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and reviewed range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. The handoff explicitly states that this work advances the canonical demo-path step `retrieve relevant material`.
3. Basket promotion is described only as a downstream consumer of structured FTS results, not as expanded lane scope.
4. The completed packet is retrieval-specific and branch-local instead of lane-stale.
5. The reviewed file list and gate summary both match the narrowed reviewed implementation range.

## Risks / Blockers

- Risk: approved shared regression coverage remains in `tests/unit/test_unified_retrieval.py`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Product Readiness`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`
- Deterministic FTS-only excerpt lookup strengthens the auditable retrieval contract before any downstream consumer uses the structured result.

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
