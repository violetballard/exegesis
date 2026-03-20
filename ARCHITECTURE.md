# Architecture Guardrails

This file defines hard boundaries to keep the codebase understandable and refactor-safe.

## Layer Ownership

- `src/qual/ui/**`
  - Owns user-facing rendering and display formatting.
  - Must not read/write storage directly.

- `src/qual/console/**`
  - Owns the future `Exegesis Console` operator surface.
  - Will consume engine/A2UI contracts rather than introducing separate business logic.
  - Is intentionally deferred until the engine and A2UI contracts are stable enough to drive it.

- `src/qual/engine/**`
  - Owns orchestration of user flows and app state transitions.
  - Owns config resolution/validation/apply logic exposed to UI/CLI.
  - Owns provider capability probing and fallback decisions from probe outputs.
  - Calls service interfaces in lower layers.
  - Must not implement crypto or raw database logic.

- `src/qual/commands/**`
  - Owns command-level behavior and command output contracts.
  - Must not directly mutate persistent storage.

- `src/qual/context/**`
  - Owns context-basket domain rules and normalization.

- `src/qual/storage/**`
  - Owns local persistence and vault lock state behavior.
  - Is the only layer that touches on-disk state files for storage/vault concerns.

- `src/qual/metrics/**`
  - Owns metrics schema, recording, storage, and export.
  - Must remain isolated from product flow logic except through explicit engine calls.

## Dependency Direction

Allowed direction only:
- `ui -> engine`
- `console -> engine`
- `commands -> drafting|context|engine` (via public entrypoints)
- `engine -> config|context|storage|metrics|drafting`
- `context -> (no engine/ui imports)`
- `storage -> (no engine/ui imports)`
- `metrics -> (no ui imports)`

Disallowed examples:
- `ui -> storage`
- `console -> storage`
- `ui -> metrics/db`
- `engine -> metrics/crypto internals`
- `console -> config files on disk`
- `commands -> storage`

## Integration Contracts

- Each cross-module concern gets one thin entrypoint:
  - config: effective-resolver + validator + apply + revision-history entrypoints only
  - metrics: recorder/report/export entrypoints only
  - storage: vault/context store entrypoints only
  - commands: public command runner only
- Model/provider routing must be centralized in engine policy modules, not scattered across commands/UI.
- Provider capability probes must run through one engine probe service and persist auditable capability reports.
- Retrieval is FTS-first for the current MVP. PageIndex/embeddings are deferred until after the May 4 demo push.
- Role overrides (if enabled) must flow through a single validated endpoint profile resolver.
- No feature lane should import private helper modules from another lane.

## Change Rules

- Any new infrastructure module (metrics, audit, encryption, persistence) must include:
  - ownership statement (what it owns)
  - non-goals (what it must never do)
  - one integration point in engine or command layer
- Keep optional behavior behind explicit flags/defaults until stable.
- Add or update focused contract tests when changing cross-layer behavior.
- Any provider override path must enforce localhost-only endpoint validation and must be auditable.
