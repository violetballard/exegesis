# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix packet regeneration`
- Current branch tip before this fixer pass: `cc6190fde2f6505f18847f293ef29ebb9f766fa1`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..cc6190fde2f6505f18847f293ef29ebb9f766fa1`
- Reviewed implementation head: `cc6190fde2f6505f18847f293ef29ebb9f766fa1`
- Packet-only descendants above the reviewed implementation head: this fixer pass only; final HEAD SHA is reported with the fixer handoff
- Packet traceability note: the submitted retrieval implementation for this handoff reaches the actual pre-fix branch tip `cc6190fde2f6505f18847f293ef29ebb9f766fa1`. This packet refresh does not exclude later retrieval commits such as `245ddb91`, `d900d077`, or `cc6190fd`; it accounts for them explicitly in scope, tasks, file inventory, and roadmap/vision mapping.

## Scope goal

- Advance `Milestone 3` by making the canonical demo-path step `retrieve relevant material` concretely FTS-first while making excerpt lookup, payload reconstruction, provenance snapshots, and basket-promotion state deterministic and auditable for downstream engine flows.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: keep retrieval runtime behavior FTS-first while carrying canonical query, constraints, provenance, and section hints through excerpt lookup and basket promotion without reopening PageIndex/embeddings as required paths.
- Risk reason: the submitted scope includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep excerpt lookup and retrieval scopes on the canonical FTS-first path, including fail-closed behavior for deferred, sparse, and non-FTS cases.
2. Normalize retrieval payloads, citation/provenance bundles, query snapshots, and rebuilt section hints across retrieval and engine facades.
3. Preserve auditable downstream basket-promotion state by carrying query text, constraints, policy aliases, retrieved IDs, and source fingerprints through context bundles.
4. Regenerate the handoff packet so the reviewed implementation range, tasks, files changed, roadmap mapping, and gate results match the actual submitted tip.

### Checkpoint Status

- `plan complete`: the packet is regenerated against the actual submitted implementation head `cc6190fd...`.
- `first green tests`: recorded after rerunning the required gates for this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in the submitted range remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the handoff now accounts for the full retrieval implementation range through `cc6190fd...` and reserves only this fixer commit as packet-only metadata.

## Scope completed

- Advanced `Milestone 3` by keeping the canonical demo-path step `retrieve relevant material` concretely FTS-first: SQLite FTS remains the authoritative MVP retrieval backend, with fail-closed behavior for non-canonical excerpt lookup, deferred scopes, and sparse query-context reconstruction.
- Normalized retrieval payload IDs, query/date-range snapshots, citation/provenance/source bundles, hit ordering, and rebuilt section hints across `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`.
- Carried canonical query text, query constraints, policy aliases, retrieved IDs, source-bundle fingerprints, and basket-promotion evidence through retrieval context bundles so downstream engine consumers receive auditable deterministic state.
- Preserved approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the FTS-only excerpt contract and the broader deterministic retrieval payload surface.

## Canonical Demo-Path Steps Advanced

- `retrieve relevant material`
- `carry retrieved evidence into downstream workflow state`

This handoff advances `retrieve relevant material` by keeping excerpt lookup, hit ordering, query normalization, and section-hint reconstruction on the canonical FTS path. It advances `carry retrieved evidence into downstream workflow state` by preserving auditable query constraints, provenance, source fingerprints, and basket-promotion snapshots that downstream engine flows consume.

## Tasks completed

1. Enforced the canonical FTS-first retrieval path in `src/qual/retrieval/service.py`, including fail-closed excerpt lookup, deferred-scope handling, sparse query-context hardening, and normalized rebuilt section hints.
2. Canonicalized payload/citation/provenance/query snapshot behavior across `src/qual/retrieval/__init__.py`, `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/interface.py`, and `src/qual/engine/retrieval/payload.py`.
3. Preserved auditable basket-promotion and retrieval-hit state across `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/pageindex_strategy.py`, and `src/qual/engine/retrieval/embeddings_strategy.py`, including query constraints carried into promotion state.
4. Maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` and regenerated the packet artifacts so the handoff matches the actual submitted implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..cc6190fde2f6505f18847f293ef29ebb9f766fa1`.

## Files changed

- Total files in the submitted reviewed range: `12`
- Handoff metadata:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
- Submitted implementation and regression files in the reviewed range:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. The handoff now names the true submitted retrieval implementation head `cc6190fde2f6505f18847f293ef29ebb9f766fa1` instead of stopping at `adfa8cda...`.
2. `Scope completed`, `Tasks completed`, and `Files changed` now explicitly include the non-metadata retrieval work that landed after `adfa8cda`, including payload, strategy, service, and regression-surface changes.
3. Roadmap, vision, and demo-path mapping now describe the real cumulative retrieval scope through `cc6190fd...`, including basket-promotion constraints and rebuilt section-hint normalization.
4. The required handoff fields now explicitly name the canonical demo-path step `retrieve relevant material` and tie it to the Milestone 3 FTS-first retrieval requirement instead of leaving that alignment implicit.
5. The packet now states the exact reviewed-range file count (`12`) so the resubmitted scope matches the branch diffstat the reviewer called out.
6. The required gates are rerun and recorded against the resubmitted tree represented by this fixer pass.
7. This fixer pass reconfirms the explicit demo-path mapping so plan alignment remains stated in the packet rather than inferred by the reviewer.

## Risks / blockers

- Risk: `HIGH`
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Product Readiness`
- `Milestone 4: Retrieval Layer`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Milestone 3 FTS-first requirement alignment

- This handoff advances `Milestone 3` by keeping `retrieve relevant material` on the canonical SQLite FTS path and by documenting that PageIndex and embeddings are not required MVP retrieval paths.

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable generation`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits in the reviewed implementation range: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval implementation file in the submitted range.
- Ownership detail: runtime edits remain in the lane-owned retrieval paths, and no integrator-locked runtime files are part of the submitted retrieval implementation range.
