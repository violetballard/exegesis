# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix packet regeneration against actual branch tip`
- Current submitted tip before this packet refresh commit: `d9542206f6fd14db37d1ddf5efd76f941d32314b`
- Reviewed implementation head: `d9542206f6fd14db37d1ddf5efd76f941d32314b`
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..d9542206f6fd14db37d1ddf5efd76f941d32314b`
- Packet traceability note: the previous packet stopped at `0bf3263d` and therefore hid a real non-metadata branch-tip change in `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py`. This packet treats the full non-metadata `adfa8cda..d9542206` diff as in-scope reviewed implementation, while still separating interleaved packet-refresh docs from product or tooling behavior changes.

## Scope goal

- Advance the canonical demo-path step `retrieve relevant material` by keeping excerpt lookup and excerpt-promotion metadata on the authoritative SQLite FTS path, and by making the packet generator emit that demo-path mapping even when lane metadata is stale.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: preserve SQLite FTS as the authoritative retrieval path while closing the reviewer-requested handoff fidelity gaps on the current branch tip.
- Risk reason: the reviewed implementation range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py` plus reviewer-fix support edits in `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Regenerate the handoff packet against the real branch tip `d9542206` instead of freezing the story at `0bf3263d`.
2. Restate the reviewed scope so it covers both the retrieval-runtime fixes and the planner/test safeguard commit that prevents the same packet omission from recurring.
3. Keep the canonical demo-path mapping explicit as `retrieve relevant material` and tie it to the actual FTS-first behavior in `src/qual/retrieval/service.py`.
4. Re-run the required gate suite on the true current tip and record the results against that exact commit.

### Early Review Triggers

- before first edit to the shared-by-approval regression file `tests/unit/test_unified_retrieval.py`
- before changing public retrieval contract wording in the handoff packet
- before changing packet-generator behavior outside the reviewer-required demo-path field backfill

### Checkpoint Status

- `plan complete`: this packet now targets the actual branch tip `d9542206` instead of the stale `0bf3263d` story.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on `d9542206`.
- `before risky/shared file edit`: the reviewed range still includes the approved shared regression file `tests/unit/test_unified_retrieval.py`; this packet refresh itself edits only handoff metadata files.
- `ready for handoff`: this packet now aligns the reviewed range, canonical demo-path step, branch-tip traceability, and gate evidence to the same real submitted tip.

## Scope completed

- Canonical demo-path step advanced: `retrieve relevant material`.
- `src/qual/retrieval/service.py` keeps `retrieve relevant material` FTS-first by failing closed when sparse excerpt payloads cannot reconstitute canonical query metadata, by clearing mirrored query fields consistently, and by deriving excerpt-promotion query metadata from the canonical query snapshot instead of stale provenance fragments.
- `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` close the reviewer-requested packet gap by making packet generation include the canonical demo-path step and impact for `feat-retrieval-fts` even when lane metadata is stale, so the same omission does not reappear on a later packet refresh.
- The reviewed runtime changes remain narrow: SQLite FTS stays authoritative, PageIndex and embeddings remain compatibility-only shims, and no routing, provider, CLI, app, or integrator-locked entrypoints are added to the retrieval surface.

## Reviewed Scope Boundary

- The reviewed implementation range is `adfa8cdadd43747ffbcb612e4151e262b13e52ca..d9542206f6fd14db37d1ddf5efd76f941d32314b`.
- Non-metadata reviewed files in that range:
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`
- Interleaved `.codex/**`, `THREAD_PACKET.md`, and `docs/gate_passed.txt` commits in the same branch window remain metadata-only packet refreshes and are not counted as reviewed implementation files.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`
- This handoff advances `retrieve relevant material` by ensuring excerpt lookup and excerpt-promotion records stay bound to canonical FTS-backed query context, which keeps downstream basket/workflow use deterministic and auditable.

## Tasks completed

1. Hardened `src/qual/retrieval/service.py` so orphaned sparse excerpt payloads fail closed on mirrored query state instead of fabricating incomplete query fingerprints or partially repaired lookup context.
2. Hardened excerpt-promotion metadata in `src/qual/retrieval/service.py` so query text, scope, intent, confidentiality profile, fingerprint, and date-range fields are rebuilt from the canonical query snapshot before promotion records are emitted.
3. Updated `codex_packet_handoff/tools/planner.py` to emit the canonical demo-path step and impact for `feat-retrieval-fts` by default, and added `tests/unit/test_packet_planner.py` coverage for both metadata-driven and stale-metadata fallback packet generation.
4. Regenerated the handoff metadata against `d9542206` and reran the required gate suite on that exact tip so the packet scope and gate evidence now refer to the same code.

## Files changed

- Non-metadata reviewed implementation files in `adfa8cdadd43747ffbcb612e4151e262b13e52ca..d9542206f6fd14db37d1ddf5efd76f941d32314b`:
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`
- Metadata-only packet-refresh files in the same branch window:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands run with results

- Gate rerun date: `2026-04-23`
- Gate rerun target: `d9542206f6fd14db37d1ddf5efd76f941d32314b`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS` (`200` tests, `OK`)
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. The packet is regenerated against the actual submitted tip `d9542206` instead of stopping at `0bf3263d`.
2. `Reviewed implementation range`, `Scope completed`, `Tasks completed`, and `Files changed` now cover the retrieval-runtime fixes plus the planner/test safeguard commit that existed at the real branch tip.
3. The canonical demo-path step advanced is stated directly as `retrieve relevant material` and is tied both to the FTS-first retrieval behavior and to the packet-generator fallback that now preserves that mapping.
4. The gate evidence section is now explicitly commit-scoped, and the full required suite passed on `d9542206`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Risks / blockers

- Risk: `HIGH`
- Residual risk: callers that relied on incomplete sparse excerpt query mirrors will now fail closed instead of receiving partially reconstructed metadata; that is the intended FTS-first contract but can expose stale callers outside this lane.
- Residual risk: the branch includes reviewer-fix support edits in packet-planner tooling outside the lane-owned retrieval paths; those changes are narrow and regression-tested, but they are still part of the reviewed tip and must stay called out explicitly.
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `ROADMAP.md: Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits in the reviewed implementation range: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` remains the sole shared-by-approval implementation file in the retrieval-runtime slice.
- Additional non-lane reviewer-fix support edits in the reviewed tip: `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py`.
- All remaining non-metadata reviewed files stay in the lane-owned retrieval paths.
