# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f7689ab0f91a0426b4ae0aeaf8bb5c2d09d4d44d`
- Packet refresh commit: `HEAD (feature-fixer reviewer-required-fix re-review refresh)`
- Packet refresh role: `feature-fixer reviewer-required-fix re-review handoff refresh`

## Packet Traceability Note

- This packet now reviews the true current command-surface implementation tip,
  not the earlier `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice alone.
- Included implementation commits in scope:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` - lock
    `command_cli_contract()` to canonical catalog ordering.
  - `801532e089c1b123bb586c18ac1f874141ebfdd1` - add workflow compatibility
    invocation-table accessors in `src/qual/commands/catalog.py` and re-export
    them from `src/qual/commands/__init__.py`.
  - `edff6d8f18ea4b8a24c87bbb062226d5fe6b1961` - normalize additional demo
    compatibility variants onto canonical loop tokens for transition helpers.
  - `f7689ab0f91a0426b4ae0aeaf8bb5c2d09d4d44d` - tighten workflow preferred
    surface-token resolution so the lead workflow token preserves the intended
    terminal route sequence while later tokens stay specific.
- The branch-tip validation evidence now covers the compatibility-variant
  normalization and the workflow preferred-surface-token fix through the
  required local gate rerun.
- Latest packet refresh prepared at: `2026-04-17T15:01:14Z`

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any
  Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Keep the CLI-first MVP command surface deterministic and parser-ready by
  locking canonical CLI order, exposing workflow compatibility invocation
  tables, and normalizing demo compatibility variants onto the trusted loop
  tokens.

## Canonical Demo-Path Step Advanced

- Primary step advanced: `open project/document`.
- Why this is the primary step: `feat-commands` owns the operator-facing
  command surface for entering the MVP loop, and this packet only hardens how
  CLI verbs are normalized, ordered, and exposed to the parser. That is
  first-order MVP work because the current operator surface is the CLI, so a
  drifting or opaque entry contract can break the very first step of the
  canonical loop before retrieval, patch preview, or continuation can happen.
- First-order CLI-loop justification: this refresh does not add generic infra
  or speculative contract polish. It removes concrete operator-surface failure
  modes in the active CLI-first loop by making the accepted command verbs
  deterministic, inspectable, and parser-ready at the command boundary the
  user hits first.
- Concrete blockers removed:
  - `command_cli_contract()` now fails immediately if parser canonical names
    drift from `command_names()` instead of silently returning a reordered or
    truncated contract.
  - Workflow compatibility verbs can now be flattened into parser-ready argv
    through explicit invocation-table accessors, so the compatibility surface
    remains inspectable and smoke-testable.
  - Demo transition helpers now normalize additional compatibility variants
    such as `open-workspace`, `preview-diff`, `accept-patch`, `resume-work`,
    and `queue-handoff` onto the canonical loop tokens, keeping alternate
    operator verbs on the same trusted MVP path rather than falling off the
    route lookup surface.
  - Workflow contracts now preserve the intended preferred surface-token
    sequence for the lead terminal workflow token, so the command surface keeps
    the expected `apply -> reject -> persist -> export` routing order instead
    of collapsing that path to a singleton token.
- Scope-tightening note: this remains command-surface hardening for the
  existing MVP-loop entrypoints only; it does not add new workflow behavior or
  expand beyond the current CLI compatibility layer.
- Reviewer-fix closure note: this packet now answers both required fixes from
  the reviewer by naming the exact canonical demo-path step advanced and by
  framing the change strictly as CLI-first MVP-loop contract hardening while
  Textual remains disabled.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it
  validates canonical command order against `command_names()`, raising
  `ValueError` if the CLI lookup table drifts from the catalog's canonical
  names.
- Kept the returned contract aligned with the canonical command order by
  reusing the canonical names tuple instead of rebuilding a divergent list.
- Added workflow compatibility invocation-table accessors in
  `src/qual/commands/catalog.py` and re-exported them from
  `src/qual/commands/__init__.py` so compatibility verbs stay available as a
  parser-ready contract surface.
- Normalized additional demo compatibility variants in
  `src/qual/commands/catalog.py` so transition helpers resolve alternate verbs
  onto the canonical loop tokens for the trusted MVP path.
- Tightened workflow preferred surface-token resolution in
  `src/qual/commands/catalog.py` so lead workflow tokens keep the intended
  preferred route sequence while later tokens remain token-specific.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py`
  for canonical-order alignment, canonical-name drift rejection, workflow
  compatibility invocation-table accessors, and branch-tip transition helper
  behavior; the current gate rerun also exercises the committed workflow
  preferred-token fix at the true implementation tip.
- Refreshed the handoff packet and thread pointer so re-review is anchored to
  the true branch-tip implementation surface and the current gate rerun.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute
  budget, and lane size limits. The implementation slice stays limited to two
  owned command files plus one focused approved shared test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`. It
  remains the only non-owned implementation path in this handoff.
- Approval provenance available to this fixer turn: the reviewer packet source
  of truth explicitly included `Approved shared-test exception for
  tests/unit/test_commands_catalog.py`; this refresh carries that same
  exception forward and does not add any new shared implementation paths.

## Tasks Completed (Numbered)

1. Hardened `command_cli_contract()` to verify canonical-name consistency
   against `command_names()` and fail fast on canonical-name drift.
   Demo-path step advanced: `open project/document`.
   Concrete blocker removed: the CLI entry contract can no longer silently
   reorder or drop canonical startup verbs before the operator enters the MVP
   loop.
2. Preserved canonical command ordering in the CLI contract by returning the
   validated canonical tuple directly.
   Demo-path step advanced: `open project/document`.
   Concrete blocker removed: smoke tests and parser consumers now see the same
   canonical startup-command order as the command catalog instead of a derived
   order that could drift.
3. Added workflow compatibility invocation-table accessors and exports for the
   current MVP command surface.
   Demo-path step advanced: `open project/document`.
   Concrete blocker removed: compatibility verbs are now exposed as explicit
   parser-ready argv tables, so transition helpers can enter the loop through
   the supported CLI surface instead of relying on implicit lookup behavior.
4. Normalized additional demo compatibility variants so transition helpers map
   alternate verbs back onto the canonical loop tokens.
   Demo-path step advanced: `open project/document`.
   Concrete blocker removed: alternate operator verbs such as
   `open-workspace` and `resume-work` now land on the trusted canonical entry
   tokens instead of falling off the supported command route.
5. Tightened workflow preferred surface-token resolution so the lead terminal
   workflow token preserves the intended route sequence.
   Demo-path step advanced: `open project/document`.
   Concrete blocker removed: the workflow contract now keeps the expected
   `apply -> reject -> persist -> export` preferred route on the terminal
   entrypoint instead of collapsing the lead token to a singleton surface.
6. Added focused regression coverage for the branch-tip command-surface
   contracts and reran the full local gate suite at the true branch tip.
   Demo-path step advanced: `open project/document`.
   Concrete blocker removed: the current CLI entry contract and workflow
   surface now have verified local validation at the true implementation tip,
   which catches parser-surface and preferred-route drift before it can break
   the MVP loop's operator entrypoint.
7. Refreshed the handoff packet and thread pointer so re-review tracks the true
   implementation scope and current gate rerun.
   Demo-path step advanced: `open project/document`.
   Concrete blocker removed: re-review now evaluates the actual branch-tip CLI
   entry surface instead of an older partial slice, which keeps approval tied
   to the real operator contract.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD.md`
- `THREAD_PACKET.md`

## Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`
- Re-verification point: `2026-04-17T15:01:14Z` at the current branch tip

## Risks / Blockers

- Risk: `LOW`
- Remaining risk: none beyond normal merge sequencing for a narrow
  command-catalog change.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the
  package/layout migration lands by keeping the command surface deterministic,
  parser-ready, and smoke-testable across canonical and compatibility verbs.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the
  engine-first MVP loop.
- Scope-tightening note: this packet only claims command-surface hardening for
  the current CLI compatibility layer covering `bootstrap`,
  `context-basket`, `diff-preview`, and `terminal` plus their compatibility
  verbs in the active MVP loop, not a broader workflow capability change.

### Vision capability affected

- Canonical engine contract - the CLI compatibility surface stays stable and
  smoke-testable while Textual remains disabled.
- Auditable state and workflow - compatibility verbs now stay on explicit,
  inspectable parser-ready routes instead of relying on implicit fallback
  behavior.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused
  command-catalog test coverage.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: owned implementation paths are
  `src/qual/commands/catalog.py` and `src/qual/commands/__init__.py`; the only
  non-owned implementation path is the approved shared test
  `tests/unit/test_commands_catalog.py`.
