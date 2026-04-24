# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `branch-tip reviewer-fix handoff refresh`
- Current branch tip before fixer commit: `141b2168208d78cbd25bc8fd63fcdbc34e6aa958`
- Reviewed implementation head: `141b2168208d78cbd25bc8fd63fcdbc34e6aa958`
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..141b2168208d78cbd25bc8fd63fcdbc34e6aa958`
- Scope goal: regenerate the handoff against the actual branch tip so review covers the real retrieval implementation and packet state now present on this merge candidate.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this branch-tip slice advances `retrieve relevant material` by keeping the engine retrieval path FTS-first, preserving deterministic retrieval payload and provenance state for basket-promotion inputs, and failing closed on unsupported excerpt and scoped-query requests.
- Direct handoff statement: this handoff now covers the real branch tip. It does not claim that post-`adfa8cda` retrieval commits are metadata-only.

## Scope Completed

- Localized and delegated the canonical retrieval query builder through the engine-facing retrieval facade so the retrieval path stays on one believable engine entrypoint.
- Expanded retrieval payload, provenance, citation, source-bundle, context-bundle, and basket-promotion normalization so downstream consumers receive deterministic state.
- Hardened the SQLite FTS strategy and excerpt lookup surface to fail closed for unsupported, orphaned, deferred, noncanonical, and scoped-query cases while keeping FTS authoritative.
- Extended approved shared regression coverage in `tests/unit/test_unified_retrieval.py` across the branch-tip retrieval surface.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the handoff packet so it matches the actual merge candidate and explicitly states the canonical demo-path step advanced.
- Risk reason: the reviewed slice includes shared-by-approval edits in `tests/unit/test_unified_retrieval.py` and spans substantive retrieval changes across multiple facade, strategy, payload, and test files.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Reissued the handoff against the actual reviewed range `adfa8cda..141b2168` instead of describing later retrieval commits as metadata-only.
2. Recomputed the scope summary, reviewed file list, and risk classification against the real branch-tip implementation state.
3. Added the explicit canonical demo-path statement that this work advances `retrieve relevant material`.
4. Re-ran the required local gates for the corrected reviewed tip and recorded the results below.

## Files Changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `tests/unit/test_unified_retrieval.py`

### Handoff artifact files refreshed in this fixer pass

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

### Handoff artifact files that remain stale in this worktree

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- Blocker: `This worktree cannot write .codex/kickoff_packets/feat-retrieval-fts.md or .codex/lane_meta/feat-retrieval-fts.json` (`operation not permitted`), so those packet mirrors still describe the stale narrowed slice.`
- Fixer pass note: `2026-04-24 visible handoff rerun confirmed the corrected branch-tip slice and revalidated all required local gates against HEAD 141b2168208d78cbd25bc8fd63fcdbc34e6aa958.`
- Budget classification: shared/high-risk because `tests/unit/test_unified_retrieval.py` is a shared-by-approval file in the reviewed slice.
- Budget status: over the normal high-risk autonomy window for a single handoff slice. The reviewed range touches `13` files total (`9` implementation files plus `4` handoff artifacts) with `10976` insertions and `1132` deletions, so this must be reviewed as a cumulative branch-tip handoff rather than a narrow 4-task packet-only refresh.

## Required Handoff Fields

- Roadmap item(s) affected: `Milestone 3: Real workflow loop`, `feat-retrieval-fts`
- Vision capability affected: `Retrieval-first context handling`, `Auditable state and workflow`
- Routing/provider impact note: `None`
- Canonical demo-path step advanced: `retrieve relevant material`
- Ownership/risk classification: `shared-by-approval`; the reviewed slice includes shared test coverage in `tests/unit/test_unified_retrieval.py` and no integrator-locked files.
- Proposed `README.md` patch text: `None`
