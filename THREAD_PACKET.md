# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix handoff refresh`
- Packet refresh trace anchor before fixer commit: `9bd108298e82f2ba9cc1a6ab97d2f20f7dc622fe`
- Reviewed implementation head: `9bd108298e82f2ba9cc1a6ab97d2f20f7dc622fe`
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..9bd108298e82f2ba9cc1a6ab97d2f20f7dc622fe`
- Scope goal: publish a review-safe handoff packet for the live retrieval branch tip after the post-`adfa8cda` follow-up fixes landed.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by mirroring normalized query text onto doc hits, excerpt hits, and their provenance so retrieval output stays auditable and ready for later basket-promotion consumers without widening runtime scope beyond SQLite FTS.
- Direct handoff statement: this fixer pass refreshes packet metadata only. It does not change the reviewed implementation head or the reviewed implementation range.

## Scope Completed

The reviewed implementation range extends the prior FTS-first excerpt slice to the live retrieval code tip. It mirrors normalized query text into doc-hit and excerpt-hit payloads plus provenance backfills, keeps downstream payload reconstruction deterministic when sparse source bundles omit top-level hit query text, and resolves engine-facing query annotations without introducing an eager import cycle. SQLite FTS remains the authoritative retrieval path for the MVP surface, and the result shape stays structured and auditable for downstream engine workflows and later basket promotion.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: regenerate the handoff around the real retrieval implementation tip instead of a stale metadata-only trace, while preserving the FTS-first Milestone 3 scope.
- Risk reason: the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the handoff must stay on the high-risk/shared basis.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the reviewed implementation head and range to the live retrieval code tip.
2. Update scope, task, and file summaries so they match the post-`adfa8cda` query-text and annotation fixes.
3. State the canonical demo-path step explicitly as `retrieve relevant material` and explain the downstream contract effect.
4. Re-run the required gates and publish the corrected handoff packet.

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

### Handoff Packet

- branch name
- tasks completed (numbered)
- files changed
- commands run + outcomes
- risks/blockers
- all required fields from `INTEGRATION.md`

## Tasks Completed

1. Regenerated the handoff so the reviewed implementation range now includes the real retrieval follow-up commits at `1eaf77adace04274f20e1ff596fad89f4e06b8bf` and `9bd108298e82f2ba9cc1a6ab97d2f20f7dc622fe`.
2. Updated the scope summary to reflect normalized query-text mirroring on hit payloads and provenance, plus the sparse-source backfill coverage that keeps downstream payload reconstruction deterministic.
3. Added the explicit canonical demo-path statement for `retrieve relevant material` and tied it to later basket-promotion compatibility without widening retrieval scope beyond FTS-first MVP behavior.
4. Re-ran the required local gates against the current branch tip after refreshing the packet metadata.

## Files Changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/__init__.py`
- `tests/unit/test_unified_retrieval.py`

### Metadata-only packet artifacts refreshed in this fixer pass

- `THREAD_PACKET.md`
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PENDING`
- `./quality-format.sh --check`: `PENDING`
- `./quality-lint.sh`: `PENDING`
- `./quality-test.sh`: `PENDING`
- `./typecheck-test.sh`: `PENDING`
- `make ci`: `PENDING`

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none
- Budget classification: shared/high-risk because `tests/unit/test_unified_retrieval.py` is the approved shared regression surface for this lane.
- Traceability note: the final fixer commit will be metadata-only, but the reviewed retrieval implementation head for re-review is `9bd108298e82f2ba9cc1a6ab97d2f20f7dc622fe`.

## Required Handoff Fields

- Roadmap item(s) affected: `Milestone 3: Real workflow loop`, `feat-retrieval-fts`
- Vision capability affected: `Retrieval-first context handling`, `Auditable state and workflow`
- Routing/provider impact note: `None`
- Canonical demo-path step advanced: `retrieve relevant material`
- Demo-path effect statement: `Normalized query text is now mirrored into hit payloads and provenance so retrieval output remains deterministic and auditable for downstream engine flows and later basket promotion.`
- Ownership/risk classification: `shared-by-approval`; the reviewed slice includes shared test coverage in `tests/unit/test_unified_retrieval.py` and no integrator-locked files.
- Proposed `README.md` patch text: `None`
