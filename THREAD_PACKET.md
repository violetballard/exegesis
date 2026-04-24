# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before this fixer commit: `72a65689bc806e3f33afa9f28e87c827020e5021`
- Reviewed implementation head before this fixer commit: `72a65689bc806e3f33afa9f28e87c827020e5021`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..72a65689bc806e3f33afa9f28e87c827020e5021`
- Reviewer-facing packet sources refreshed in this fixer pass: `THREAD_PACKET.md`, `docs/gate_passed.txt`
- Blocked packet mirror files in this fixer pass: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`
- Mirror write attempt result in this session: `operation not permitted`
- Canonical demo-path step advanced: `retrieve relevant material`
- Demo-path sentence: This handoff makes the "retrieve relevant material" step more real by keeping retrieval FTS-first, hardening deterministic payload and provenance shaping on the canonical retrieval surface, and normalizing direct constraint booleans before retrieval executes.

## Scope Goal

- Return this lane for re-review with a truthful packet that matches the actual reviewed implementation tip `72a65689bc806e3f33afa9f28e87c827020e5021`, the shared/high-risk scope, and the canonical demo-path step it advances.

## Scope Completed

- SQLite FTS remains the primary retrieval path for the reviewed range, with PageIndex and embeddings staying compatibility-only fallback shims.
- The canonical retrieval query constructor and `retrieve_auto` helper are exported through both retrieval facades, and retrieval payloads, provenance bundles, and hit snapshots stay deterministic for downstream engine flows.
- Sparse source and context bundles rehydrate deterministically, and `fetch_excerpt` stays on the canonical FTS-only excerpt path so PageIndex-only excerpt IDs fail closed under shared regression coverage.
- Direct retrieval constraint booleans are normalized on the canonical surface: boolean `max_results` is rejected, and `require_citations` plus `prefer_exact_matches` are canonicalized through `_optional_bool` before retrieval runs.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: regenerate the retrieval handoff against the actual reviewed tip, keep the shared/high-risk classification coherent, and map the reviewed slice to the canonical demo path.
- Risk reason: the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so this remains shared/high-risk work under `AGENTS.md`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Regenerate the packet against the real reviewed implementation tip `72a65689bc806e3f33afa9f28e87c827020e5021` and include that tip in the reviewed range and scope summary.
2. Keep the handoff consistently classified as shared/high-risk work under the `4`-task cap because `tests/unit/test_unified_retrieval.py` is shared-by-approval.
3. Add an explicit canonical demo-path mapping that states this lane advances `retrieve relevant material`.
4. Re-run `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on the refreshed packet state.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## AGENTS Checkpoint Evidence

- `plan complete`: the handoff was re-scoped to the actual reviewed implementation tip `72a65689bc806e3f33afa9f28e87c827020e5021`, the shared/high-risk classification, and the explicit canonical demo-path step.
- `before risky/shared file edit`: the shared/high-risk boundary was called out before packet edits because the reviewed range still includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `first green tests`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed on the refreshed handoff state.
- `ready for handoff`: the writable handoff artifacts now agree on the reviewed head `72a65689bc806e3f33afa9f28e87c827020e5021`, the reviewed range, the shared/high-risk classification, and the canonical demo-path mapping. The `.codex` mirror files remain blocked by `operation not permitted`.

## Tasks Completed

1. Restamped the handoff artifacts to the real reviewed implementation tip `72a65689bc806e3f33afa9f28e87c827020e5021` and its cumulative reviewed range.
2. Reconciled the packet budget/risk classification so the handoff consistently reads as shared/high-risk work under the `4`-task cap.
3. Added the explicit canonical demo-path mapping showing that this lane advances `retrieve relevant material`.
4. Re-ran the required local gates and recorded the outcomes on the refreshed packet state.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/init_lane_meta.py`
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
- Shared regression coverage in `tests/unit/test_unified_retrieval.py` remains the reason this handoff is capped at `4` tasks.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain blocked in this session; write attempts fail with `operation not permitted`.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: retrieval/search

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared-by-approval edits in reviewed range: `YES` (`tests/unit/test_unified_retrieval.py`)
- Integrator-locked edits in reviewed range: `NO`
- The reviewed implementation range is cumulative through `72a65689bc806e3f33afa9f28e87c827020e5021`; this fixer commit only refreshes packet metadata on top of that reviewed tip.
