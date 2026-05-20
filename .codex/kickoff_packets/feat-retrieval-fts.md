# feat-retrieval-fts Handoff Metadata

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Reviewed source range: `31f37df743172e74813f9a4fb056b040bb384692..5da9644dd22f91385cfecfaf4d1a6d7aae328ee5`
- Reviewed commit: `5da9644dd22f91385cfecfaf4d1a6d7aae328ee5`
- Roadmap item(s) affected:
  - ROADMAP.md: Milestone 3: Real workflow loop
- Vision capability affected:
  - 2. Retrieval-first context handling
  - 6. Auditable state and workflow
- Canonical demo-path step advanced: retrieve relevant material and promote or gather context into the basket with deterministic FTS provenance
- Concrete tasks completed:
  1. Exposed the retrieval demo-path contract so downstream payloads can name the FTS retrieval-to-basket steps.
  2. Allowed FTS excerpt promotion to derive source strategy from an explicit sqlite_fts/fts_first retrieval envelope.
  3. Rejected incomplete excerpt promotion records that lack required document, span, hash, or FTS lookup provenance.
  4. Kept the implementation diff lane-scoped to retrieval payload/service exports while advancing retrieve relevant material and basket promotion.

This file is control-plane metadata. The feature implementation remains on the lane branch.
