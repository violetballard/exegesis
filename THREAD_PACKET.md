# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: regenerate the handoff packet against the actual branch tip and make the reviewer-facing scope, shared-file notes, and CLI-first demo-path alignment match the implementation currently on `HEAD`.
- Risk reason: the branch under review changes the shared command surface and shared handoff metadata, so an inaccurate packet would misstate the real review target.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the packet to the actual branch tip instead of the earlier narrow-slice description.
2. Expand handoff scope, files changed, and shared-path notes so they match the live `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD` diff.
3. Add an explicit AGENTS alignment line naming the canonical demo-path step and how the deterministic CLI contract strengthens the Milestone 3 CLI-first loop.
4. Re-run `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Early Review Triggers

- Before first edit to any shared/integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing/config behavior.

### Stop Triggers

- Unresolved test/lint/typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: packet regeneration will describe the actual `HEAD` implementation instead of the earlier narrowed handoff.
- First green tests: recorded after the full required gate suite on `2026-04-18`.
- Before risky/shared file edit: `THREAD.md` and `THREAD_PACKET.md` are shared metadata paths; the reviewed implementation also includes shared test coverage.
- Ready for handoff: packet scope, files changed, exceptions, and demo-path alignment now match the branch tip being re-reviewed.

## Packet Traceability Note

- Reviewer packet cited branch tip `3e0be5cbf94ff74cc192e88c239aebc9fb98982a` but described it as metadata-only; that was incorrect.
- Reviewer-visible implementation anchor is `3e0be5cbf94ff74cc192e88c239aebc9fb98982a` (`feat(commands): add trusted surface lookup helpers`).
- This fixer adds a metadata refresh commit on top so the handoff packet matches the real live scope instead of repeating the earlier incorrect metadata-only claim.
- Review scope for this regenerated packet is the live branch state, including the full diff from reviewer anchor `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` through the implementation anchor and this packet-refresh commit.
- That live scope includes `8` changed files and `9029` insertions / `462` deletions.

## Reviewer Required Fixes Satisfied

1. The packet is regenerated against the actual branch tip `3e0be5cbf94ff74cc192e88c239aebc9fb98982a`; it no longer describes that commit as metadata-only.
1. The packet now treats `3e0be5cbf94ff74cc192e88c239aebc9fb98982a` as the reviewer-visible implementation anchor and treats this fixer as the metadata refresh on top of it, instead of incorrectly describing `3e0be5cb...` itself as metadata-only.
2. The handoff now covers the full live branch state rather than the earlier narrow `f8d860ed...` slice, so the scope, file inventory, and risk notes match the implementation under review.
3. The AGENTS alignment is explicit: this work advances the canonical `open project/document` demo-path step and strengthens the Milestone 3 CLI-first loop by hardening the deterministic bootstrap command contract.
4. The shared-file exception note now lists every non-owned/shared path in scope for the regenerated handoff instead of naming only one shared test file.
5. This fixer pass stays metadata-only and does not expand the reviewed implementation scope beyond the handoff files needed to satisfy the reviewer packet.

## Scope Completed

- Refreshed only the handoff metadata in `THREAD.md` and `THREAD_PACKET.md` for this fixer pass so the reviewer packet leaves a commit on `codex/feat-commands` without widening the implementation scope.
- Expanded the command surface in `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, and `src/qual/commands/catalog.py` so trusted surface lookups, canonical/demo-path mappings, and parser-facing command resolution stay deterministic.
- Updated `src/qual/commands/diff_preview.py` and the unit coverage in `tests/unit/test_diff_preview.py` to keep diff-preview behavior aligned with the current command surface.
- Extended `tests/unit/test_commands_catalog.py` to cover the wider command-surface and parser-contract behavior now shipped on this branch tip.
- Regenerated `THREAD.md` and `THREAD_PACKET.md` so the handoff accurately reflects the real branch tip and review scope.

## Kickoff Budget / Limits Compliance

- This packet regeneration stayed within the current fixer-pass task budget.
- The reviewed branch tip is wider than the earlier narrow-slice packet claimed; this regenerated packet intentionally documents that wider live scope rather than repeating the invalid narrow claim.

## Approved Exception Note

- Shared/non-owned paths in scope for this branch-tip handoff:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Handoff Packet

- Branch name: `codex/feat-commands`
- Reviewer-visible implementation anchor: `3e0be5cbf94ff74cc192e88c239aebc9fb98982a`
- Current packet-refresh commit: pending this fixer commit

### Tasks Completed (Numbered)

1. Added trusted surface lookup helpers and supporting command-surface exports in `src/qual/commands/__init__.py` and `src/qual/commands/catalog.py`.
2. Hardened canonical/demo-path command resolution in `src/qual/commands/canonical.py` and `src/qual/commands/catalog.py`, including parser-surface determinism checks covered by `tests/unit/test_commands_catalog.py`.
3. Kept diff-preview command behavior and coverage aligned with the widened command surface in `src/qual/commands/diff_preview.py` and `tests/unit/test_diff_preview.py`.
4. Regenerated the handoff metadata in `THREAD.md` and `THREAD_PACKET.md` so this packet matches the actual branch tip, shared-path scope, and demo-path alignment.

### Files Changed

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

### Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`
- Verification date: `2026-04-18`

### Risks / Blockers

- Risk: `MEDIUM`
- Remaining risk: the command surface is broader than the original narrow packet described, so future follow-up reviews should continue to anchor packet claims to the real branch tip rather than a historical subset.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: CLI-first operator contract support for the active engine demo path while Textual remains disabled, preserving a deterministic bootstrap command for the workflow loop.
- `feat-commands`: keep command discovery, canonicalization, and preview flows stable as the reviewed CLI surface expands.

### Vision capability affected

- Writing-centered workflow: the operator can still begin the active engine demo path from a stable CLI bootstrap surface while Textual remains disabled.
- Canonical engine contract: trusted surface lookup helpers and parser-contract coverage keep the reviewed command catalog auditable instead of allowing silent drift across aliases or demo-path shims.

### Canonical demo-path step advanced

- Step advanced: `open project/document`
- Explicit handoff statement: this change advances the canonical `open project/document` demo-path step.
- AGENTS alignment: this change makes the canonical `open project/document` bootstrap step more real by keeping the CLI-first operator contract deterministic while Milestone 3 remains CLI-first and Textual remains disabled.
- Concrete blocker removed: the branch now documents and tests the real parser-facing command surface, reducing the risk that alias/canonical drift silently changes the operator’s first CLI step.
- Why this is MVP-loop-specific: while Textual is disabled, the CLI bootstrap command is the active operator entry into the engine workflow, so deterministic command-surface lookup protects the Milestone 3 CLI-first loop.

### Routing/provider impact note

- None.

### Proposed `README.md` patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail:
  - lane-owned implementation: `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`
  - shared/non-owned tests: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`
  - shared metadata updated for handoff accuracy: `THREAD.md`, `THREAD_PACKET.md`
