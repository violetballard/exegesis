# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `branch-tip cumulative retrieval handoff`
- Reviewed implementation head: `e5d20f4012eed3c1e12e9acea2737e1e03dad50b`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..e5d20f4012eed3c1e12e9acea2737e1e03dad50b`
- Packet refresh note: the final fixer commit for this handoff is metadata-only and restamps these packet mirrors after the cumulative retrieval range above.

## Scope Goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt, provenance, and handoff output on the actual branch tip.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path across the cumulative lane range, and excerpt lookup stays fail-closed on the canonical FTS path instead of promoting PageIndex or embeddings to required runtime paths.
- Retrieval payloads, lookup snapshots, sparse bundles, provenance mirrors, and query-context fields are normalized deterministically for downstream engine and basket consumers, including direct-constraint normalization and mirrored lookup/backfill context.
- The canonical retrieval query constructor and FTS policy metadata are exported through both retrieval facades, while the engine-side FTS strategy rejects invalid binary query metadata and guards candidate-doc-id inputs.
- Handoff plumbing was updated on this branch so planner-generated packets can carry canonical demo-path metadata and the tracked packet mirrors now truthfully describe the actual reviewed branch-tip range.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`
- This cumulative branch makes `retrieve relevant material` more real by keeping retrieval FTS-first, preserving deterministic payload and provenance fields, and ensuring excerpt/query metadata stays auditable and structured for downstream basket promotion and workflow use.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: finish the FTS-first retrieval MVP and restamp the branch-tip handoff packet so it matches the code actually present on the branch.
- Risk reason: the cumulative branch includes shared regression coverage and shared packet-plumbing edits outside lane-owned retrieval paths.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Trace the actual cumulative branch-tip retrieval range and identify code-bearing commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. Regenerate the tracked handoff packet so it names the actual reviewed implementation head and cumulative file set.
3. Restate roadmap, vision, and canonical demo-path mapping against the real branch-tip range.
4. Re-run the required local gates and hand off the refreshed packet.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## AGENTS Checkpoint Evidence

- `plan complete`: traced the actual post-`adfa8c` branch history and confirmed `e5d20f4` is code-bearing retrieval work, not metadata-only packet churn.
- `first green tests`: the required lane gates were re-run on the current branch tip for this packet restamp.
- `before risky/shared file edit`: this fixer pass only refreshed the tracked handoff mirrors, but it acknowledges the cumulative shared packet-plumbing and shared-test edits already present in the reviewed range.
- `ready for handoff`: the packet now explicitly maps the real branch-tip range to `retrieve relevant material` and truthfully lists the cumulative files and scope.

## Tasks Completed

1. Kept retrieval FTS-first while hardening excerpt lookup, query metadata normalization, direct-constraint normalization, and deterministic retrieval payload/provenance mirrors across the cumulative lane range.
2. Exported the canonical retrieval query constructor and FTS policy metadata through the retrieval facades, while preserving deferred PageIndex and embeddings behavior as compatibility-only paths.
3. Updated the engine-side FTS strategy and payload helpers to reject invalid binary query metadata, guard candidate-doc-id inputs, and preserve mirrored query context for lookup/backfill payloads.
4. Updated the handoff planner plumbing and packet mirrors so branch-tip review packets include the canonical demo-path field and accurately restamp the actual reviewed implementation range.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/init_lane_meta.py`
- `codex_packet_handoff/tools/planner.py`
- `docs/gate_passed.txt`
- `docs/retrieval_post_adfa_commit_accounting.md`
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
- Blockers: none
- The reviewed branch range is cumulative and includes shared handoff-plumbing files plus approved shared regression coverage, so integration should review the cumulative file list rather than the earlier narrowed `adfa8c` slice.
- This fixer pass itself is metadata-only; the code-bearing reviewed head remains `e5d20f4012eed3c1e12e9acea2737e1e03dad50b`.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md: Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: retrieval/search

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Approved exception note: approved shared regression coverage in `tests/unit/test_unified_retrieval.py` remains part of the reviewed range, and the cumulative branch also includes shared packet-plumbing updates needed to emit canonical demo-path metadata in handoff packets.
- Retrieval remains FTS-first; PageIndex and embeddings stay deferred or compatibility-only and are not promoted to required MVP paths.
