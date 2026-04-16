# Thread Handoff Packet

- Branch name: `codex/feat-commands`

## Review Basis

- This packet is anchored to the actual current branch-tip implementation lineage on `codex/feat-commands`, including this packet refresh commit.
- Current implementation proposed for review is the branch tip on `codex/feat-commands`; reviewers should use this packet plus the listed in-scope implementation commits below rather than the earlier narrowed packet.
- This packet supersedes the earlier narrowed re-review request that asked reviewers to inspect only `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; that narrowed basis was incomplete and should not be used for re-review.
- It does not treat all commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as metadata-only.
- Non-doc implementation commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` that remain in scope for review:
  - `1abb3bc162bc6e718db82ff79beb8cfadda47d90` `fix(commands): validate CLI parser surface`
  - `26658f395761421f90e4b843e50883787e60b1d0` `Add command CLI shim contract`
  - `8b52002c3f963820bb1b3efe7698c7f97c952ae5` `fix(commands): reject parser surface drift`
  - `cea5da3599799e72b24ed5f3e88474f3e275846a` `Add invocation metadata to command smoke contract`
  - `1c579bad8730c1e6a2fe31d8c1af63b7c230f748` `Add deterministic command shim argv helpers`
  - `87c41dfca9176387c07223a15ea08c5deea68578` `Add deterministic command resolution helpers`
  - `adffc42fe4a23e8196ce76a09f58fcf512dc3c4c` `fix(commands): close reviewer packet fixes`
  - `d71711d733585988c4c670db103745b01ce79c37` `Add parser-ready command entrypoint argv helper`
  - `2edf67f71042b6156a9e845dcd87b0b5362468a1` `feat(commands): classify legacy aliases correctly`
  - `f3e88eb90a1116054bac208067568d3c7fbed927` `Add runnable smoke argv for commands`
  - `923e61c123b2b1cb2d67a9a952c3e4672d79d4d4` `Fix canonical command wrapper export`
- Docs-only `docs(commands): ...` commits after those implementation commits update `THREAD_PACKET.md` only.
- This packet refresh commit updates `THREAD_PACKET.md` only after rerunning the full required gate set; it does not widen the implementation scope beyond the implementation commits listed above, and it exists specifically to keep the review basis aligned with the real branch tip after the reviewer-required parser-surface fixes landed.

## Reviewer Fix Closure

- Parser-surface invariant: `command_cli_contract()` now preserves canonical ordering for the CLI-exposed command subset and validates the exact declared per-command CLI parser surface, so alias substitution or token reordering raises `ValueError` instead of silently mutating the operator contract.
- Migration-safe catalog growth: command-catalog entries can now opt out of the CLI parser surface explicitly, so future non-CLI catalog commands do not break the live CLI contract.
- Regression coverage: `tests/unit/test_commands_catalog.py` includes focused rejection tests for alias substitution in the parser surface and parser-token reordering, plus migration-safe coverage showing that an additional non-CLI catalog command does not break the CLI contract or its canonical CLI ordering.
- Demo-path mapping: this packet explicitly names the canonical demo-path step advanced by the lane so the handoff satisfies the `AGENTS.md` narrowing rule instead of relying on reviewer inference.

## Scope Goal

- Harden the CLI command contract so CLI-exposed command ordering, parser entrypoints, route ordering, and invocation planning stay deterministic and fail fast when the parser surface drifts from the catalog.
- Keep the CLI-first MVP loop stable while Textual remains disabled.

## Canonical Demo-Path Step Advanced

- Primary step advanced: `preview and apply or reject a patch`
- Secondary step supported: `continue working without losing context`
- Exact mapping: this lane hardens the `patch-review` command surface so parser/catalog drift cannot silently change the live CLI operator contract used to preview and apply or reject a patch and then continue working without losing context through the same stable command surface.
- Operational narrowing: this packet claims only CLI contract support for the active operator loop, not a broad engine-stability improvement outside the live demo path.

## Lane / Ownership

- Owned runtime path: `src/qual/commands/**`
- Approved non-owned shared-test exception: `tests/unit/test_commands_catalog.py`
- No integrator-locked implementation files were edited.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so CLI-exposed canonical names stay in catalog order, catalog-only commands can opt out of the parser surface, and the declared parser surface must exactly match the catalog-backed CLI entrypoint layout or raise `ValueError`.
- Added parser-surface lookup helpers, deterministic route and invocation metadata, CLI shim contract helpers, and MVP smoke-contract metadata in `src/qual/commands/catalog.py`.
- Classified legacy command aliases deterministically in `src/qual/commands/catalog.py` so raw CLI tokens preserve the intended `primary` vs `cli` vs `flow-step` vs `lookup` kind even when the user input differs only by case or underscore normalization.
- Added runnable smoke argv metadata in `src/qual/commands/catalog.py` so the deterministic command contract covers the actual CLI invocation plan for the active smoke path.
- Exported the expanded command-contract helpers from `src/qual/commands/__init__.py` so compatibility imports remain aligned with the branch-tip implementation.
- Restored the public `canonical_command` wrapper export in `src/qual/commands/canonical.py` so compatibility imports keep resolving against the catalog-backed implementation.
- Fixed bounded diff preview truncation in `src/qual/commands/diff_preview.py` so the `patch-review` path stays deterministic under output limits.
- Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order validation, parser-surface alias substitution rejection, parser-token reordering rejection, migration-safe non-CLI catalog growth, shim argv helpers, deterministic resolution helpers, legacy-alias kind classification, route determinism, and smoke invocation metadata.
- Refreshed this handoff packet so the review basis, files changed, and demo-path mapping match the actual current branch-tip implementation.

## Files Changed

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD_PACKET.md`

## Tasks Completed

1. Locked the CLI `patch-review` contract to canonical command ordering and fail-fast parser validation.
2. Stabilized CLI shim, route, parser lookup, invocation metadata, and parser-ready argv normalization from the canonical command catalog.
3. Preserved deterministic legacy-alias classification and patch-preview behavior under normalized CLI input and truncation.
4. Added regression coverage for drift rejection, alias classification, and deterministic command-resolution behavior.

## Kickoff Budget / Limits Compliance

- High-risk/shared-file template applies because of the approved shared test edit in `tests/unit/test_commands_catalog.py`.
- This handoff remains within the `4`-task cap for the implementation slice under review; the packet refresh is documentation only and is not counted as an implementation task.
- Runtime edits stayed within lane-owned paths; the only non-owned implementation file is the approved shared test above.

## Commands Run With Results

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / Blockers

- Residual risk: no material runtime risk remains after the passing gate set. The only remaining exposure is the approved shared-test exception `tests/unit/test_commands_catalog.py`; runtime behavior stays confined to lane-owned command code.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` because deterministic command ordering and parser-drift rejection keep the live CLI `open/retrieve/basket/patch-review` operator loop stable while the package/layout migration lands.
- `feat-commands` because this slice keeps the CLI-first MVP operator surface deterministic and smoke-testable for the active engine-first loop.
- Concrete loop impact: the branch preserves a deterministic CLI contract for the live `patch-review` step inside the current engine-first demo path instead of allowing parser/catalog drift to change that operator surface silently.

### Vision capability affected

- `Canonical engine contract` because the active CLI compatibility surface stays stable and deterministic while Textual remains disabled.
- `Auditable state and workflow` because parser/catalog drift is rejected explicitly instead of silently mutating the operator contract that drives patch review and continued work.
- Concrete contract impact: operators can rely on the same catalog-backed CLI surface when entering the patch-review path and continuing work, which keeps the MVP contract explicit and reviewable.

### Routing/provider impact note

- None. This lane only changes local command-catalog and CLI-contract behavior.

### Proposed README.md patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Shared edit is limited to the approved test exception `tests/unit/test_commands_catalog.py`.
- No edits were made to `src/main.py`, `src/qual/cli.py`, `src/qual/app.py`, or any provider/routing/config files.
