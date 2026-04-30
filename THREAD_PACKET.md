## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Authoritative merge/review range for the actual integration candidate: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`
- Current pre-fix branch tip audited for source/test surface: `f3a9d73d22ff8677daa79874dd28616551826ea5`
- Merge candidate: the branch tip after this packet-only fixer commit; it is not `adfa8cdadd43747ffbcb612e4151e262b13e52ca` or `e4f835c50`.
- Scope classification: high-risk/shared because the candidate includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Packet type: retrieval feature handoff for the FTS-first retrieval lane.

## Scope Completed

The actual branch-tip candidate keeps SQLite FTS as the only active retrieval path and reconciles the handoff with the full source/test surface from `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`. The candidate exports canonical retrieval query construction through the engine retrieval facade, normalizes boolean constraints deterministically, removes the stale one-entry FTS strategy cache, makes payload/source/context snapshots deterministic, adds basket-promotion item fingerprints, and keeps excerpt lookup on the canonical FTS-only path so PageIndex-only excerpt IDs fail closed under shared regression coverage.

PageIndex and embeddings remain compatibility-only fallback shims and are not reintroduced as required retrieval paths. This packet supersedes earlier narrowed packet claims that stopped at `adfa8cdadd43747ffbcb612e4151e262b13e52ca` or `e4f835c50`; re-review should inspect the full `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` candidate.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: kept retrieval FTS-first by making `fetch_excerpt` require an FTS excerpt hit and by removing the stale FTS strategy result cache.
2. Canonical demo-path step `retrieve relevant material`: exported and normalized canonical retrieval query construction through the engine retrieval facade, including deterministic boolean constraint handling.
3. Canonical demo-path step `retrieve relevant material`: made retrieval payloads, provenance snapshots, citation bundles, and sparse source/context rehydration deterministic for downstream engine flows.
4. Canonical demo-path step `promote or gather context into the basket`: added deterministic basket-promotion refs, item IDs, context-bundle fingerprints, and `basket_item_fingerprint` backfill for sparse excerpt-hit snapshots.

## Files Changed

Authoritative candidate files changed for `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`:

- `.codex/kickoff_packets/feat-retrieval-fts.md` - existing packet mirror in the candidate; this fixer session could not refresh it because filesystem writes to `.codex` are blocked with `Operation not permitted`.
- `.codex/lane_meta/feat-retrieval-fts.json` - existing lane metadata mirror in the candidate; this fixer session could not refresh it because filesystem writes to `.codex` are blocked with `Operation not permitted`.
- `THREAD_PACKET.md` - handoff packet regenerated for the actual branch-tip candidate.
- `src/qual/engine/retrieval/__init__.py` - exports canonical query construction with strict optional-boolean normalization.
- `src/qual/engine/retrieval/fts_strategy.py` - removes stale one-entry result caching while preserving the compatibility `clear_cache` hook.
- `src/qual/engine/retrieval/payload.py` - normalizes deterministic retrieval payloads, source/context bundles, basket-promotion items, and sparse snapshot backfill.
- `src/qual/retrieval/service.py` - keeps FTS as the authoritative lookup path and emits deterministic result/query/basket fingerprints.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage for cache invalidation, deterministic payloads, facade exports, basket refs, and FTS-only excerpt lookup.

Full candidate stat before this packet-only commit: `8 files changed, 936 insertions(+), 210 deletions(-)`.

Source/test surface included for review:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Source/test stat before this packet-only commit: `5 files changed, 683 insertions(+), 119 deletions(-)`.

Lane-owned source files:

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`

Shared-by-approval files:

- `tests/unit/test_unified_retrieval.py` - approved shared regression surface for the retrieval lane.

Out-of-lane tooling files:

- None.

Integrator-locked files:

- None.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `8/8` high-risk files before this packet-only commit.
- Source/test file count: `5` files.
- Full candidate net LOC before this packet-only commit: `+726`.
- Source/test net LOC before this packet-only commit: `+564`.
- Size exception required: yes. The candidate exceeds the AGENTS.md high-risk `<=300` net LOC guideline because the actual branch-tip surface includes the full retrieval payload/service/test implementation, not only the earlier narrowed packet slice.
- Explicit size exception request: approve review of the full `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` candidate as a single high-risk retrieval handoff because splitting the already-committed branch tip would reintroduce the traceability gap the reviewer flagged.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is included as the approved shared-by-approval regression surface for the retrieval lane.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; PageIndex and embeddings remain deferred/compatibility-only and are not active retrieval paths.
- Merge risk: high until reviewer accepts the corrected full branch-tip range and size exception; implementation risk is contained to retrieval-owned paths plus the approved shared test file.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 4 retrieval layer; active MVP focus for FTS-first retrieval.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable state/workflow.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

Required gates for the corrected candidate:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, smoke plus 126 unit tests.
- `./typecheck-test.sh` PASS, Python sources under `src/` compile.
- `make ci` PASS, includes scope-check, format, lint, typecheck, and 126 unit tests.

Focused gate already run earlier in this branch:

- `python -m unittest tests.unit.test_unified_retrieval` PASS, 57 tests, after fixing the first focused fingerprint-helper failure.

## Risks/Blockers

No implementation blocker is known. The remaining reviewer-facing risks are the requested AGENTS.md size exception for the full high-risk branch-tip candidate and the inability to refresh `.codex` packet mirrors from this sandbox; `THREAD_PACKET.md` is the corrected handoff packet for re-review.
