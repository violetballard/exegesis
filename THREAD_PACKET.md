## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Packet HEAD role: `reviewer-fix handoff regenerated at the retrieval branch tip`
- Reviewed implementation head: `fe57bbf292bbb4212c8661f261b639779d0ef7b6`
- Packet refresh base commit before this rerun: `6649f317c40d7a93bdb7238ec805c180daf4a29b`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..fe57bbf292bbb4212c8661f261b639779d0ef7b6`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt, provenance, and evidence output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in the reviewed slice. The reviewed implementation range removes the PageIndex fallback from `fetch_excerpt`, keeping excerpt lookup on the canonical FTS-only path, while approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now raise `KeyError`.
- The current reviewed implementation head `fe57bbf292bbb4212c8661f261b639779d0ef7b6` also fixes FTS cache date-range normalization in `src/qual/engine/retrieval/fts_strategy.py` so ordered date ranges remain stable in cache keys and only inverted pairs are swapped into canonical start/end order.
- Public retrieval contract tightening: FTS excerpt IDs are canonical; PageIndex-only excerpt IDs are no longer accepted by `fetch_excerpt`. PageIndex and embeddings remain deferred compatibility identifiers, not required runtime paths for the MVP retrieval contract.

## Canonical demo-path step advanced

- `retrieve relevant material`: this handoff explicitly advances that canonical demo-path step required by `AGENTS.md`.
- The excerpt lookup change keeps retrieval hits, excerpt payloads, and downstream evidence/provenance bundles on the deterministic FTS-backed path before basket promotion.
- The date-range normalization fix keeps FTS cache behavior stable for retrieval queries that carry ordered date constraints, which makes the same retrieval step more auditable and repeatable.

## Reviewer-required fix
- Reviewer packet fix addressed: `Regenerate the handoff so the reviewed implementation range matches the actual branch tip.`
- Reviewer packet fix addressed: `Update the packet traceability note to match reality and summarize the behavioral impact of fe57bbf292bbb4212c8661f261b639779d0ef7b6.`
- Reviewer packet fix addressed: `Add an explicit canonical demo-path step stating that this work advances "retrieve relevant material".`
- Reviewer packet fix addressed: `Tighten the scope wording so the public excerpt lookup contract is explicitly FTS-only for canonical excerpt IDs.`

## AGENTS.md handoff packet
- Risk reason: shared/high-risk work because the reviewed implementation range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Required checkpoint status notes:
  - `plan complete`: the packet is now anchored to the actual reviewed implementation head `fe57bbf292bbb4212c8661f261b639779d0ef7b6` and reviewed range ending at that head.
  - `first green local tests`: the required gate sweep rerun completed cleanly on `2026-04-16`.
  - `before risky/shared file edit`: no new shared implementation files were edited in this fixer pass; the reviewed implementation range still includes only the approved shared regression file.
  - `ready for handoff`: the packet traceability now matches the live branch state and records the passing gate rerun below.
- Tasks completed:
  1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
  2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.
  3. Fixed FTS cache date-range normalization in `src/qual/engine/retrieval/fts_strategy.py` so ordered query date ranges remain stable and only inverted pairs are reordered.
- Files changed:
  - `src/qual/retrieval/service.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `tests/unit/test_unified_retrieval.py`

## Commands run with results
- `make scope-check`: PASS on `2026-04-16` (`[devex] scope-check: passed for branch 'codex/feat-retrieval-fts'`)
- `./quality-format.sh --check`: PASS on `2026-04-16` (`[format] check passed`)
- `./quality-lint.sh`: PASS on `2026-04-16` (`[lint] passed`)
- `./quality-test.sh`: PASS on `2026-04-16` (`Ran 157 tests in 4.964s`, `OK`, `[test] passed`)
- `./typecheck-test.sh`: PASS on `2026-04-16` (`[typecheck] compiling Python sources in src/`)
- `make ci`: PASS on `2026-04-16` (`Ran 157 tests in 4.917s`, `OK`, `[devex] CI entrypoint completed`)
- Final fixer-pass note: the full required gate sweep was rerun on the lane branch after regenerating the handoff metadata around the actual reviewed implementation head.
- Packet mirror note: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are permission-locked in this worktree, so this fixer pass updates the canonical writable handoff file `THREAD_PACKET.md` and reports the restriction explicitly for re-review.

## Risks/blockers
- Risks: high, because the narrowed reviewed range includes approved shared regression coverage.
- Blockers: none

## Roadmap item(s) affected
- `ROADMAP.md`: `Milestone 3: Real workflow loop`
- Step-level alignment: `retrieve relevant material` is the canonical demo-path step this reviewed retrieval slice advances by keeping excerpt lookup and retrieval cache behavior on an authoritative, auditable FTS-backed path before basket promotion.

## Vision capability affected
- `PRODUCT_VISION.md`: `2. Retrieval-first context handling`
- `PRODUCT_VISION.md`: `6. Auditable state and workflow`
- Step-level alignment: deterministic excerpt lookup, stable date-constrained retrieval caching, provenance, and evidence output stay stable on the FTS-first path used before `promote or gather context into the basket`.

## Routing/provider impact note
- None

## Proposed README.md patch text
- None
