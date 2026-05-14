## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Authoritative source-bearing review range: `9abf31c55f420be74389af72b7e4707bb5132790..HEAD` on branch `codex/feat-a2ui-contract`.
- Merge base: `9abf31c55f420be74389af72b7e4707bb5132790`.
- Scope completed: This packet now treats the branch tip as the merge candidate and includes every source-bearing and packet/config/doc change in that range. It no longer asks review to ignore commits between earlier A2UI runtime commits and branch tip.
- Canonical demo-path step advanced: `AGENTS.md` active MVP item `A2UI contracts with CLI fallback`. The actual submitted range also includes broad engine/retrieval/config/coordinator cleanup that supports the engine-stability and FTS-first retrieval MVP notes, so those surfaces require their proper lane/integrator review before merge approval.
- Risk class: High-risk. The submitted range touches shared contracts, retrieval, coordinator/config tooling, quality gates, docs, and many deleted legacy package/test paths. It exceeds the normal `feat-a2ui-contract` lane-owned scope.

### Corrected Task List

1. Move A2UI card/action contract definitions into the shared package and preserve compatibility imports for `src.qual` callers.
2. Keep deterministic CLI fallback materialization in `src/qual/ui/a2ui.py` and update A2UI contract tests.
3. Reshape retrieval implementation and tests around the current FTS-first/page-index/embedding strategy surfaces.
4. Consolidate runtime/package layout by deleting legacy split-package files and updating remaining `src/qual/**` entrypoints.
5. Update coordinator/router/planner/status tooling and packet-planner metadata.
6. Update scope/quality/typecheck scripts and repo-level governance docs to match the current branch shape.
7. Remove retired Textual, remote-monitoring, migration, legacy docs, offline-handoff, lane-profile, and git-helper files.
8. Correct this handoff packet so review is against the true branch-tip merge candidate.

### Changed Files

Complete changed-files list for `9abf31c55f420be74389af72b7e4707bb5132790..HEAD` before this packet-fix commit:

- `M .codex/kickoff_packets/feat-a2ui-contract.md`
- `M .codex/packet_planner/state.json`
- `M .gitignore`
- `M A2UI_SPEC.md`
- `M AGENTS.md`
- `M ARCHITECTURE.md`
- `M INTEGRATION.md`
- `D MIGRATION.md`
- `M PIPELINE_RUNBOOK.md`
- `M PRODUCT_VISION.md`
- `M README.md`
- `D REMOTE_MONITORING_SPEC.md`
- `M ROADMAP.md`
- `M THREAD_OWNERSHIP.md`
- `M THREAD_PACKET.md`
- `D client-textual/src/exegesis_textual/__init__.py`
- `D client-textual/src/exegesis_textual/app/__init__.py`
- `D client-textual/src/exegesis_textual/app/main.py`
- `D client-textual/src/exegesis_textual/cards/__init__.py`
- `D client-textual/src/exegesis_textual/cards/patch_card.py`
- `D client-textual/src/exegesis_textual/cards/plan_card.py`
- `D client-textual/src/exegesis_textual/commands/__init__.py`
- `D client-textual/src/exegesis_textual/commands/palette.py`
- `D client-textual/src/exegesis_textual/events/__init__.py`
- `D client-textual/src/exegesis_textual/inspectors/__init__.py`
- `D client-textual/src/exegesis_textual/inspectors/renderers.py`
- `D client-textual/src/exegesis_textual/layout/__init__.py`
- `D client-textual/src/exegesis_textual/layout/shell.py`
- `D client-textual/src/exegesis_textual/panes/__init__.py`
- `D client-textual/src/exegesis_textual/panes/basket_pane.py`
- `D client-textual/src/exegesis_textual/panes/document_pane.py`
- `D client-textual/src/exegesis_textual/panes/inspector_pane.py`
- `D client-textual/src/exegesis_textual/panes/project_pane.py`
- `D client-textual/src/exegesis_textual/shortcuts/__init__.py`
- `D client-textual/src/exegesis_textual/shortcuts/footer.py`
- `D client-textual/src/exegesis_textual/theme/__init__.py`
- `D client-textual/src/exegesis_textual/workflow/__init__.py`
- `D client-textual/src/exegesis_textual/workflow/workflow_pane.py`
- `D codex_packet_handoff/config/remote_monitor.example.json`
- `M codex_packet_handoff/tools/agents_coordinator.py`
- `M codex_packet_handoff/tools/codex_mcp_client.py`
- `D codex_packet_handoff/tools/control_repo_commit.py`
- `M codex_packet_handoff/tools/daemon_ctl.py`
- `M codex_packet_handoff/tools/daemon_monitor.py`
- `M codex_packet_handoff/tools/daemon_resume_check.py`
- `D codex_packet_handoff/tools/git_hygiene.py`
- `D codex_packet_handoff/tools/git_ops.py`
- `M codex_packet_handoff/tools/init_lane_meta.py`
- `D codex_packet_handoff/tools/lane_profiles.py`
- `D codex_packet_handoff/tools/lane_repo_commit.py`
- `M codex_packet_handoff/tools/launch_feature_lanes.py`
- `D codex_packet_handoff/tools/launchd_ctl.py`
- `D codex_packet_handoff/tools/launchd_daemon.sh`
- `D codex_packet_handoff/tools/local_cli_worker.py`
- `D codex_packet_handoff/tools/local_codex_runtime.py`
- `D codex_packet_handoff/tools/local_exec_sweeper.py`
- `D codex_packet_handoff/tools/log_maintenance.py`
- `D codex_packet_handoff/tools/offline_handoff_probe.py`
- `D codex_packet_handoff/tools/packet_progress.py`
- `M codex_packet_handoff/tools/planner.py`
- `D codex_packet_handoff/tools/remote_monitor_client.py`
- `D codex_packet_handoff/tools/remote_monitor_ctl.py`
- `D codex_packet_handoff/tools/remote_monitor_server.py`
- `D codex_packet_handoff/tools/remote_monitor_snapshot.py`
- `M codex_packet_handoff/tools/router.py`
- `M codex_packet_handoff/tools/runtime_mode_ctl.py`
- `M codex_packet_handoff/tools/setup.py`
- `M codex_packet_handoff/tools/status.py`
- `D codex_packet_handoff/tools/status_report.sh`
- `D docs/FUTURE_IMPORT_RAG_SPEC.md`
- `D docs/FUTURE_MVP_FEATURES_SPEC.md`
- `D docs/MVP_SPRINT_PLAN.md`
- `D docs/NOTEBOOK_CONTEXT_COMPACTION_SPEC.md`
- `D docs/POST_MVP_FEATURES_SPEC.md`
- `D docs/PROJECT_STRUCTURE.md`
- `D docs/README-for-codex.md`
- `D docs/TASKS.md`
- `D docs/milestones.md`
- `D engine/src/exegesis_engine/__init__.py`
- `D engine/src/exegesis_engine/api/__init__.py`
- `D engine/src/exegesis_engine/api/app_service.py`
- `D engine/src/exegesis_engine/api/bootstrap.py`
- `D engine/src/exegesis_engine/api/cli.py`
- `D engine/src/exegesis_engine/api/runtime_commands.py`
- `D engine/src/exegesis_engine/audit/__init__.py`
- `D engine/src/exegesis_engine/audit/event_log.py`
- `D engine/src/exegesis_engine/config/__init__.py`
- `D engine/src/exegesis_engine/config/app_config.py`
- `D engine/src/exegesis_engine/context/__init__.py`
- `D engine/src/exegesis_engine/context/basket.py`
- `D engine/src/exegesis_engine/context/store.py`
- `D engine/src/exegesis_engine/core/__init__.py`
- `D engine/src/exegesis_engine/drafting/__init__.py`
- `D engine/src/exegesis_engine/drafting/service.py`
- `D engine/src/exegesis_engine/metrics/__init__.py`
- `D engine/src/exegesis_engine/metrics/crypto.py`
- `D engine/src/exegesis_engine/metrics/db.py`
- `D engine/src/exegesis_engine/metrics/exporter.py`
- `D engine/src/exegesis_engine/metrics/recorder.py`
- `D engine/src/exegesis_engine/metrics/schema.py`
- `D engine/src/exegesis_engine/metrics/ui.py`
- `D engine/src/exegesis_engine/patches/__init__.py`
- `D engine/src/exegesis_engine/patches/patch_model.py`
- `D engine/src/exegesis_engine/patches/patch_service.py`
- `D engine/src/exegesis_engine/providers/__init__.py`
- `D engine/src/exegesis_engine/retrieval/__init__.py`
- `D engine/src/exegesis_engine/retrieval/search_service.py`
- `D engine/src/exegesis_engine/services/__init__.py`
- `D engine/src/exegesis_engine/state/__init__.py`
- `D engine/src/exegesis_engine/state/models.py`
- `D engine/src/exegesis_engine/storage/__init__.py`
- `D engine/src/exegesis_engine/storage/project_store.py`
- `D engine/src/exegesis_engine/storage/vault.py`
- `D engine/src/exegesis_engine/workflow/__init__.py`
- `D engine/src/exegesis_engine/workflow/plan_service.py`
- `D engine/src/exegesis_engine/workflow/revise_service.py`
- `M exegesis.yml`
- `D exegesis_engine/__init__.py`
- `D exegesis_shared/__init__.py`
- `D exegesis_textual/__init__.py`
- `M quality-format.sh`
- `M quality-lint.sh`
- `M quality-test.sh`
- `M scripts/common.sh`
- `M scripts/scope-check.sh`
- `M shared/src/exegesis_shared/__init__.py`
- `M shared/src/exegesis_shared/contracts/__init__.py`
- `A shared/src/exegesis_shared/contracts/a2ui.py`
- `D shared/src/exegesis_shared/contracts/actions.py`
- `D shared/src/exegesis_shared/contracts/cards.py`
- `D shared/src/exegesis_shared/models/__init__.py`
- `D shared/src/exegesis_shared/models/selection.py`
- `D shared/src/exegesis_shared/types/__init__.py`
- `D shared/src/exegesis_shared/types/object_types.py`
- `D shared/src/exegesis_shared/utils/__init__.py`
- `M src/main.py`
- `M src/qual/app.py`
- `M src/qual/audit.py`
- `M src/qual/bootstrap.py`
- `M src/qual/cli.py`
- `M src/qual/commands/__init__.py`
- `D src/qual/commands/catalog.py`
- `M src/qual/config.py`
- `M src/qual/context/__init__.py`
- `M src/qual/context/basket.py`
- `D src/qual/context/set_store.py`
- `M src/qual/context/store.py`
- `M src/qual/drafting/__init__.py`
- `M src/qual/drafting/service.py`
- `M src/qual/engine/retrieval/__init__.py`
- `A src/qual/engine/retrieval/embeddings_strategy.py`
- `M src/qual/engine/retrieval/fts_strategy.py`
- `A src/qual/engine/retrieval/pageindex_strategy.py`
- `M src/qual/engine/retrieval/payload.py`
- `M src/qual/engine/retrieval/policy.py`
- `M src/qual/engine/service.py`
- `M src/qual/metrics/__init__.py`
- `M src/qual/metrics/crypto.py`
- `M src/qual/metrics/db.py`
- `M src/qual/metrics/exporter.py`
- `M src/qual/metrics/recorder.py`
- `M src/qual/metrics/schema.py`
- `M src/qual/metrics/ui.py`
- `M src/qual/retrieval/__init__.py`
- `M src/qual/retrieval/service.py`
- `A src/qual/shared/__init__.py`
- `A src/qual/shared/contracts/__init__.py`
- `A src/qual/shared/contracts/a2ui.py`
- `M src/qual/storage/__init__.py`
- `M src/qual/storage/vault.py`
- `M src/qual/ui/a2ui.py`
- `D tests/fixtures/offline_handoff/approved_packet.md`
- `D tests/fixtures/offline_handoff/feature_packet.md`
- `D tests/fixtures/offline_handoff/integrator_bad_missing_required_parameter.txt`
- `D tests/fixtures/offline_handoff/reviewer_bad_text_format.txt`
- `D tests/fixtures/offline_handoff/reviewer_good_approved.txt`
- `D tests/fixtures/offline_handoff/reviewer_good_changes_requested.txt`
- `M tests/unit/test_a2ui_contract.py`
- `D tests/unit/test_cloud_concurrency_caps.py`
- `D tests/unit/test_commands_catalog.py`
- `M tests/unit/test_context_storage_recovery.py`
- `D tests/unit/test_coordinator_reboot_resume.py`
- `D tests/unit/test_daemon_ctl.py`
- `D tests/unit/test_daemon_monitor.py`
- `D tests/unit/test_daemon_resume_check.py`
- `D tests/unit/test_git_hygiene.py`
- `D tests/unit/test_git_ops.py`
- `D tests/unit/test_lane_profiles.py`
- `D tests/unit/test_launchd_ctl.py`
- `D tests/unit/test_local_cli_worker.py`
- `D tests/unit/test_local_exec_sweeper.py`
- `D tests/unit/test_log_maintenance.py`
- `D tests/unit/test_mvp_migration.py`
- `D tests/unit/test_offline_handoff.py`
- `A tests/unit/test_packet_planner.py`
- `D tests/unit/test_packet_progress.py`
- `D tests/unit/test_quality_test_script.py`
- `D tests/unit/test_remote_monitor.py`
- `D tests/unit/test_router_quota_fallback.py`
- `M tests/unit/test_unified_retrieval.py`
- `M typecheck-test.sh`
- `M THREAD_PACKET.md` from this packet-fix commit.

### Approval And Routing Notes

- Lane-owned paths from the kickoff were `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`.
- Shared/out-of-lane paths requiring explicit reviewer/integrator approval include `.codex/**`, repo governance docs, `codex_packet_handoff/**`, `scripts/**`, `quality-*.sh`, `typecheck-test.sh`, `shared/src/exegesis_shared/**`, `src/qual/shared/**`, retrieval/config/context/storage/metrics/CLI files under `src/qual/**`, `exegesis.yml`, and deleted legacy packages/tests/docs.
- No approval is claimed in this packet for those out-of-lane edits. They must be accepted explicitly by reviewer/integrator or split/routed through their proper engine, retrieval, coordinator, docs, and quality-gate lanes.
- Provider/routing/config behavior was touched by the submitted range through `src/qual/config.py`, `exegesis.yml`, and coordinator/router tooling, so this cannot be treated as a narrow A2UI-only review.

### Roadmap/Vision Mapping

- Roadmap item(s) affected by the A2UI slice: `ROADMAP.md` Milestone 5 A2UI Presentation Layer, specifically stable schema/versioned output and CLI fallback readiness.
- Roadmap item(s) affected by the broader submitted range: active MVP emphasis on engine stability and FTS-first retrieval, plus coordinator/automation cleanup. These require non-A2UI lane review.
- Vision capability affected by the A2UI slice: Capability 5, Agent-to-UI protocol (`A2UI`), with client-agnostic contracts and renderers outside shared.
- Vision capability affected by the broader submitted range: engine/retrieval execution and automation support for the canonical demo path. This packet does not claim that those changes are justified solely by A2UI roadmap references.

### Commands Run

- `make scope-check` -> passed for branch `codex/feat-a2ui-contract`.
- `./quality-format.sh --check` -> passed.
- `./quality-lint.sh` -> passed shell syntax and trailing-whitespace checks.
- `./quality-test.sh` -> passed smoke tests and 123 unit tests.
- `./typecheck-test.sh` -> passed Python source compilation under `src/`.
- `make ci` -> passed setup, scope-check, format, lint, typecheck, smoke tests, and 123 unit tests.

### Risks/Blockers

- The branch remains high-risk because the actual merge candidate is broad: 201 files changed before this packet-fix commit, including large deletions and source changes outside the A2UI lane.
- If reviewer/integrator requires a narrow A2UI-only candidate, this branch tip is not that candidate. The narrow A2UI work must be split to a branch whose merge range contains only that slice plus truthful packet updates.
- This corrected packet satisfies traceability by naming the branch-tip range and full file set; it does not convert out-of-lane changes into lane-owned work.

### Proposed `README.md` Patch Text

None.
