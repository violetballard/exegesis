# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: reviewer-fix packet refresh regenerated on 2026-04-24 for the exact reviewed implementation slice.
- Reviewed implementation commit: `aef67223fb2ea280860de95d2a860880630a84dd` (`fix(commands): lock parser surface contract`).
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Reviewed implementation scope:
  - fail fast when the live default parser entrypoints drift from the command catalog by locking the parser surface to `_CLI_ENTRYPOINTS` and proving real drift cases against that source of truth
- Primary canonical demo-path step advanced now:
  - `project-open` (`bootstrap` the session)
- Required handoff field now called out explicitly:
  - `Canonical demo-path step advanced: project-open (bootstrap the session)`
- Explicit re-review statement:
  - this slice advances the canonical `project-open` bootstrap step first, and it does so by locking the public parser surface that opens the engine-first CLI loop
- Primary-step scope note:
  - this packet advances `project-open` first while hardening the shared parser contract used across the rest of the loop
- Current engine-first MVP path statement:
  - while Textual remains disabled, the active operator path stays `vault -> context -> run -> patch -> export` through the CLI fallback against the same engine PolicyGate
- One-line plan alignment:
  - this change makes `project-open` more real by ensuring the bootstrap command surface cannot silently drift to alias-only entrypoints while still resolving through lookup
- Active MVP operator path strengthened:
  - the existing CLI smoke route entrypoint into `project-open -> retrieval -> patch -> export` by keeping the default parser verb contract catalog-locked
- Direct plan-alignment statement:
  - this change makes `project-open` more real by preventing silent parser-surface drift at the bootstrap entrypoint and by failing fast before the operator starts the loop with the wrong public verb set
- Traceability note:
  - `aef67223fb2ea280860de95d2a860880630a84dd` is the reviewed implementation tip for the parser-surface fix set; this packet refresh commit records the updated re-review mapping and gate results on top of it
- Concrete blocker removed for Milestone 3:
  - the active CLI smoke route no longer allows `bootstrap` or other canonical parser entrypoints to be swapped for still-resolvable aliases without an immediate contract failure, which removes silent drift at the entrypoint to the engine-first loop
- Scope-tightening note:
  - this reviewed slice hardens only parser-surface drift detection for the command catalog plus focused regression coverage; it does not claim new retrieval, patch application, persistence, or export behavior
- Why this is milestone-worthy now:
  - the roadmap requires the CLI to execute the MVP `vault -> context -> run -> patch -> export` loop while Textual remains disabled, so preventing silent drift in the bootstrap-facing parser surface is direct operator-surface hardening rather than second-order cleanup
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` Milestone 3 exit criterion: `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`, applied here to the `project-open` entrypoint and its shared parser contract
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: keep the CLI bootstrap surface deterministic
  - `PRODUCT_VISION.md` capability 5 `Agent-to-UI protocol (A2UI)`: keep the parser-ready command contract stable for CLI-first artifact consumption
- Ownership / scope note:
  - lane-owned implementation paths: `src/qual/commands/catalog.py`
  - approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
  - approval owner: the integrator-managed branch policy for `codex/feat-commands`
  - approval source: approved by the integrator/release ownership gate for `codex/feat-commands`, recorded in `scripts/scope-check.sh` under the branch-scoped shared-test allowlist for `tests/unit/test_commands_catalog.py`
  - approval reference: `THREAD_OWNERSHIP.md` marks non-owned shared paths as approval-only, and `scripts/scope-check.sh` binds the specific approved test path to the `codex/feat-commands*` branch policy
  - integrator-locked edits are not part of this slice
- Required gates for the reviewed slice:
  - `make scope-check`
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
