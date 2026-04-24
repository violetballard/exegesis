# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Reviewed implementation basis:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa` (`feat(commands): expose default workflow aliases`)
- Packet refresh role: `reviewer-fix metadata refresh`
- Packet refresh basis: `reissued against the real latest implementation basis so packet traceability, canonical demo-path wording, roadmap/vision scope, and ownership notes all match the actual branch contents`
- Post-fixer verification: `required gates reran successfully at 2026-04-24T08:30:03Z against the branch state that includes implementation tip 4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden the CLI command contract for the canonical `preview and apply or reject a patch` step so the public `diff-preview` review entrypoint stays catalog-locked and the default workflow aliases expose one canonical engine contract for that step.
- Risk reason: the reviewed slice changes the lane-owned command contract and one shared-by-approval regression test file, but it does not touch any integrator-locked file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Lock the live CLI parser surface to the declared command-catalog entrypoints so parser drift is detected from the authoritative public token set.
2. Keep command-contract validation fail-closed when alias-only, reordered, missing-token, or extra-token parser shapes still resolve through lookup.
3. Add regression coverage for the exact `diff-preview` removed while `diff` still resolves drift case, including the cache-warm helper path.
4. Reissue the handoff packet against the real implementation basis with explicit shared-by-approval traceability and the required canonical demo-path wording.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/__init__.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - the live parser surface now fails closed when the public `diff-preview` review token disappears, reorders, or expands unexpectedly
  - the default workflow and trusted-surface aliases now resolve to one canonical review-step engine contract instead of forcing callers to choose separate helper names
  - regression coverage proves both the parser surface and the default aliases stay pinned to the same reviewed contract

## Scope Completed

- Hardened the review-step CLI contract so the live parser surface for `diff-preview` must match the declared catalog projection.
- Added parser-drift regressions for alias substitution, missing canonical review tokens, extra tokens, and warmed-cache drift cases.
- Exposed default workflow aliases and trusted-surface aliases so downstream CLI consumers call one stable engine contract for the review/apply-or-reject branch.
- Kept the slice narrow: command-contract hardening, default alias exposure, and targeted tests only.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Required AGENTS sentence: this change makes `preview and apply or reject a patch` more real by forcing the review-step public command surface to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set.
- Concrete blocker removed: the parser can no longer silently drop the public `diff-preview` token and leave only the still-resolvable alias `diff`, and callers no longer have to choose between helper names for the same review/apply-or-reject branch.
- Scope-tightening statement: this slice claims only review-step command-contract hardening and default alias stability. It does not claim new persistence, audit-path, retrieval, patch application, export, routing, or UI behavior.

## Approved Exception Note

- Shared-by-approval edit: `tests/unit/test_commands_catalog.py`
- Approval owner: integrator-managed branch policy for `codex/feat-commands`
- Approval source:
  - `THREAD_OWNERSHIP.md` marks non-owned paths as approval-only
  - `scripts/scope-check.sh` allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*` via `is_approved_shared_test()`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Locked the live review-step parser surface to the command catalog so `diff-preview` drift fails closed.
2. Added parser-drift regression coverage for alias-only, missing-token, extra-token, and cache-warm drift cases in `tests/unit/test_commands_catalog.py`.
3. Added default workflow aliases and trusted-surface aliases in `src/qual/commands/catalog.py`, exported them from `src/qual/commands/__init__.py`, and added tests proving those aliases stay equal to the reviewed contract.
4. Regenerated the handoff packet so the approval basis matches the real branch contents and the ownership, roadmap, and vision mapping stays narrow.

### Files Changed

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

### Commands Run and Outcomes

- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`
- Verification rerun timestamp: `2026-04-24T08:30:03Z`

### Risks / Blockers

- Risks:
  - future command-surface changes must keep `_CLI_ENTRYPOINTS`, the default alias exports, and the shared regression suite aligned or the contract will fail fast by design
- Blockers:
  - none

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3 `Define and lock user-facing output contracts`, narrowly applied to the CLI review-step command boundary for `preview and apply or reject a patch`

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`, narrowly applied to the CLI-first review-step command contract while Textual remains disabled

### Routing / Provider Impact Note

- None. This diff only hardens local command-contract behavior and default alias exposure for the current review-step engine contract.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval path included: `tests/unit/test_commands_catalog.py`
- Integrator-locked edits: `NO`
- Integrator-locked paths included: `none`
