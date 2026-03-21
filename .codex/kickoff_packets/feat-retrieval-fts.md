# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- Scope goal: Record the commit-accurate self-describing citation bundle metadata in the retrieval payload and service path.
- Scope completed: The reviewed commit `b8a6f9c1649e76e97992687cc81d92561d1e9f18` changes `src/qual/engine/retrieval/payload.py` and `src/qual/retrieval/service.py` to self-describe the citation bundle and propagate it downstream.

### Priority outcomes
1. Keep the kickoff packet, lane metadata, and handoff packet commit-accurate.
2. State clearly that the reviewed change is citation-bundle self-description plus payload propagation.
3. Avoid implying ingestion, routing, PageIndex, embeddings, or broader retrieval-engine changes.

### Tasks
1. Add self-describing citation-bundle metadata in `src/qual/engine/retrieval/payload.py`.
2. Propagate the citation bundle through `src/qual/retrieval/service.py`.
3. Preserve a narrow, commit-accurate file list and metadata for the reviewed diff.

### Files changed
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`

### Guardrails
- Keep the change limited to handoff-artifact alignment.
- Preserve commit accuracy between the packet, lane metadata, and git history.
- Do not reference unrelated retrieval MVP scope or files outside the reviewed diff.
