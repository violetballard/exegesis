# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `branch-tip reviewer-fix handoff refresh`
- Current branch tip: `ab9a54d6ca4c076689e273f287925199fd0594c5`
- Reviewed implementation head: `4ec62ffecef5ee266d766cbb35ffc531cd597e60`
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..4ec62ffecef5ee266d766cbb35ffc531cd597e60`
- Reviewed branch-tip range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..ab9a54d6ca4c076689e273f287925199fd0594c5`
- Scope goal: keep the post-`adfa8cda` retrieval follow-up slice FTS-first, deterministic, and auditable on the canonical engine surface while making unsupported scoped excerpt queries fail closed.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by forcing excerpt lookup and scoped retrieval validation to stay on the canonical SQLite FTS path, preserving deterministic provenance for basket promotion and downstream workflow consumers.
- Direct handoff statement: this handoff is against the actual branch tip `ab9a54d6ca4c076689e273f287925199fd0594c5`. The retrieval behavior change in that tip is `4ec62ffecef5ee266d766cbb35ffc531cd597e60` (`fix(retrieval): fail closed on unsupported scoped queries`), and the later commits `d9dcf91cb19860de91d29d4e850312887d56c5e1`, `0038073fac1dfebef0c643769784c22f59bcbc92`, and `ab9a54d6ca4c076689e273f287925199fd0594c5` are packet/docs-only follow-up commits after that implementation head.
- Approved exception surface: one approved shared test edit in `tests/unit/test_unified_retrieval.py` only; no integrator-locked files and no other shared-by-approval files are part of the reviewed implementation slice.

## Scope Completed

- The post-`adfa8cda` retrieval follow-up slice remains FTS-first and deterministic across the current engine retrieval tree.
- `4ec62ffecef5ee266d766cbb35ffc531cd597e60` adds fail-closed handling for unsupported scoped excerpt queries in `src/qual/engine/retrieval/fts_strategy.py`.
- `tests/unit/test_unified_retrieval.py` preserves the approved shared regression coverage for the canonical retrieval contract in the same reviewed slice.
- The reviewed implementation range for this handoff is `adfa8cdadd43747ffbcb612e4151e262b13e52ca..4ec62ffecef5ee266d766cbb35ffc531cd597e60`, and the reviewed branch-tip range is `adfa8cdadd43747ffbcb612e4151e262b13e52ca..ab9a54d6ca4c076689e273f287925199fd0594c5`.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: regenerate the retrieval handoff so it matches the actual branch tip, truthfully includes `4ec62ffecef5ee266d766cbb35ffc531cd597e60` in the reviewed implementation range, and keeps the shared/high-risk classification explicit.
- Risk reason: the reviewed slice includes the approved shared regression edit in `tests/unit/test_unified_retrieval.py`, so the packet must follow the high-risk/shared budget class.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Kept the engine-facing retrieval facade FTS-first across the post-`adfa8cda` follow-up slice.
2. Preserved deterministic payload, provenance, facade-export, and sparse-bundle retrieval behavior in the reviewed implementation range.
3. Added fail-closed behavior for unsupported scoped excerpt queries in `src/qual/engine/retrieval/fts_strategy.py` with approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
4. Regenerated the visible handoff artifact so it describes the actual branch tip, reviewed implementation head, canonical demo-path step, and shared/high-risk classification truthfully.

## Files Changed

### Reviewed implementation files

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Metadata-only handoff files

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
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
- Residual risk: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are read-only in this environment, so the visible repo-root handoff is corrected here but the mirrored hidden packet files could not be rewritten from this worktree.
- Blockers: hidden `.codex/**` packet paths reject writes with `Operation not permitted` in this environment.
- Budget note: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it remains shared/high-risk work under the `4`-task cap and outside the low-risk owned-path-only budget class.

## Required Handoff Fields

- Roadmap item(s) affected: `Milestone 3: Real workflow loop`, `feat-retrieval-fts` as a narrow retrieval-contract slice rather than as lane completion
- Vision capability affected: `2. Retrieval-first context handling`, `6. Auditable state and workflow`
- Routing/provider impact note: `None`
- Canonical demo-path step advanced: `retrieve relevant material`; forcing scoped excerpt lookup to stay on the authoritative FTS-first path strengthens deterministic excerpt retrieval on that step without claiming broader workflow progress.
- Ownership/risk classification: `shared-by-approval only`; the reviewed slice includes one approved shared test edit in `tests/unit/test_unified_retrieval.py` and includes no integrator-locked edits.
- Proposed README.md patch text: `None`
