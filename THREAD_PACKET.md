# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before this fixer commit: `b74c4330906db2bb660d96987ae4f75a0663cb4b`
- Reviewed implementation head before this fixer commit: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewer-facing packet sources refreshed in this fixer pass: `THREAD_PACKET.md`, `docs/gate_passed.txt`
- Blocked packet mirror files in this fixer pass: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`
- Mirror write attempt result in this session: `not writable`
- Canonical demo-path step advanced: `retrieve relevant material`
- Demo-path sentence: This handoff makes `retrieve relevant material` more real by ensuring the canonical excerpt lookup surface is FTS-only and auditable for downstream engine use through deterministic provenance on the engine retrieval surface.

## Scope Goal

- Return this lane for re-review with a truthful packet that matches the current packet-refresh branch tip `b74c4330906db2bb660d96987ae4f75a0663cb4b`, the actual reviewed implementation tip `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, the shared/high-risk scope, the precise ownership distinction between approved shared and integrator-locked edits, and the canonical demo-path step it advances.

## Scope Completed

- SQLite FTS remains the primary retrieval path for the reviewed range, with PageIndex and embeddings staying compatibility-only fallback shims.
- The canonical retrieval query constructor and `retrieve_auto` helper are exported through both retrieval facades, and retrieval payloads, provenance bundles, and hit snapshots stay deterministic for downstream engine flows.
- Sparse source and context bundles rehydrate deterministically, and `fetch_excerpt` stays on the canonical FTS-only excerpt path so PageIndex-only excerpt IDs fail closed under shared regression coverage.
- Direct retrieval constraint booleans are normalized on the canonical surface: boolean `max_results` is rejected, and `require_citations` plus `prefer_exact_matches` are canonicalized through `_optional_bool` before retrieval runs.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: regenerate the retrieval handoff against the current packet-refresh branch tip, keep the shared/high-risk classification coherent, and map the reviewed slice to the canonical demo path.
- Risk reason: the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so this remains shared/high-risk work under `AGENTS.md`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Regenerate the packet against the current packet-refresh branch tip `b74c4330906db2bb660d96987ae4f75a0663cb4b` while explicitly keeping the real reviewed implementation tip `adfa8cdadd43747ffbcb612e4151e262b13e52ca` inside the reviewed range and scope summary.
2. Keep the handoff consistently classified as shared/high-risk work under the `4`-task cap because `tests/unit/test_unified_retrieval.py` is shared-by-approval.
3. Tighten the ownership wording so approved shared test coverage is called out separately from integrator-locked edits while keeping the explicit canonical demo-path mapping that states this lane advances `retrieve relevant material` by ensuring the canonical excerpt lookup surface is FTS-only and auditable for downstream engine use through deterministic provenance on the engine retrieval surface.
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

- `plan complete`: the handoff was re-scoped to the current packet-refresh branch tip `b74c4330906db2bb660d96987ae4f75a0663cb4b`, the actual reviewed implementation tip `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, the approved shared test-edit classification, the explicit no-integrator-locked-edits note, and the explicit canonical demo-path step `retrieve relevant material` with the required FTS-only excerpt/provenance wording.
- `before risky/shared file edit`: the shared/high-risk boundary was called out before packet edits because the reviewed range still includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `first green tests`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed on the refreshed handoff state.
- `ready for handoff`: the writable handoff artifacts agree on the packet-refresh branch tip `b74c4330906db2bb660d96987ae4f75a0663cb4b`, the reviewed head `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, the reviewed range, the shared/high-risk classification, the ownership distinction, and the canonical demo-path mapping. The `.codex` mirrors remain blocked by permissions in this session.

## Tasks Completed

1. Restamped the handoff artifacts to the current packet-refresh branch tip `b74c4330906db2bb660d96987ae4f75a0663cb4b` while keeping the real reviewed implementation tip `adfa8cdadd43747ffbcb612e4151e262b13e52ca` inside the cumulative reviewed range.
2. Reconciled the packet budget/risk classification so the handoff consistently reads as shared/high-risk work under the `4`-task cap.
3. Tightened the ownership wording so approved shared test coverage is called out separately from integrator-locked edits, and kept the explicit canonical demo-path mapping showing that this lane advances `retrieve relevant material` by ensuring the canonical excerpt lookup surface is FTS-only and auditable for downstream engine use through deterministic provenance on the engine retrieval surface.
4. Re-ran the required local gates and recorded the outcomes on the refreshed packet state.

## Files Changed

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- Approved shared test coverage in `tests/unit/test_unified_retrieval.py` remains the reason this handoff is capped at `4` tasks; no integrator-locked files are part of the reviewed implementation range.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain blocked in this session; both report `not writable`.

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

- Approved shared test edit in reviewed range: `YES` (`tests/unit/test_unified_retrieval.py`)
- Integrator-locked edit in reviewed range: `NO`
- The reviewed implementation range is cumulative through `adfa8cdadd43747ffbcb612e4151e262b13e52ca`; the pre-fix packet-refresh branch tip for this pass is `b74c4330906db2bb660d96987ae4f75a0663cb4b`, and this fixer commit only refreshes packet metadata on top of that reviewed tip.
