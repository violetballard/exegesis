# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Commit: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Packet traceability note

- The pre-fixer packet-refresh commit `6a94334ea3b13e716770e2cf4e8bb17d139e3e9d` is metadata-only and its actual diff is `docs/gate_passed.txt` only. Review the narrowed retrieval implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`; later packet-refresh commits remain metadata-only unless this handoff is regenerated.

## Current program focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current engine execution order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope goal

- Remove the PageIndex fallback from `fetch_excerpt`, keep excerpt lookup on the canonical FTS-only path, and prove PageIndex-only excerpt IDs fail closed under approved shared regression coverage. This lane slice advances the canonical demo-path step `retrieve relevant material` and stays out of scope for broader retrieval MVP claims, basket promotion, plan/revise/apply flow work, and any PageIndex or embeddings runtime fallback behavior beyond fail-closed compatibility.

## Priority outcomes

1. Keep `fetch_excerpt` on the canonical FTS-only lookup path.
2. Fail closed for PageIndex-only excerpt IDs instead of silently falling back.
3. Keep the reviewed slice explicitly limited to the excerpt lookup contract and its regression coverage.

## Definition of done for this lane

- `fetch_excerpt` no longer uses the PageIndex fallback path.
- PageIndex-only excerpt IDs raise `KeyError` through the public excerpt lookup surface.
- Approved shared regression coverage proves the fail-closed behavior.
- The handoff outcome is limited to the canonical excerpt lookup contract, not the full retrieval lane.

## Do not spend time on

- Over-investing in embeddings or alternate retrieval modes.
- UI rendering concerns.
- Search features outside the core writing loop.

## Lane/owned paths

- `src/qual/retrieval/**`
- `src/qual/engine/retrieval/**`
- `engine/src/exegesis_engine/retrieval/**`

## Scope completed

- The reviewed implementation commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` removes the PageIndex fallback from `fetch_excerpt`, so excerpt lookup now resolves only through the canonical FTS path.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs fail closed with `KeyError`.
- This work advances `retrieve relevant material` by making excerpt lookup fail closed to FTS-backed IDs and preserving deterministic provenance on the FTS-first canonical retrieval path.
- In AGENTS terms, this strengthens the canonical demo-path step `retrieve relevant material` by keeping excerpt lookup on the canonical FTS path, preserving deterministic provenance on that path, and leaving basket promotion, plan/revise/apply flow work, and broader retrieval MVP claims explicitly out of scope for this handoff.

## Canonical demo-path step advanced

- `retrieve relevant material`
- Milestone 3 engine-first demo path: this slice advances `retrieve relevant material` by making excerpt lookup fail closed to FTS-backed IDs and preserving deterministic provenance on the FTS-first canonical retrieval path.

## Reviewer fix reconciliation

- This packet explicitly names the canonical demo-path step `retrieve relevant material`.
- The scope stays narrow to FTS-only excerpt lookup, fail-closed PageIndex-only IDs, and deterministic provenance on the FTS-first MVP retrieval path.
- PageIndex and embeddings remain out of scope as active runtime retrieval paths for this handoff.

## Explicitly out of scope for this lane slice

- Basket promotion remains out of scope.
- Plan, revise, patch, and apply workflow work remains out of scope.
- PageIndex or embeddings runtime fallback behavior remains out of scope beyond compatibility-only fail-closed handling.

## Kickoff budget/limits compliance

- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap. The narrowed reviewed slice changes 2 files with 59 lines touched in `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, and the handoff describes 2 meaningful tasks, which fits the shared/high-risk size budget.

## Approved exception note

- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Tasks completed (numbered)

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Packet refresh commit `6a94334ea3b13e716770e2cf4e8bb17d139e3e9d` files

- `docs/gate_passed.txt`

### Current fixer-pass handoff artifacts

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

### Previously refreshed packet mirror artifacts

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

## Commands run and outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Residual risk: This slice edited shared regression coverage in `tests/unit/test_unified_retrieval.py`, so any future retrieval change that intentionally broadens excerpt lookup semantics or reintroduces PageIndex fallback will need coordinated updates to that shared test surface before integration.
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - FTS-first retrieval remains the authoritative context path for the engine loop.
- `feat-retrieval-fts` - authoritative FTS-first retrieval feeding the engine loop.

### Vision capability affected

- Retrieval-first context handling
- Auditable state and workflow

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
