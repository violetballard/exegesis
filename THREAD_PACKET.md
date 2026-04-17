# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Current packet-refresh head before this fixer commit: `4dfc09848f7c7a68d45ce139758e2bf32479532b`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed

- The reviewed implementation range keeps SQLite FTS authoritative for this MVP lane and preserves PageIndex plus embeddings as deferred compatibility paths rather than required runtime paths.
- The excerpt lookup surface now stays on the canonical FTS-only path, so PageIndex-only excerpt IDs fail closed instead of promoting a non-canonical runtime fallback.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves the FTS-only excerpt contract and the fail-closed behavior for PageIndex-only excerpt IDs.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This reviewed slice makes that step more real by keeping the excerpt lookup contract deterministic, auditable, and FTS-only before downstream basket promotion.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Packet / handoff files

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / blockers

- Risk: `HIGH`
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` because this reviewed slice keeps the engine retrieval path FTS-first and auditable.
- `feat-retrieval-fts - retrieval/search` because this reviewed slice preserves the lane's authoritative excerpt lookup contract.

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared-by-approval edits: `YES`
- Approved shared regression surface: `tests/unit/test_unified_retrieval.py`
- Integrator-locked edits: `NO`

## Traceability note

- Re-review should stay anchored to the reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- The current packet-refresh head before this fixer commit is `4dfc09848f7c7a68d45ce139758e2bf32479532b`.
- Use the final HEAD SHA reported with this fixer handoff for the post-fix branch tip.
