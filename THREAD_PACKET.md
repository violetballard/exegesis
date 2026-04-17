# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Current packet-refresh head before this fixer commit: `790c9174e79db53f0fb51e64d7e87d3a6a56ed31`
- Reviewed implementation head: `e744fe89c74abe487ebcd5df76282149f89de6bb`
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..e744fe89c74abe487ebcd5df76282149f89de6bb`

## Scope goal

- Keep the lane FTS-first while making retrieval payloads, provenance, excerpt lookup, and basket-promotion metadata deterministic and auditable for engine flows.

## Scope completed

- The reviewed implementation range keeps SQLite FTS authoritative for this MVP lane and preserves PageIndex plus embeddings as deferred compatibility paths rather than required runtime paths.
- Canonical retrieval payloads now carry normalized query context, richer provenance, source-bundle fingerprints, and deterministic context/basket-promotion snapshots for downstream engine flows.
- Canonical excerpt lookup stays on the FTS-only path, and lookup promotion metadata is hardened so excerpt resolution fails closed off the authoritative retrieval surface instead of promoting non-canonical fallbacks.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` covers the FTS-only excerpt contract, payload/provenance normalization, deferred-scope rejection, helper exports, and basket-promotion backfills.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This reviewed slice makes that step more real by keeping engine-facing retrieval outputs deterministic, structured, and auditable at the point where retrieved material is turned into excerpt/context payloads for downstream basket promotion.

## Tasks completed

1. Kept excerpt lookup and engine-facing excerpt helpers on the canonical FTS-only path, including deterministic lookup promotion metadata and fail-closed behavior for non-canonical excerpt IDs.
2. Hardened retrieval payload, provenance, source-bundle, and context-bundle snapshots so query context, fingerprints, citations, and basket-promotion fields round-trip deterministically for engine consumers.
3. Tightened FTS-first query behavior by normalizing retrieval query context, failing fast on deferred scopes that the lane does not support, and keeping deferred strategies out of the canonical runtime path.
4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the canonical retrieval contract across helpers, provenance/citation backfills, scope validation, and excerpt lookup behavior.

## Files changed

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

- `Milestone 3: Real workflow loop` because this reviewed slice hardens the FTS-first retrieval contract used by the engine loop when it retrieves relevant material.
- `feat-retrieval-fts - retrieval/search` because this reviewed slice keeps the lane authoritative for structured, deterministic retrieval output and excerpt lookup.

### Vision capability affected

- `Retrieval-first context handling` because this reviewed slice keeps retrieval outputs structured enough for context gathering and basket promotion.
- `Auditable state and workflow` because this reviewed slice keeps provenance, excerpt lookup, and downstream retrieval payloads deterministic and fail-closed on the canonical path.

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared-by-approval edits: `YES`
- Approved shared regression surface: `tests/unit/test_unified_retrieval.py`
- Integrator-locked edits: `NO`

## Traceability note

- The earlier packet was inaccurate because it still anchored review to `adfa8cdadd43747ffbcb612e4151e262b13e52ca` even though later runtime commits remained on the branch.
- Re-review should use the full reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..e744fe89c74abe487ebcd5df76282149f89de6bb`.
- The current packet-refresh head before this fixer commit is `790c9174e79db53f0fb51e64d7e87d3a6a56ed31`, and the commits after `e744fe89c74abe487ebcd5df76282149f89de6bb` up to that head are packet-only metadata refreshes.
- Use the final HEAD SHA reported with this fixer handoff for the post-fix branch tip.
