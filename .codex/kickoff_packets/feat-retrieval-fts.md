# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/policy.py`, `src/qual/retrieval/service.py`
- Scope goal: Record the commit-accurate FTS provenance hardening and `primary_strategy_id` plumbing in retrieval policy and service.
- Scope completed: The reviewed commit `5588e19ac01c380b6369781afe145f4f3850a5ba` changes `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/policy.py`, and `src/qual/retrieval/service.py` to harden FTS provenance and expose the primary retrieval strategy.

### Priority outcomes
1. Keep the kickoff packet, lane metadata, and handoff packet commit-accurate.
2. State clearly that the reviewed change is FTS provenance hardening plus `primary_strategy_id` plumbing.
3. Avoid implying ingestion, routing, PageIndex, embeddings, or broader retrieval-engine changes.

### Tasks
1. Harden FTS provenance handling in `src/qual/retrieval/service.py`.
2. Expose the primary retrieval strategy through retrieval policy and engine exports.
3. Preserve a narrow, commit-accurate file list and metadata for the reviewed diff.

### Files changed
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/policy.py`
- `src/qual/retrieval/service.py`

### Guardrails
- Keep the change limited to handoff-artifact alignment.
- Preserve commit accuracy between the packet, lane metadata, and git history.
- Do not reference unrelated retrieval MVP scope or files outside the reviewed diff.
