# Exegesis MVP (`qual` compatibility repo)

This repository is in a staged migration from the original `qual` package layout toward a unified Exegesis MVP structure:
- `engine/`
- `client-textual/`
- `shared/`
- `docs/`

The Textual writing client is the MVP target, but Textual is not an active dependency yet. Current work remains engine-first while the future UI lanes stay scaffolded and disabled.

## Canonical docs
- Product target and non-negotiables: `PRODUCT_VISION.md`
- Roadmap and milestone status: `ROADMAP.md`
- Architecture boundaries and migration rules: `ARCHITECTURE.md`
- Infra migration plan away from Codex/OpenAI: `MIGRATION.md`
- Integration process and merge gates: `INTEGRATION.md`
- Thread lane ownership and scope guardrails: `THREAD_OWNERSHIP.md`
- Detailed milestone breakdown: `docs/milestones.md`
- Detailed tasks and lane mapping: `docs/TASKS.md`
- Disabled future import/OCR/literature/RAG specs: `docs/FUTURE_IMPORT_RAG_SPEC.md`
- Disabled future summer MVP feature specs: `docs/FUTURE_MVP_FEATURES_SPEC.md`
- Detailed staged structure notes: `docs/PROJECT_STRUCTURE.md`
- Codex-facing migration notes: `docs/README-for-codex.md`

## Compatibility note
- `src/main.py` and `src/qual/*` remain the live compatibility surface for the CLI and packet tooling.
- Canonical packages now live under `exegesis_engine`, `exegesis_shared`, and `exegesis_textual` via staged import bridges.

## Quick commands
- `make help`
- `make ci`
