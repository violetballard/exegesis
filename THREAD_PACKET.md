# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Current branch head before this handoff commit: `8ac415f5cd738945fd8ac2e47339b0690922d3bb`

## Scope completed

- Kept SQLite FTS authoritative for retrieval-owned excerpt lookup.
- Promoted deterministic `retrieved_doc_ids` and `retrieved_excerpt_ids` into the canonical excerpt lookup payload, its provenance snapshot, and the basket-promotion record.
- Kept the lookup contract aligned with the retrieval result contract so engine flows can promote lookup-derived context into the basket without reconstructing ranked source ids.

## Tasks completed

1. Backfilled stable ranked retrieval ids for canonical excerpt lookup provenance.
2. Surfaced the same ranked retrieval ids at the top level of the excerpt lookup payload.
3. Aligned lookup basket-promotion metadata with the same canonical ranked ids for downstream engine promotion flows.

## Files changed

- `src/qual/retrieval/service.py`
- `THREAD_PACKET.md`

## Commands run with results

- `python -m unittest tests.unit.test_unified_retrieval`: `PASS`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / blockers

- Risks: low; this change is additive to the lookup payload contract and does not widen retrieval strategy scope beyond FTS-first behavior.
- Blockers: none.

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 4: Retrieval Layer` by tightening the deterministic, auditable retrieval contract used by engine flows.
- `Milestone 3: Product Readiness` by narrowing and stabilizing a user-facing retrieval payload shape used in the workflow loop.

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable generation`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This narrowed reviewed slice makes the canonical `retrieve relevant material` step more real by forcing excerpt lookup through the FTS-backed retrieval contract and failing closed instead of falling back to PageIndex-only excerpt ids.
- The same FTS-only lookup contract remains suitable for later basket/context promotion flows without widening the MVP retrieval path.
- This fixer pass records that explicit demo-path mapping in the tracked handoff packet so re-review can verify AGENTS alignment directly from the handoff.

### Routing/provider impact note

- None.

### Proposed `README.md` patch text

- None.
