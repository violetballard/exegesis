# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix handoff refresh`
- Actual branch tip: `ab9a54d6ca4c076689e273f287925199fd0594c5`
- Reviewed implementation head: `4ec62ffecef5ee266d766cbb35ffc531cd597e60`
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..4ec62ffecef5ee266d766cbb35ffc531cd597e60`
- Scope goal: keep the post-`adfa8cda` retrieval follow-up slice FTS-first, deterministic, and auditable by failing closed on unsupported scoped-query payloads
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice makes `retrieve relevant material` more real by forcing excerpt lookup and scoped-query handling to resolve only through supported canonical FTS requests, preserving deterministic provenance for later basket-promotion and downstream workflow use
- Direct handoff statement: this refreshed packet now matches the actual branch state the reviewer called out. `4ec62ffecef5ee266d766cbb35ffc531cd597e60` is reviewed retrieval code and test behavior, while only the later packet commits `d9dcf91c90ee421f2f383c316af02e5aa5af7551` and `ab9a54d6ca4c076689e273f287925199fd0594c5` are metadata-only.
- Approved exception surface: one approved shared test edit in `tests/unit/test_unified_retrieval.py` only. No integrator-locked files and no other shared-by-approval files are part of the reviewed implementation slice.

## Scope Completed

- Kept SQLite FTS authoritative through the engine retrieval facade while making unsupported scoped-query payloads fail closed instead of running as canonical FTS requests.
- Preserved deterministic retrieval provenance on the canonical engine surface so downstream basket-promotion and workflow consumers only see supported FTS-backed state.
- Added matching shared regression coverage in `tests/unit/test_unified_retrieval.py` for the unsupported scoped-query behavior.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: regenerate the retrieval handoff against the actual post-`adfa8cda` branch state so the reviewed slice truthfully includes `4ec62ffecef5ee266d766cbb35ffc531cd597e60`
- Risk reason: the reviewed slice includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the handoff remains shared/high-risk work

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Tightened `src/qual/engine/retrieval/fts_strategy.py` so unsupported scoped queries fail closed instead of running through the canonical FTS strategy path.
2. Updated the shared regression file `tests/unit/test_unified_retrieval.py` to cover the unsupported scoped-query behavior on the canonical retrieval surface.
3. Regenerated the handoff packet so the reviewed implementation head, reviewed range, file list, and traceability notes all match the actual branch state.

## Files Changed

### Reviewed implementation files

- `src/qual/engine/retrieval/fts_strategy.py`
- `tests/unit/test_unified_retrieval.py`

### Metadata-only handoff files

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- Residual risk: approval should review the actual branch tip `ab9a54d6ca4c076689e273f287925199fd0594c5`, but evaluate retrieval behavior against the reviewed implementation head `4ec62ffecef5ee266d766cbb35ffc531cd597e60` and the narrow range `adfa8cdadd43747ffbcb612e4151e262b13e52ca..4ec62ffecef5ee266d766cbb35ffc531cd597e60`
- Blockers: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are sandbox-protected in this worktree, so this fixer pass could not rewrite those mirrored packet files

## Required Handoff Fields

- Roadmap item(s) affected: `Milestone 3: Real workflow loop`, `feat-retrieval-fts` as the authoritative retrieval path feeding engine workflow state
- Vision capability affected: `2. Retrieval-first context handling`, `6. Auditable state and workflow`
- Routing/provider impact note: `None`
- Canonical demo-path step advanced: `retrieve relevant material`
- Ownership/risk classification: `shared-by-approval only`; the reviewed slice includes one approved shared test edit in `tests/unit/test_unified_retrieval.py` and no integrator-locked edits
- Proposed README.md patch text: `None`
