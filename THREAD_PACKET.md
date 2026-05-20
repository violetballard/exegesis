## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Review target: metadata-only packet repair commit on `codex/feat-a2ui-contract`.
- Source commit(s): implementation branch range `74a1fb5d22fa3451a041bde51888f3f214ec9b51..HEAD`; this packet repair commit changes only `THREAD_PACKET.md`.
- Scope goal: Correct the A2UI handoff metadata so the review target describes the `feat-a2ui-contract` lane rather than `feat-engine-runs`.
- Scope completed: Reissued the handoff metadata for the A2UI contract lane, naming the A2UI contract scope, branch review surface, roadmap mapping, product vision mapping, and canonical demo-path step accurately.
- Roadmap item(s) affected (from `ROADMAP.md`): `Milestone 3: Real workflow loop`, specifically `feat-a2ui-contract`: shared card/action contracts and selection models.
- Vision capability affected (from `PRODUCT_VISION.md`): `Capability 4: Shared UI contract (A2UI)`, where cards/actions/selection types live in a client-agnostic shared layer and rendering adapters stay outside shared.
- Canonical demo-path step advanced (from `AGENTS.md`): `preview and apply or reject a patch`, by stabilizing the shared card/action and selection contracts the engine loop can expose to a future client without UI ambition.
- Shared/integrator-locked edits in this metadata repair commit: `NO`.
- Branch-diff control-plane note: the full `main..HEAD` branch review surface includes control-plane/shared files listed below. Those files are not changed by this metadata repair commit; they require explicit integrator/control-plane approval if the reviewer chooses to review the full branch diff instead of this metadata-only repair commit.

## Review Surface

- Metadata repair commit files changed, matching `git show --name-status HEAD` after this commit:
  - `THREAD_PACKET.md`
- Full branch diff files currently present in `main..HEAD`, matching `git diff --name-status main..HEAD` before this repair:
  - `.codex/packet_router/config.json`
  - `.codex/packet_router/example.json`
  - `THREAD_OWNERSHIP.md`
  - `packet_garden/tools/agents_coordinator.py`
  - `packet_garden/tools/daemon_monitor.py`
  - `packet_garden/tools/planner.py`
  - `packet_garden/tools/router.py`
  - `packet_garden/tools/setup.py`
  - `scripts/scope-check.sh`
  - `shared/src/exegesis_shared/contracts/__init__.py`
  - `shared/src/exegesis_shared/contracts/actions.py`
  - `shared/src/exegesis_shared/contracts/cards.py`
  - `src/qual/ui/a2ui.py`
  - `src/qual/ui/test_a2ui_fallback_safety.py`
  - `tests/unit/test_a2ui_contract.py`
  - `tests/unit/test_coordinator_reboot_resume.py`
  - `tests/unit/test_packet_planner.py`

## Tasks Completed

1. Replaced the incorrect `feat-engine-runs` handoff metadata with `feat-a2ui-contract` metadata.
2. Made the review target unambiguous as a metadata-only packet repair commit.
3. Listed the full branch diff separately, including control-plane and shared paths, so reviewers can choose whether to review only this repair commit or require integrator/control-plane handling for the broader branch surface.
4. Corrected the roadmap mapping to `ROADMAP.md` Milestone 3 `feat-a2ui-contract`.
5. Corrected the product mapping to `PRODUCT_VISION.md` Capability 4 `Shared UI contract (A2UI)`.
6. Named the canonical demo-path step advanced: `preview and apply or reject a patch`.

## Commands Run

- `make scope-check` -> failed: `THREAD_PACKET.md` is disallowed on `codex/feat-a2ui-contract`; this fixer commit intentionally repairs that control-plane handoff packet.
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed, 614 unit/smoke tests
- `./typecheck-test.sh` -> passed
- `make ci` -> failed at `make scope-check` for the same intentional `THREAD_PACKET.md` packet repair.

## Risks / Blockers

- The full `main..HEAD` branch surface contains control-plane/shared files. This metadata repair commit does not alter those files and does not itself provide integrator/control-plane approval for them.
- `make scope-check` and `make ci` require integrator/control-plane approval for this intentional `THREAD_PACKET.md` repair on a feature branch.
