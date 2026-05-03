from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from codex_packet_handoff.tools import agents_coordinator, launch_feature_lanes, router


class CloudConcurrencyCapsTests(unittest.TestCase):
    def test_runtime_launch_config_reads_parallel_limits(self) -> None:
        cfg = {
            "runtime_mode_default": "cloud_primary",
            "profiles": {
                "worker_cloud": {"codex_cmd": "codex", "model": "gpt-5.4-mini"},
                "worker_local": {
                    "codex_cmd": "codex",
                    "codex_args": ["-c", "model_provider=lms"],
                    "model": "gpt-oss-120b",
                },
            },
            "role_profiles": {
                "feature_cloud": "worker_cloud",
                "feature_local": "worker_local",
            },
            "max_parallel_feature_lanes_cloud": 2,
            "max_parallel_feature_lanes_local": 2,
        }
        state = {"runtime_mode": "cloud_primary"}
        with mock.patch.object(launch_feature_lanes, "load_json", side_effect=[cfg, state]):
            launch_cfg = launch_feature_lanes.runtime_launch_config()

        self.assertEqual(launch_cfg["max_parallel_feature_lanes_cloud"], 2)
        self.assertEqual(launch_cfg["max_parallel_feature_lanes_local"], 2)

    def test_runtime_launch_config_honors_lane_cloud_profile_override(self) -> None:
        cfg = {
            "runtime_mode_default": "cloud_primary",
            "profiles": {
                "worker_cloud": {
                    "codex_cmd": "codex",
                    "model": "gpt-5.4-mini",
                    "model_args": ["-c", "model_reasoning_effort=medium"],
                },
                "worker_cloud_standard_medium": {
                    "codex_cmd": "codex",
                    "model": "gpt-5.5",
                    "model_args": ["-c", "model_reasoning_effort=medium"],
                },
                "worker_local": {
                    "codex_cmd": "codex",
                    "codex_args": ["-c", "model_provider=lms"],
                    "model": "gpt-oss-120b",
                },
            },
            "role_profiles": {
                "feature_cloud": "worker_cloud",
                "feature_local": "worker_local",
            },
            "lanes": {
                "feat-commands": {
                    "feature_cloud_profile": "worker_cloud_standard_medium",
                }
            },
        }
        state = {"runtime_mode": "cloud_primary"}
        with mock.patch.object(launch_feature_lanes, "load_json", side_effect=[cfg, state]):
            launch_cfg = launch_feature_lanes.runtime_launch_config("feat-commands")

        self.assertEqual(launch_cfg["profile_name"], "worker_cloud_standard_medium")
        self.assertEqual(launch_cfg["model"], "gpt-5.5")
        self.assertEqual(launch_cfg["model_args"], ["-c", "model_reasoning_effort=medium"])

    def test_runtime_launch_config_honors_lane_local_profile_override(self) -> None:
        cfg = {
            "runtime_mode_default": "cloud_primary",
            "profiles": {
                "worker_cloud": {"codex_cmd": "codex", "model": "gpt-5.4-mini"},
                "worker_local": {
                    "codex_cmd": "codex",
                    "codex_args": ["-c", "model_provider=lms"],
                    "model": "gpt-oss-20b",
                },
                "worker_local_heavy": {
                    "codex_cmd": "codex",
                    "codex_args": ["-c", "model_provider=lms"],
                    "model": "gpt-oss-120b",
                },
            },
            "role_profiles": {
                "feature_cloud": "worker_cloud",
                "feature_local": "worker_local",
                "integrator_local": "worker_local_heavy",
            },
            "lanes": {
                "feat-engine-runs": {
                    "feature_local_profile": "worker_local_heavy",
                }
            },
        }
        state = {"runtime_mode": "local_fallback"}
        with mock.patch.object(launch_feature_lanes, "load_json", side_effect=[cfg, state]):
            launch_cfg = launch_feature_lanes.runtime_launch_config("feat-engine-runs")

        self.assertEqual(launch_cfg["profile_name"], "worker_local_heavy")
        self.assertEqual(launch_cfg["model"], "gpt-oss-120b")

    def test_router_profile_for_role_honors_lane_cloud_profile_override(self) -> None:
        cfg = router.RouterConfig(
            model="gpt-5.1-codex",
            codex_cmd="codex",
            fallback_model="gpt-oss-120b",
            fallback_codex_cmd="codex",
            fallback_codex_args=["--oss", "--local-provider", "lmstudio"],
            fallback_model_args=[],
            runtime_mode_default="cloud_primary",
            auto_switch_to_local_on_quota=True,
            auto_probe_cloud_recovery=True,
            cloud_probe_cooldown_seconds=1800.0,
            cloud_probe_timeout_seconds=30.0,
            reviewer_timeout=180.0,
            integrator_timeout=900.0,
            max_packets_per_run=5,
            inline_fixer=True,
            kick_fixers_on_reviewer_backlog=True,
            fixer_kick_timeout_seconds=8.0,
            reviewer_fixer_retry_cooldown_seconds=120.0,
            fixer_quota_retry_cooldown_seconds=3600.0,
            max_cloud_fixer_kicks_per_run=1,
            max_local_fixer_kicks_per_run=1,
            max_cloud_fixer_jobs=2,
            max_local_fixer_jobs=2,
            prefer_cli_fixer=True,
            prefer_cli_reviewer=True,
            prefer_cli_integrator=True,
            use_cli_reviewer_fallback=True,
            use_cli_integrator_fallback=True,
            profiles={
                "worker_cloud": router.LaunchProfile(
                    "codex",
                    [],
                    "gpt-5.4-mini",
                    ["-c", "model_reasoning_effort=medium"],
                ),
                "worker_cloud_standard_medium": router.LaunchProfile(
                    "codex",
                    [],
                    "gpt-5.5",
                    ["-c", "model_reasoning_effort=medium"],
                ),
            },
            role_profiles={"reviewer_cloud": "worker_cloud"},
            lanes={
                "feat-retrieval-fts": {
                    "reviewer_cloud_profile": "worker_cloud_standard_medium",
                }
            },
        )

        profile = router._profile_for_role(cfg, "reviewer", local=False, lane="feat-retrieval-fts")

        self.assertEqual(profile.model, "gpt-5.5")
        self.assertEqual(profile.model_args, ["-c", "model_reasoning_effort=medium"])

    def test_router_profile_for_role_honors_lane_local_profile_override(self) -> None:
        cfg = router.RouterConfig(
            model="gpt-5.1-codex",
            codex_cmd="codex",
            fallback_model="gpt-oss-20b",
            fallback_codex_cmd="codex",
            fallback_codex_args=["-c", "model_provider=lms"],
            fallback_model_args=[],
            runtime_mode_default="cloud_primary",
            auto_switch_to_local_on_quota=True,
            auto_probe_cloud_recovery=True,
            cloud_probe_cooldown_seconds=1800.0,
            cloud_probe_timeout_seconds=30.0,
            reviewer_timeout=180.0,
            integrator_timeout=900.0,
            max_packets_per_run=5,
            inline_fixer=True,
            kick_fixers_on_reviewer_backlog=True,
            fixer_kick_timeout_seconds=8.0,
            reviewer_fixer_retry_cooldown_seconds=120.0,
            fixer_quota_retry_cooldown_seconds=3600.0,
            max_cloud_fixer_kicks_per_run=1,
            max_local_fixer_kicks_per_run=1,
            max_cloud_fixer_jobs=2,
            max_local_fixer_jobs=2,
            prefer_cli_fixer=True,
            prefer_cli_reviewer=True,
            prefer_cli_integrator=True,
            use_cli_reviewer_fallback=True,
            use_cli_integrator_fallback=True,
            profiles={
                "worker_local": router.LaunchProfile("codex", ["-c", "model_provider=lms"], "gpt-oss-20b", []),
                "worker_local_heavy": router.LaunchProfile(
                    "codex",
                    ["-c", "model_provider=lms"],
                    "gpt-oss-120b",
                    [],
                ),
            },
            role_profiles={"reviewer_local": "worker_local", "integrator_local": "worker_local_heavy"},
            lanes={
                "feat-engine-runs": {
                    "reviewer_local_profile": "worker_local_heavy",
                }
            },
        )

        profile = router._profile_for_role(cfg, "reviewer", local=True, lane="feat-engine-runs")

        self.assertEqual(profile.model, "gpt-oss-120b")

    def test_local_lms_cap_allows_feature_and_one_router_role(self) -> None:
        cfg = SimpleNamespace(max_total_local_lms_jobs=4)
        state = {
            "local_integrator_jobs": {"feat-a:packet.md": {"pid": 1001, "result_path": "/tmp/missing-integrator.json"}},
        }

        with mock.patch.object(router, "_count_active_feature_local_jobs", return_value=1), mock.patch.object(
            router, "_pid_alive", return_value=True
        ):
            self.assertTrue(router._local_lms_slot_available(cfg, state))

    def test_local_lms_cap_blocks_fifth_local_job(self) -> None:
        cfg = SimpleNamespace(max_total_local_lms_jobs=4)
        state = {
            "local_reviewer_jobs": {"feat-a": {"pid": 1001, "result_path": "/tmp/missing-reviewer.json"}},
            "local_integrator_jobs": {"feat-b:packet.md": {"pid": 1002, "result_path": "/tmp/missing-integrator.json"}},
            "fixer_fallback_jobs": {"feat-c": {"pid": 1003, "local": True}},
        }

        with mock.patch.object(router, "_count_active_feature_local_jobs", return_value=0), mock.patch.object(
            router, "_pid_alive", return_value=True
        ):
            self.assertTrue(router._local_lms_slot_available(cfg, state))

        with mock.patch.object(router, "_count_active_feature_local_jobs", return_value=1), mock.patch.object(
            router, "_pid_alive", return_value=True
        ):
            self.assertFalse(router._local_lms_slot_available(cfg, state))

    def test_coordinator_local_feature_slots_respect_four_job_cap(self) -> None:
        with (
            mock.patch.object(
                agents_coordinator,
                "load_json",
                side_effect=[
                    {"runtime_mode": "local_fallback"},
                    {"max_total_local_lms_jobs": 4},
                ],
            ),
            mock.patch.object(agents_coordinator, "find_repo_owned_local_exec_pids", return_value=[1001, 1002]),
            mock.patch.object(agents_coordinator, "_tracked_feature_exec_pids", return_value=[]),
        ):
            self.assertEqual(agents_coordinator._local_lms_feature_launch_slots(), 2)

    def test_coordinator_local_feature_slots_block_when_four_jobs_active(self) -> None:
        with (
            mock.patch.object(
                agents_coordinator,
                "load_json",
                side_effect=[
                    {"runtime_mode": "local_fallback"},
                    {"max_total_local_lms_jobs": 4},
                ],
            ),
            mock.patch.object(agents_coordinator, "find_repo_owned_local_exec_pids", return_value=[1001, 1002, 1003, 1004]),
            mock.patch.object(agents_coordinator, "_tracked_feature_exec_pids", return_value=[]),
        ):
            self.assertEqual(agents_coordinator._local_lms_feature_launch_slots(), 0)

    def test_router_tick_prioritizes_integrator_before_reviewer_fixer(self) -> None:
        cfg = SimpleNamespace(lanes={"feat-a": {}, "feat-b": {}})
        state = {}
        calls: list[str] = []

        def fake_process_once(reviewer_client, integrator_client, cfg, state, repo_cwd, reviewer_thread_ids, integrator_tid):
            calls.append("review")
            return 0, state, reviewer_thread_ids, integrator_tid

        def fake_process_integrator_backlog(integrator_client, cfg, state, repo_cwd, integrator_tid):
            calls.append("integrator")
            state["integrator_started"] = True
            return 1, state, "integrator-thread"

        def fake_process_reviewer_backlog(reviewer_client, cfg, state, repo_cwd):
            calls.append("fixer")
            state["fixer_saw_integrator_started"] = bool(state.get("integrator_started"))
            return 1, state

        with (
            mock.patch.object(router, "process_once", side_effect=fake_process_once),
            mock.patch.object(router, "process_integrator_backlog", side_effect=fake_process_integrator_backlog),
            mock.patch.object(router, "process_reviewer_backlog", side_effect=fake_process_reviewer_backlog),
            mock.patch.object(router, "save_json"),
        ):
            n, kicked, integrated, updated, reviewer_threads, integrator_tid = router._process_router_tick(
                object(),
                object(),
                cfg,
                state,
                "/repo",
                {"feat-a": "reviewer-thread"},
                None,
            )

        self.assertEqual(calls, ["review", "integrator", "fixer"])
        self.assertEqual((n, kicked, integrated), (0, 1, 1))
        self.assertTrue(updated["fixer_saw_integrator_started"])
        self.assertEqual(reviewer_threads, {"feat-a": "reviewer-thread"})
        self.assertEqual(updated["reviewer_thread_id"], "reviewer-thread")
        self.assertEqual(updated["reviewer_thread_missing_lanes"], ["feat-b"])
        self.assertEqual(integrator_tid, "integrator-thread")
        self.assertEqual(updated["integrator_thread_id"], "integrator-thread")

    def test_process_reviewer_backlog_respects_cloud_kick_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            packet_root = Path(tmpdir) / "packets"
            lanes = {
                "feat-a": {"branch": "codex/feat-a", "enabled": True},
                "feat-b": {"branch": "codex/feat-b", "enabled": True},
            }
            for lane in lanes:
                lane_dir = packet_root / lane / "inbox" / "reviewer"
                lane_dir.mkdir(parents=True, exist_ok=True)
                (lane_dir / f"R__{lane}.md").write_text("## Verdict\nCHANGES_REQUESTED\n", encoding="utf-8")

            cfg = router.RouterConfig(
                model="gpt-5.1-codex",
                codex_cmd="codex",
                fallback_model="gpt-oss-20b",
                fallback_codex_cmd="codex",
                fallback_codex_args=["-c", "model_provider=lms"],
                fallback_model_args=[],
                runtime_mode_default="cloud_primary",
                auto_switch_to_local_on_quota=True,
                auto_probe_cloud_recovery=True,
                cloud_probe_cooldown_seconds=1800.0,
                cloud_probe_timeout_seconds=30.0,
                reviewer_timeout=180.0,
                integrator_timeout=900.0,
                max_packets_per_run=5,
                inline_fixer=True,
                kick_fixers_on_reviewer_backlog=True,
                fixer_kick_timeout_seconds=8.0,
                reviewer_fixer_retry_cooldown_seconds=120.0,
                fixer_quota_retry_cooldown_seconds=3600.0,
                max_cloud_fixer_kicks_per_run=1,
                max_local_fixer_kicks_per_run=1,
                max_cloud_fixer_jobs=1,
                max_local_fixer_jobs=1,
                prefer_cli_fixer=True,
                prefer_cli_reviewer=True,
                prefer_cli_integrator=True,
                use_cli_reviewer_fallback=True,
                use_cli_integrator_fallback=True,
                profiles={},
                role_profiles={},
                lanes=lanes,
            )

            kicked_lanes = []

            def fake_ensure_lane_dirs(lane: str) -> Path:
                lane_dir = packet_root / lane
                (lane_dir / "inbox" / "feature").mkdir(parents=True, exist_ok=True)
                (lane_dir / "outbox" / "integrator").mkdir(parents=True, exist_ok=True)
                (lane_dir / "archive").mkdir(parents=True, exist_ok=True)
                return lane_dir

            def fake_run_fixer(reviewer_client, cfg, state, lane, reviewer_packet, repo_cwd, local_mode):
                kicked_lanes.append(lane)
                return state

            with mock.patch.object(router, "ensure_lane_dirs", side_effect=fake_ensure_lane_dirs), mock.patch.object(
                router, "_latest_fixer_log", return_value=None
            ), mock.patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, repo_cwd: state), mock.patch.object(
                router, "_materialize_reviewer_packet", return_value="review packet"
            ), mock.patch.object(router, "run_fixer", side_effect=fake_run_fixer):
                kicked, _ = router.process_reviewer_backlog(object(), cfg, {}, str(packet_root))

        self.assertEqual(kicked, 1)
        self.assertEqual(len(kicked_lanes), 1)

    def test_process_reviewer_backlog_ignores_stale_cloud_quota_in_local_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            packet_root = Path(tmpdir) / "packets"
            lane = "feat-a"
            lane_dir = packet_root / lane / "inbox" / "reviewer"
            lane_dir.mkdir(parents=True, exist_ok=True)
            (lane_dir / f"R__{lane}.md").write_text("## Verdict\nCHANGES_REQUESTED\n", encoding="utf-8")
            quota_log = Path(tmpdir) / "fixer.log"
            quota_log.write_text(
                "provider: openai\nERROR: You've hit your usage limit. try again at Apr 30, 2026 10:45 AM.\n",
                encoding="utf-8",
            )

            cfg = router.RouterConfig(
                model="gpt-5.1-codex",
                codex_cmd="codex",
                fallback_model="gpt-oss-20b",
                fallback_codex_cmd="codex",
                fallback_codex_args=["-c", "model_provider=lms"],
                fallback_model_args=[],
                runtime_mode_default="cloud_primary",
                auto_switch_to_local_on_quota=True,
                auto_probe_cloud_recovery=True,
                cloud_probe_cooldown_seconds=1800.0,
                cloud_probe_timeout_seconds=30.0,
                reviewer_timeout=180.0,
                integrator_timeout=900.0,
                max_packets_per_run=5,
                inline_fixer=True,
                kick_fixers_on_reviewer_backlog=True,
                fixer_kick_timeout_seconds=8.0,
                reviewer_fixer_retry_cooldown_seconds=120.0,
                fixer_quota_retry_cooldown_seconds=3600.0,
                max_cloud_fixer_kicks_per_run=1,
                max_local_fixer_kicks_per_run=1,
                max_cloud_fixer_jobs=1,
                max_local_fixer_jobs=1,
                prefer_cli_fixer=True,
                prefer_cli_reviewer=True,
                prefer_cli_integrator=True,
                use_cli_reviewer_fallback=True,
                use_cli_integrator_fallback=True,
                profiles={},
                role_profiles={},
                lanes={lane: {"branch": "codex/feat-a", "enabled": True}},
            )

            kicked_lanes = []
            state = {"runtime_mode": "local_fallback", "fixer_quota_retry_ts": {lane: 9999999999.0}}

            def fake_ensure_lane_dirs(lane_name: str) -> Path:
                lane_root = packet_root / lane_name
                (lane_root / "inbox" / "feature").mkdir(parents=True, exist_ok=True)
                (lane_root / "outbox" / "integrator").mkdir(parents=True, exist_ok=True)
                (lane_root / "archive").mkdir(parents=True, exist_ok=True)
                return lane_root

            def fake_run_fixer(reviewer_client, cfg, state, lane, reviewer_packet, repo_cwd, local_mode):
                kicked_lanes.append((lane, local_mode))
                return state

            with (
                mock.patch.object(router, "ensure_lane_dirs", side_effect=fake_ensure_lane_dirs),
                mock.patch.object(router, "_latest_fixer_log", return_value=quota_log),
                mock.patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, repo_cwd: state),
                mock.patch.object(router, "_materialize_reviewer_packet", return_value="review packet"),
                mock.patch.object(router, "run_fixer", side_effect=fake_run_fixer),
            ):
                kicked, updated = router.process_reviewer_backlog(object(), cfg, state, str(packet_root))

        self.assertEqual(kicked, 1)
        self.assertEqual(kicked_lanes, [(lane, True)])
        self.assertEqual(updated["fixer_quota_retry_ts"], {})

    def test_process_reviewer_backlog_skips_lane_that_already_advanced(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            packet_root = Path(tmpdir) / "packets"
            lane = "feat-a"
            lane_dir = packet_root / lane / "inbox" / "reviewer"
            lane_dir.mkdir(parents=True, exist_ok=True)
            (lane_dir / "R__CHANGES__codex-feat-a__1111111111111111111111111111111111111111__20260402T000000Z.md").write_text(
                "## Verdict\nCHANGES_REQUESTED\n",
                encoding="utf-8",
            )

            cfg = router.RouterConfig(
                model="gpt-5.1-codex",
                codex_cmd="codex",
                fallback_model="gpt-oss-20b",
                fallback_codex_cmd="codex",
                fallback_codex_args=["-c", "model_provider=lms"],
                fallback_model_args=[],
                runtime_mode_default="cloud_primary",
                auto_switch_to_local_on_quota=True,
                auto_probe_cloud_recovery=True,
                cloud_probe_cooldown_seconds=1800.0,
                cloud_probe_timeout_seconds=30.0,
                reviewer_timeout=180.0,
                integrator_timeout=900.0,
                max_packets_per_run=5,
                inline_fixer=True,
                kick_fixers_on_reviewer_backlog=True,
                fixer_kick_timeout_seconds=8.0,
                reviewer_fixer_retry_cooldown_seconds=120.0,
                fixer_quota_retry_cooldown_seconds=3600.0,
                max_cloud_fixer_kicks_per_run=1,
                max_local_fixer_kicks_per_run=1,
                max_cloud_fixer_jobs=1,
                max_local_fixer_jobs=1,
                prefer_cli_fixer=True,
                prefer_cli_reviewer=True,
                prefer_cli_integrator=True,
                use_cli_reviewer_fallback=True,
                use_cli_integrator_fallback=True,
                profiles={},
                role_profiles={},
                lanes={lane: {"branch": "codex/feat-a", "enabled": True}},
            )

            def fake_ensure_lane_dirs(lane_name: str) -> Path:
                lane_root = packet_root / lane_name
                (lane_root / "inbox" / "feature").mkdir(parents=True, exist_ok=True)
                (lane_root / "outbox" / "integrator").mkdir(parents=True, exist_ok=True)
                (lane_root / "archive").mkdir(parents=True, exist_ok=True)
                return lane_root

            with mock.patch.object(router, "ensure_lane_dirs", side_effect=fake_ensure_lane_dirs), mock.patch.object(
                router, "_latest_fixer_log", return_value=None
            ), mock.patch.object(router, "_branch_head_sha", return_value="2222222222222222222222222222222222222222"), mock.patch.object(
                router, "_maybe_restore_cloud", side_effect=lambda cfg, state, repo_cwd: state
            ), mock.patch.object(router, "run_fixer") as run_fixer_mock:
                kicked, state = router.process_reviewer_backlog(object(), cfg, {}, str(packet_root))

        self.assertEqual(kicked, 0)
        run_fixer_mock.assert_not_called()
        self.assertEqual(state["reviewer_fixer_cursor"], {})

    def test_process_reviewer_backlog_respects_active_fixer_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            packet_root = Path(tmpdir) / "packets"
            lanes = {
                "feat-a": {"branch": "codex/feat-a", "enabled": True},
                "feat-b": {"branch": "codex/feat-b", "enabled": True},
            }
            for lane in lanes:
                lane_dir = packet_root / lane / "inbox" / "reviewer"
                lane_dir.mkdir(parents=True, exist_ok=True)
                (lane_dir / f"R__{lane}.md").write_text("## Verdict\nCHANGES_REQUESTED\n", encoding="utf-8")

            cfg = router.RouterConfig(
                model="gpt-5.1-codex",
                codex_cmd="codex",
                fallback_model="gpt-oss-20b",
                fallback_codex_cmd="codex",
                fallback_codex_args=["-c", "model_provider=lms"],
                fallback_model_args=[],
                runtime_mode_default="cloud_primary",
                auto_switch_to_local_on_quota=True,
                auto_probe_cloud_recovery=True,
                cloud_probe_cooldown_seconds=300.0,
                cloud_probe_timeout_seconds=30.0,
                reviewer_timeout=180.0,
                integrator_timeout=900.0,
                max_packets_per_run=5,
                inline_fixer=True,
                kick_fixers_on_reviewer_backlog=True,
                fixer_kick_timeout_seconds=8.0,
                reviewer_fixer_retry_cooldown_seconds=120.0,
                fixer_quota_retry_cooldown_seconds=3600.0,
                max_cloud_fixer_kicks_per_run=1,
                max_local_fixer_kicks_per_run=1,
                max_cloud_fixer_jobs=1,
                max_local_fixer_jobs=1,
                prefer_cli_fixer=True,
                prefer_cli_reviewer=True,
                prefer_cli_integrator=True,
                use_cli_reviewer_fallback=True,
                use_cli_integrator_fallback=True,
                profiles={},
                role_profiles={},
                lanes=lanes,
            )

            state = {"fixer_fallback_jobs": {"feat-a": {"pid": 12345, "local": False}}}

            def fake_ensure_lane_dirs(lane: str) -> Path:
                lane_dir = packet_root / lane
                (lane_dir / "inbox" / "feature").mkdir(parents=True, exist_ok=True)
                (lane_dir / "outbox" / "integrator").mkdir(parents=True, exist_ok=True)
                (lane_dir / "archive").mkdir(parents=True, exist_ok=True)
                return lane_dir

            with mock.patch.object(router, "ensure_lane_dirs", side_effect=fake_ensure_lane_dirs), mock.patch.object(
                router, "_pid_alive", return_value=True
            ), mock.patch.object(router, "run_fixer") as run_fixer_mock:
                kicked, updated_state = router.process_reviewer_backlog(object(), cfg, state, str(packet_root))

        self.assertEqual(kicked, 0)
        self.assertIs(updated_state, state)
        run_fixer_mock.assert_not_called()

    def test_run_fixer_detached_cli_streams_prompt_via_stdin_for_local_mode(self) -> None:
        cfg = router.RouterConfig(
            model="gpt-5.4-mini",
            codex_cmd="codex",
            fallback_model="gpt-oss-20b",
            fallback_codex_cmd="codex",
            fallback_codex_args=["-c", "model_provider=lms"],
            fallback_model_args=[],
            runtime_mode_default="cloud_primary",
            auto_switch_to_local_on_quota=True,
            auto_probe_cloud_recovery=True,
            cloud_probe_cooldown_seconds=300.0,
            cloud_probe_timeout_seconds=30.0,
            reviewer_timeout=180.0,
            integrator_timeout=900.0,
            max_packets_per_run=5,
            inline_fixer=True,
            kick_fixers_on_reviewer_backlog=True,
            fixer_kick_timeout_seconds=8.0,
            reviewer_fixer_retry_cooldown_seconds=120.0,
            fixer_quota_retry_cooldown_seconds=3600.0,
            max_cloud_fixer_kicks_per_run=2,
            max_local_fixer_kicks_per_run=2,
            max_cloud_fixer_jobs=2,
            max_local_fixer_jobs=2,
            prefer_cli_fixer=True,
            prefer_cli_reviewer=True,
            prefer_cli_integrator=True,
            use_cli_reviewer_fallback=True,
            use_cli_integrator_fallback=True,
            profiles={
                "worker_local": router.LaunchProfile(
                    "codex",
                    ["--oss", "--local-provider", "lmstudio"],
                    "gpt-oss-120b",
                    [],
                ),
            },
            role_profiles={"fixer_local": "worker_local"},
            lanes={"feat-commands": {"branch": "codex/feat-commands"}},
        )
        state = {"runtime_mode": "local_fallback"}

        with tempfile.TemporaryDirectory() as tmp:
            worktree = Path(tmp) / "wt"
            worktree.mkdir()
            proc = SimpleNamespace(pid=12345)
            with (
                mock.patch.object(router, "_find_worktree_for_branch", return_value=str(worktree)),
                mock.patch.object(router, "_sync_lane_runbook_files"),
                mock.patch.object(router, "_profile_for_role", return_value=cfg.profiles["worker_local"]),
                mock.patch.object(router, "isolated_codex_env", return_value={"CODEX_HOME": "/tmp/codex"}),
                mock.patch.object(router, "fixer_prompt", return_value="Prompt"),
                mock.patch.object(router, "prune_log_dir"),
                mock.patch.object(router, "_count_active_feature_local_jobs", return_value=0),
                mock.patch.object(router.subprocess, "Popen", return_value=proc) as popen_mock,
            ):
                updated = router.run_fixer(
                    object(),
                    cfg,
                    state,
                    "feat-commands",
                    "review packet",
                    str(worktree),
                    local_mode=True,
                )

        self.assertEqual(updated["fixer_fallback_jobs"]["feat-commands"]["pid"], 12345)
        self.assertIn("prompt_path", updated["fixer_fallback_jobs"]["feat-commands"])
        self.assertEqual(popen_mock.call_args.args[0][-1], "-")
        self.assertEqual(popen_mock.call_args.kwargs["stdin"], router.subprocess.PIPE)
        self.assertTrue(popen_mock.call_args.kwargs["start_new_session"])

    def test_spawn_detached_cli_job_writes_prompt_to_spec_stdin_path(self) -> None:
        cfg = router.RouterConfig(
            model="gpt-5.4-mini",
            codex_cmd="codex",
            fallback_model="gpt-oss-120b",
            fallback_codex_cmd="codex",
            fallback_codex_args=["--oss", "--local-provider", "lmstudio"],
            fallback_model_args=[],
            runtime_mode_default="cloud_primary",
            auto_switch_to_local_on_quota=True,
            auto_probe_cloud_recovery=True,
            cloud_probe_cooldown_seconds=300.0,
            cloud_probe_timeout_seconds=30.0,
            reviewer_timeout=180.0,
            integrator_timeout=900.0,
            max_packets_per_run=5,
            inline_fixer=True,
            kick_fixers_on_reviewer_backlog=True,
            fixer_kick_timeout_seconds=8.0,
            reviewer_fixer_retry_cooldown_seconds=120.0,
            fixer_quota_retry_cooldown_seconds=3600.0,
            max_cloud_fixer_kicks_per_run=2,
            max_local_fixer_kicks_per_run=2,
            max_cloud_fixer_jobs=2,
            max_local_fixer_jobs=2,
            prefer_cli_fixer=True,
            prefer_cli_reviewer=True,
            prefer_cli_integrator=True,
            use_cli_reviewer_fallback=True,
            use_cli_integrator_fallback=True,
            profiles={
                "worker_cloud": router.LaunchProfile("codex", [], "gpt-5.4-mini", []),
            },
            role_profiles={"integrator_cloud": "worker_cloud"},
            lanes={"feat-commands": {"branch": "codex/feat-commands"}},
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            proc = SimpleNamespace(pid=7890)
            with (
                mock.patch.object(router, "LOCAL_JOB_ROOT", repo / "jobs"),
                mock.patch.object(router, "_profile_for_role", return_value=cfg.profiles["worker_cloud"]),
                mock.patch.object(router, "_current_resume_epoch", return_value="resume-1"),
                mock.patch.object(router.subprocess, "Popen", return_value=proc),
            ):
                job = router._spawn_detached_cli_job(
                    role="integrator",
                    cfg=cfg,
                    repo_cwd=str(repo),
                    lane="feat-commands",
                    packet_name="pkt.md",
                    prompt="very long prompt",
                    sandbox="workspace-write",
                    timeout_seconds=30.0,
                    local=False,
                )

            spec = router.load_json(Path(job["spec_path"]), {})
            self.assertIn(".prompt.txt", spec["cmd"][-1])
            self.assertNotIn("stdin_path", spec)

    def test_feature_direct_exec_bootstraps_prompt_from_file(self) -> None:
        profile_cfg = {
            "cmd": "codex",
            "cmd_args": [],
            "mode": "cloud_primary",
            "model": "gpt-5.4-mini",
            "model_args": [],
        }
        proc = SimpleNamespace(pid=2468)
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp) / "wt"
            workdir.mkdir()
            log_path = Path(tmp) / "lane.log"
            prompt_path = Path(tmp) / "lane.prompt.md"
            with mock.patch.object(launch_feature_lanes.subprocess, "Popen", return_value=proc) as popen_mock:
                pid = launch_feature_lanes._spawn_direct_exec(
                    profile_cfg,
                    workdir=str(workdir),
                    prompt="lane kickoff prompt",
                    log_path=log_path,
                    prompt_path=prompt_path,
                )
                self.assertEqual(pid, 2468)
                self.assertEqual(prompt_path.read_text(), "lane kickoff prompt")
                self.assertIn(str(prompt_path), popen_mock.call_args.args[0][-1])
                self.assertIs(popen_mock.call_args.kwargs["stdin"], launch_feature_lanes.subprocess.DEVNULL)
                self.assertTrue(popen_mock.call_args.kwargs["start_new_session"])

    def test_materialize_reviewer_packet_uses_final_verdict_packet_for_huge_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lane_dir = Path(tmp)
            reviewer_dir = lane_dir / "inbox" / "reviewer"
            reviewer_dir.mkdir(parents=True, exist_ok=True)
            reviewer_note = reviewer_dir / "R__CHANGES__lane__abc1234__20260418T000000Z.md"
            reviewer_note.write_text(
                "\n".join(
                    [
                        "Reading additional input from stdin...",
                        "tokens used",
                        "999,999",
                        "",
                        "## 1. Verdict",
                        "`CHANGES_REQUESTED`",
                        "",
                        "## 2. Findings",
                        "- Keep only the final actionable review packet.",
                        "",
                        "## 4. Required fixes before re-review",
                        "1. Do the real fix.",
                        "",
                        "Error: turn/start failed: Input exceeds the maximum length of 1048576 characters.",
                    ]
                ),
                encoding="utf-8",
            )

            materialized = router._materialize_reviewer_packet(lane_dir, reviewer_note)

        self.assertIn("## 1. Verdict", materialized)
        self.assertIn("Do the real fix.", materialized)
        self.assertNotIn("Reading additional input from stdin", materialized)
        self.assertNotIn("tokens used", materialized)


if __name__ == "__main__":
    unittest.main()
