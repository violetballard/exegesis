# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Scope goal: harden the Milestone 3 retrieval contract on the canonical retrieval surface by keeping the canonical FTS-first retrieval path deterministic and by rejecting PageIndex-only excerpt IDs on the public excerpt lookup path.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by hardening the Milestone 3 retrieval contract around the canonical retrieval surface: SQLite FTS stays authoritative, PageIndex-only excerpt IDs are rejected on the public excerpt lookup path, and the structured hit/provenance payloads stay deterministic enough to unblock downstream basket promotion and workflow cards.
- Direct handoff statement: this handoff advances the canonical demo-path step `retrieve relevant material` by hardening the Milestone 3 retrieval contract on the canonical retrieval surface and rejecting PageIndex-only excerpt IDs on that public excerpt lookup path.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in the reviewed implementation range.
- This slice hardens the Milestone 3 retrieval contract on the canonical retrieval surface by making `fetch_excerpt` resolve through the canonical FTS-only path and fail closed for PageIndex-only excerpt identifiers.
- Deterministic structured retrieval output remains available through the canonical engine surface for downstream workflow use.
- No retrieval code changed after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`; later commits are metadata-only packet refreshes.

## Thread Kickoff

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: re-emit the retrieval handoff packet with accurate traceability and explicit Milestone 3 retrieval-contract wording while preserving the reviewed implementation range above.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Removed the PageIndex fallback from `fetch_excerpt` so excerpt lookup stays on the canonical FTS-only path.
2. Added approved shared regression coverage proving PageIndex-only excerpt IDs fail closed with `KeyError`.
3. Corrected handoff traceability so the reviewed implementation range remains anchored to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
4. Added explicit canonical demo-path mapping for `retrieve relevant material` and stated plainly that this slice hardens the Milestone 3 retrieval contract by rejecting PageIndex-only excerpt IDs on the canonical retrieval surface.

## Files Changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Metadata-only handoff files

- `8f6fbb02309502159aac91a30d1fd6f0dcea114c`: `THREAD_PACKET.md`
- `f360f73552fb5536abf9e4b74d1a8348fd54eec6`: `THREAD_PACKET.md`, `docs/gate_passed.txt`
- `307c6576ecf36031ce7bee82f076580772e5ca77`: `THREAD_PACKET.md`, `docs/gate_passed.txt`
- `f2c2cbd90bc3b5b5d062911296cb9b8d13a9c6d6`: `THREAD_PACKET.md`, `docs/gate_passed.txt`

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
