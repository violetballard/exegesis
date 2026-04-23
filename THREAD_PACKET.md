# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: regenerate the handoff so it truthfully describes the real `codex/feat-commands` branch tip, names the exact CLI-first MVP steps advanced by that tip, and records traceable approval basis for every shared path still in scope.
- Risk reason: the reviewed branch tip mixes lane-owned command implementation with shared test files, and this fixer updates shared handoff metadata that must match the true tip-level diff.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Replace the stale narrow-slice review basis with the real branch-tip diff basis.
2. Update scope, file inventory, and roadmap mapping so they describe the actual implementation present on `codex/feat-commands`.
3. Replace the vague shared-test exception note with concrete policy and commit traceability for each shared path still in scope.
4. Re-run `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Early Review Triggers

- Before first edit to any shared or integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing or config behavior.

### Stop Triggers

- Unresolved test, lint, or typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (Short Updates)

- Plan complete: switch the packet from a false cherry-picked review basis to the actual branch-tip diff.
- First green tests: recorded after the required gate rerun on `2026-04-23`.
- Before risky/shared file edit: this fixer only edits `THREAD.md` and `THREAD_PACKET.md`.
- Ready for handoff: the packet now matches the real implementation scope and its concrete MVP step mapping.

## Review Basis

- Review basis for re-review is the real branch tip for `codex/feat-commands`, not a cherry-picked subset of commits.
- Tip-level implementation basis:
  - merge base with `codex/quality-baseline`: `60136caf9ee4e1ff08d35e2da2922af78e7974d5`
  - reviewed tip before this metadata-only fixer commit: `ca17857f2039f59fbd19e0e150168f6d220a110b`
- This packet does not claim that post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` commits are metadata-only. The current branch diff includes many implementation commits after that point, including `1e04f9633c4abc4988dcb991944680b86f94f753`, `5c89ce987fc78ed158d378a988b3e211ce93145d`, and `b3be9f0c12e6fd3ecd52f1b8af2bd1b6d890e1a0`.
- Current implementation files in scope for the truthful tip-based handoff:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- Metadata refreshed by this fixer:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Scope Completed

- Built out the trusted command surface used by the current CLI fallback path, including command-surface metadata, canonical wrapper exports, deterministic route and alias helpers, parser-surface validation, shim routing, and smoke-ready invocation contracts across the owned `src/qual/commands/**` lane files.
- Hardened `src/qual/commands/catalog.py` so the CLI contract is checked against the catalog, parser-surface drift is rejected deterministically, and routed fallback subcommands such as retrieval-oriented command shims preserve their intended subcommand tokens.
- Stabilized `src/qual/commands/diff_preview.py` so `diff-preview` keeps effective labels and option-state visibility in no-diff JSON responses instead of silently dropping operator-visible review context.
- Added and expanded focused regression coverage in `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` for command-surface drift, canonical ordering, routed subcommand preservation, and no-diff preview payload fidelity.
- Refreshed `THREAD.md` and `THREAD_PACKET.md` so the handoff now covers the real branch-tip scope, the concrete MVP demo-path step mapping, and traceable approval basis for shared tests.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the `4`-task cap, `30m` budget, and metadata-only fixer scope.
- This fixer pass edits only `THREAD.md` and `THREAD_PACKET.md`.

## Canonical Demo-Path Mapping

- Exact current MVP demo-path steps advanced by this lane:
  - step 1 `open project/document`
  - step 2 `retrieve relevant material`
  - step 3 `preview and apply or reject a patch`
- Concrete blocker removed:
  - after step 1, the operator could still lose deterministic CLI routing for step 2 or lose operator-visible state during step 3 because command-surface drift, shimmed-subcommand loss, or no-diff preview-state loss could silently break the CLI fallback contract while Textual remains disabled.
- Explicit AGENTS/ROADMAP mapping statement:
  - this branch tip makes steps 2 and 3 more real, and keeps step 1 wired into them reliably, by hardening the CLI-first command contract that the current MVP loop depends on for `open project/document -> retrieve relevant material -> preview and apply or reject a patch`.

## Shared-Path Approval Basis

- Shared path still in scope: `tests/unit/test_commands_catalog.py`
  - current policy basis: `scripts/scope-check.sh` explicitly allowlists this path for `codex/feat-commands*`
  - traceable policy commits:
    - `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50` `fix(commands): align feat-commands handoff policy`
    - `c3a66bb580772d65201a630d673a8de1d4a63776` `fix(commands): tighten feat-commands packet and policy`
  - approver / policy author for those commits: `Violet Ballard`
- Shared path still in scope: `tests/unit/test_diff_preview.py`
  - current branch diff still includes this shared test file even though it is not on the present allowlist
  - traceable branch approval trail:
    - `8a38d7bde29da3ecfb3da905ff78416034b151b7` `fix(commands): approve diff preview shared regression`
    - `2afa0f7f2f23c2d73773cc9c5a2fc0007ba19be3` `fix(commands): restore diff preview scope allowance`
    - `51279575df18d44dc112129f561f2dcb7743e70f` `Restore scope-check shared-test allowance`
  - approver / policy author for those commits: `Violet Ballard`
- This fixer does not claim any new scope exception beyond the current policy file and the traceable branch-history approvals above.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Built out the trusted command-surface contract and canonical wrapper exports for the CLI fallback path in `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, and `src/qual/commands/catalog.py`.
2. Hardened deterministic command routing and parser-surface validation so routed command shims preserve the intended CLI-first MVP flow instead of silently drifting.
3. Stabilized `diff-preview` no-diff payload reporting in `src/qual/commands/diff_preview.py`.
4. Added and expanded regression coverage in `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.
5. Regenerated the handoff metadata so it now reflects the real branch-tip diff, the exact canonical demo-path steps advanced, and concrete shared-path approval traceability.

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
- Verification date: `2026-04-23`
- Verification basis: rerun on the metadata-refresh working tree immediately before the fixer commit

### Risks / Blockers

- Risk: `MEDIUM`
- Remaining risk:
  - the current policy file explicitly allowlists `tests/unit/test_commands_catalog.py`, while `tests/unit/test_diff_preview.py` depends on branch-history approval traceability rather than a present allowlist line.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` current MVP focus: CLI remains the operator-first control surface and must keep the MVP flow executable while `Exegesis Console` remains deferred.
- `ROADMAP.md` Milestone 5 (`A2UI Presentation Layer`) exit criteria: CLI must execute the MVP flow (`vault -> context -> run -> patch -> export`) against the same engine-authoritative contracts.

### Vision capability affected

- `PRODUCT_VISION.md` operator-first control surface: this branch tip keeps the CLI fallback deterministic and operator-visible so engine outputs can remain consumable by CLI now and future UI surfaces later.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Ownership detail:
  - lane-owned implementation: `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`
  - shared tests: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`
  - shared metadata updated for handoff accuracy: `THREAD.md`, `THREAD_PACKET.md`
