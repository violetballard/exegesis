# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Scope goal: complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by keeping SQLite FTS authoritative and by making excerpt lookup, structured hits, and provenance payloads deterministic enough to unblock downstream basket promotion and workflow cards.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in the reviewed implementation range.
- `fetch_excerpt` now resolves through the canonical FTS-only path and fails closed for PageIndex-only excerpt identifiers.
- Deterministic structured retrieval output remains available through the canonical engine surface for downstream workflow use.
- No retrieval code changed after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`; later commits are metadata-only packet refreshes.

## Thread Kickoff

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: re-emit the retrieval handoff packet with accurate traceability and demo-path mapping while preserving the reviewed implementation range above.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Removed the PageIndex fallback from `fetch_excerpt` so excerpt lookup stays on the canonical FTS-only path.
2. Added approved shared regression coverage proving PageIndex-only excerpt IDs fail closed with `KeyError`.
3. Corrected handoff traceability so the reviewed implementation range remains anchored to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
4. Added explicit canonical demo-path mapping for `retrieve relevant material` and tied the deterministic structured output to downstream basket/workflow use.

## Files Changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Metadata-only handoff files

- `8f6fbb02309502159aac91a30d1fd6f0dcea114c`: `THREAD_PACKET.md`
- `f360f73552fb5536abf9e4b74d1a8348fd54eec6`: `THREAD_PACKET.md`, `docs/gate_passed.txt`
- `307c6576ecf36031ce7bee82f076580772e5ca77`: `THREAD_PACKET.md`, `docs/gate_passed.txt`

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
- Budget note: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it remains shared/high-risk work under the 4-task cap.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Canonical demo-path step advanced

- `retrieve relevant material`
- The deterministic structured retrieval output in this slice is the concrete unblocker for promoting or gathering context into the basket later in the workflow.

### Routing/provider impact note

- None

### Proposed README.md patch text

- None
