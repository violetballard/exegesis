# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix branch-tip restamp`
- Pre-fix branch tip restamped by this packet pass: `b31db490a635fe5c7195cb2ce173b09a838ad8ab`
- Reviewed implementation head before this fixer commit: `b31db490a635fe5c7195cb2ce173b09a838ad8ab`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..b31db490a635fe5c7195cb2ce173b09a838ad8ab`
- Previous reviewer-missed head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewer-facing packet sources refreshed in this fixer pass: `THREAD_PACKET.md`, `docs/gate_passed.txt`, `docs/retrieval_post_adfa_commit_accounting.md`
- Blocked packet mirror files in this fixer pass: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`
- Mirror write attempt result in this session: `not writable in sandbox`
- Canonical demo-path step advanced: `retrieve relevant material`
- Demo-path sentence: This handoff makes `retrieve relevant material` more real by keeping excerpt lookup on the canonical SQLite FTS path and preserving deterministic provenance for downstream engine retrieval consumers.

## Scope Goal

- Return this lane for re-review with a truthful packet that matches the actual branch tip `b31db490a635fe5c7195cb2ce173b09a838ad8ab` and an auditable post-`adfa8cdadd` commit ledger.

## Scope Completed

- SQLite FTS remains the primary retrieval path for the reviewed range, with PageIndex and embeddings preserved only as compatibility/fallback shims.
- The retrieval and engine facades keep the canonical query, payload, and provenance surfaces wired for downstream engine flows.
- The canonical excerpt lookup path stays FTS-only, so non-FTS/PageIndex-only excerpt requests fail closed under the reviewed shared regression coverage.
- Direct retrieval constraint normalization remains on the canonical retrieval surface.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: regenerate the retrieval handoff against the actual branch tip and replace the stale traceability note with exact post-`adfa8cdadd` commit accounting.
- Risk reason: approved shared regression coverage in `tests/unit/test_unified_retrieval.py` keeps this lane shared/high-risk under `AGENTS.md`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Restamp the handoff packet to the actual pre-fix branch tip `b31db490a635fe5c7195cb2ce173b09a838ad8ab`.
2. Replace the old adfa-only traceability note with exact post-`adfa8cdadd` commit accounting.
3. Add the explicit canonical demo-path step field and retrieval sentence, and sync every writable handoff artifact.
4. Re-run `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

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

- `plan complete`: the packet was re-scoped to the actual pre-fix branch tip `b31db490a635fe5c7195cb2ce173b09a838ad8ab` and the retrieval demo-path step was made explicit.
- `before risky/shared file edit`: the shared/high-risk boundary was called out before touching packet files because `tests/unit/test_unified_retrieval.py` remains in the reviewed range.
- `first green tests`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed on the restamped packet state.
- `ready for handoff`: the writable handoff artifacts now agree on the actual pre-fix branch tip, the exact post-adfa ledger, the retrieval demo-path mapping, and the green gate results; the `.codex` mirrors remain blocked by sandbox write restrictions.

## Exact Post-adfa Commit Accounting

- Previous reviewer-missed head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Runtime/test commits after `adfa8cdadd`: `265`
- Metadata-only commits after `adfa8cdadd`: `678`
- Exact ledger document: `docs/retrieval_post_adfa_commit_accounting.md`
- Runtime/test files touched after `adfa8cdadd`: `codex_packet_handoff/tools/init_lane_meta.py`, `codex_packet_handoff/tools/planner.py`, `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/embeddings_strategy.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/interface.py`, `src/qual/engine/retrieval/pageindex_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/engine/tools/excerpt_tools.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, `tests/unit/test_packet_planner.py`, `tests/unit/test_unified_retrieval.py`
- Metadata-only filesets after `adfa8cdadd`: [.codex/kickoff_packets/feat-retrieval-fts.md, .codex/lane_meta/feat-retrieval-fts.json, THREAD_PACKET.md], [THREAD_PACKET.md], [docs/gate_passed.txt], [THREAD_PACKET.md, docs/gate_passed.txt]

## Tasks Completed

1. Restamped the handoff artifacts to the actual pre-fix branch tip `b31db490a635fe5c7195cb2ce173b09a838ad8ab` instead of the older `adfa8cdadd43747ffbcb612e4151e262b13e52ca` reviewer anchor.
2. Replaced the stale traceability note with exact post-`adfa8cdadd` commit accounting in the writable docs packet.
3. Added the explicit canonical demo-path step field naming `retrieve relevant material` and a sentence describing the FTS-only excerpt path impact.
4. Updated the writable handoff artifacts and recorded the blocked `.codex` mirror writes accurately for this sandbox.

## Files Changed

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`
- `docs/retrieval_post_adfa_commit_accounting.md`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- Approved shared test coverage in `tests/unit/test_unified_retrieval.py` remains the reason this handoff stays under the `4`-task high-risk cap.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are readable but not writable in this sandbox, so their stale contents could not be refreshed in this pass.

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
- The handoff now matches the actual pre-fix branch tip `b31db490a635fe5c7195cb2ce173b09a838ad8ab`; the prior packet was incorrect to stop at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
