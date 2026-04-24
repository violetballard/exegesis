# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before this fixer commit: `3a7f478b243e5e6e23c46a9bedea7f782defd497`
- Reviewed implementation head: `4387c7277d8d983012d970312a6bcc14f6fb571d`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..4387c7277d8d983012d970312a6bcc14f6fb571d`
- Packet traceability note: the current branch tip before this fixer pass is `3a7f478b243e5e6e23c46a9bedea7f782defd497`, which is a metadata-only packet refresh on top of the substantive retrieval commit `4387c7277d8d983012d970312a6bcc14f6fb571d`. Re-review this lane against the true merge candidate range above. The post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval commit `4387c7277d8d983012d970312a6bcc14f6fb571d fix(retrieval): canonicalize hit provenance strategy metadata` is in-scope implementation, not metadata-only.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: this lane advances `retrieve relevant material` by keeping SQLite FTS authoritative across retrieval execution, excerpt lookup, and provenance payload rehydration so engine flows consume canonical retrieval state instead of PageIndex-only fallbacks.
- Approved shared regression exception: `tests/unit/test_unified_retrieval.py` remains the only shared-by-approval regression surface in the reviewed implementation range.
- Packet authority note: `THREAD_PACKET.md` is the corrected reviewer-fix artifact for this pass. The `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` mirrors remain stale in this environment because sandbox writes to `.codex/**` are blocked with `operation not permitted`.

## Scope Goal

- Complete the FTS-first retrieval MVP handoff for the actual current merge candidate and correct packet traceability so review scope matches the live branch tip.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: regenerate the handoff packet against the true merge candidate instead of the stale narrowed slice.
- Risk reason: this lane includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, and the packet previously misrepresented the reviewed retrieval head after a later live code commit landed.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Re-anchor the reviewed implementation head/range to the true merge candidate `378cf9a74a3658058079a32f186fcd254c4a4034..4387c7277d8d983012d970312a6bcc14f6fb571d`.
2. Correct the packet traceability note so `4387c7277d8d983012d970312a6bcc14f6fb571d` is listed as in-scope retrieval implementation.
3. Re-list `Scope completed`, `Files changed`, and `Tasks completed` against the true merge candidate.
4. Re-run `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`, then record the outcomes.

## Scope Completed

- The true merge candidate `378cf9a74a3658058079a32f186fcd254c4a4034..4387c7277d8d983012d970312a6bcc14f6fb571d` keeps retrieval FTS-first for the MVP: engine and service facades export the canonical retrieval helpers, FTS strategy execution and cache/query normalization are hardened for canonical vault/doc scopes, payloads and provenance snapshots are deterministic for downstream engine flows, sparse source and context bundles rehydrate consistently, basket-promotion and excerpt-lookup metadata stay canonical, and excerpt lookup now fails closed on non-FTS/PageIndex-only paths under shared regression coverage.

## Reviewed Scope Boundary

- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..4387c7277d8d983012d970312a6bcc14f6fb571d`
- Current metadata-only branch tip before this fixer pass: `3a7f478b243e5e6e23c46a9bedea7f782defd497`
- Substantive post-review retrieval commit now included in scope:
- `4387c7277d8d983012d970312a6bcc14f6fb571d fix(retrieval): canonicalize hit provenance strategy metadata`

## Tasks Completed

1. Hardened the FTS-first retrieval path by exporting canonical retrieval helpers through the service and engine facades, guarding unsupported scopes, and keeping PageIndex/embeddings fallback-only and fail-closed.
2. Canonicalized retrieval payloads, provenance bundles, hit snapshots, and excerpt/basket-promotion metadata so downstream engine flows consume deterministic audit-friendly state.
3. Rehydrated sparse source/context bundle fields and preserved canonical query, policy, citation, and strategy metadata across excerpt lookup and basket promotion flows.
4. Expanded regression coverage in `tests/unit/test_unified_retrieval.py` and `tests/unit/test_packet_planner.py`, and kept the packet planner aligned with cumulative reviewed-range handoffs.

## Files Changed

- Files in the true merge candidate `378cf9a74a3658058079a32f186fcd254c4a4034..4387c7277d8d983012d970312a6bcc14f6fb571d`:
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

## Reviewer Fix Closure

1. The reviewed implementation head/range now match the true merge candidate: `378cf9a74a3658058079a32f186fcd254c4a4034..4387c7277d8d983012d970312a6bcc14f6fb571d`.
2. The traceability note now treats `4387c7277d8d983012d970312a6bcc14f6fb571d` as in-scope retrieval implementation instead of calling everything after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` metadata-only.
3. `Scope completed`, `Files changed`, and `Tasks completed` are re-listed against the true merge candidate rather than the stale narrowed slice.
4. This handoff explicitly states that it advances the canonical demo-path step `retrieve relevant material`.
5. Required gates were re-run and recorded against the true merge candidate.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: sandbox policy prevented updating `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` (`operation not permitted`), so `THREAD_PACKET.md` is the corrected source of truth for this fixer pass.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: retrieval/search

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
