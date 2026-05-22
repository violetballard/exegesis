from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from packet_garden.tools import agents_coordinator, launch_feature_lanes, router


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
            "max_total_cloud_jobs": 4,
            "max_total_local_lms_jobs": 4,
        }
        state = {"runtime_mode": "cloud_primary"}
        with mock.patch.object(launch_feature_lanes, "load_json", side_effect=[cfg, state]):
            launch_cfg = launch_feature_lanes.runtime_launch_config()

        self.assertEqual(launch_cfg["max_parallel_feature_lanes_cloud"], 2)
        self.assertEqual(launch_cfg["max_parallel_feature_lanes_local"], 2)
        self.assertEqual(launch_cfg["max_total_cloud_jobs"], 4)
        self.assertEqual(launch_cfg["max_total_local_lms_jobs"], 4)

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

    def test_runtime_launch_config_explicit_provider_overrides_hybrid_state(self) -> None:
        cfg = {
            "runtime_mode_default": "hybrid",
            "profiles": {
                "worker_cloud": {"codex_cmd": "codex", "model": "gpt-5.5"},
                "worker_local": {
                    "codex_cmd": "opencode",
                    "model": "gemma-4-31b-it",
                    "harness": "opencode",
                },
            },
            "role_profiles": {
                "feature_cloud": "worker_cloud",
                "feature_local": "worker_local",
            },
        }
        state = {"runtime_mode": "hybrid", "cloud_available": True}

        with mock.patch.object(launch_feature_lanes, "load_json", side_effect=[cfg, state]):
            local_cfg = launch_feature_lanes.runtime_launch_config("feat-commands", provider="local")
        with mock.patch.object(launch_feature_lanes, "load_json", side_effect=[cfg, state]):
            cloud_cfg = launch_feature_lanes.runtime_launch_config("feat-commands", provider="cloud")

        self.assertEqual(local_cfg["mode"], "local_fallback")
        self.assertEqual(local_cfg["profile_name"], "worker_local")
        self.assertEqual(cloud_cfg["mode"], "cloud_primary")
        self.assertEqual(cloud_cfg["profile_name"], "worker_cloud")

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
            max_cloud_feature_jobs=1,
            max_cloud_reviewer_jobs=1,
            max_cloud_integrator_jobs=1,
            max_total_cloud_jobs=4,
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
            max_cloud_feature_jobs=1,
            max_cloud_reviewer_jobs=1,
            max_cloud_integrator_jobs=1,
            max_total_cloud_jobs=4,
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

    def test_coordinator_local_feature_slots_ignore_cloud_feature_pids(self) -> None:
        with (
            mock.patch.object(
                agents_coordinator,
                "load_json",
                side_effect=[
                    {"runtime_mode": "hybrid"},
                    {"max_total_local_lms_jobs": 4},
                    {
                        "lanes": {
                            "feat-cloud": {"mode": "cloud_primary", "pid": 1001},
                            "feat-local": {"mode": "local_fallback", "pid": 1002},
                        }
                    },
                ],
            ),
            mock.patch.object(agents_coordinator, "find_repo_owned_local_exec_pids", return_value=[]),
            mock.patch.object(agents_coordinator, "_pid_alive", return_value=True),
        ):
            self.assertEqual(agents_coordinator._local_lms_feature_launch_slots(), 3)

    def test_coordinator_counts_active_local_fixer_jobs(self) -> None:
        router_state = {
            "fixer_fallback_jobs": {
                "feat-retrieval-fts": {"pid": 1234, "local": True},
                "feat-cloud": {"pid": 5678, "local": False},
                "feat-stale": {"pid": 9999, "local": True},
            }
        }

        def fake_pid_alive(pid: int) -> bool:
            return pid == 1234

        with (
            mock.patch.object(agents_coordinator, "load_json", return_value=router_state),
            mock.patch.object(agents_coordinator, "_pid_alive", side_effect=fake_pid_alive),
        ):
            self.assertEqual(agents_coordinator._active_local_fixer_jobs(), 1)

    def test_feature_launcher_bounds_local_launches_by_total_lms_cap(self) -> None:
        launch_cfg = {"mode": "local_fallback", "max_total_local_lms_jobs": 4}
        feature_state = {
            "lanes": {
                "feat-context-storage": {"mode": "local_fallback", "pid": 1111},
                "feat-cloud": {"mode": "cloud_primary", "pid": 2222},
                "feat-stale": {"mode": "local_fallback", "pid": 3333},
            }
        }
        router_state = {
            "fixer_fallback_jobs": {
                "feat-retrieval-fts": {"pid": 4444, "local": True},
                "feat-cloud": {"pid": 5555, "local": False},
            },
            "local_integrator_jobs": {"feat-engine-runs:packet": {"pid": 6666}},
        }

        def fake_pid_alive(pid: int) -> bool:
            return pid in {1111, 4444, 6666}

        with (
            mock.patch.object(launch_feature_lanes, "load_json", return_value=router_state),
            mock.patch.object(launch_feature_lanes, "_pid_alive", side_effect=fake_pid_alive),
        ):
            self.assertEqual(launch_feature_lanes._local_lms_launch_slots(launch_cfg, feature_state), 1)

    def test_feature_launcher_bounds_cloud_launches_by_total_cloud_cap(self) -> None:
        launch_cfg = {"mode": "cloud_primary", "max_cloud_feature_jobs": 4, "max_total_cloud_jobs": 4}
        feature_state = {
            "lanes": {
                "feat-engine": {"mode": "cloud_primary", "pid": 1111},
                "feat-context": {"mode": "local_fallback", "pid": 2222},
            }
        }
        router_state = {
            "cloud_reviewer_jobs": {"feat-review:packet": {"pid": 6666}},
            "cloud_integrator_jobs": {"feat-retrieval:packet": {"pid": 3333}},
            "fixer_fallback_jobs": {
                "feat-a": {"pid": 4444, "local": False},
                "feat-b": {"pid": 5555, "local": True},
            },
        }

        def fake_pid_alive(pid: int) -> bool:
            return pid in {1111, 3333, 4444, 5555, 6666}

        with (
            mock.patch.object(launch_feature_lanes, "load_json", return_value=router_state),
            mock.patch.object(launch_feature_lanes, "_pid_alive", side_effect=fake_pid_alive),
        ):
            self.assertEqual(launch_feature_lanes._cloud_feature_launch_slots(launch_cfg, feature_state), 0)

    def test_router_cloud_role_slots_share_total_cloud_cap(self) -> None:
        cfg = SimpleNamespace(
            max_cloud_feature_jobs=4,
            max_cloud_reviewer_jobs=4,
            max_cloud_integrator_jobs=4,
            max_cloud_fixer_jobs=4,
            max_total_cloud_jobs=4,
            runtime_mode_default="hybrid",
        )
        state = {
            "runtime_mode": "hybrid",
            "cloud_available": True,
            "cloud_integrator_jobs": {"feat-a:packet": {"pid": 1111, "result_path": "/tmp/missing-cloud-integrator-result"}},
            "fixer_fallback_jobs": {
                "feat-b": {"pid": 2222, "local": False},
                "feat-local": {"pid": 3333, "local": True},
            },
        }

        with (
            mock.patch.object(router, "_count_active_feature_cloud_jobs", return_value=2),
            mock.patch.object(router, "_pid_alive", side_effect=lambda pid: pid in {1111, 2222, 3333}),
        ):
            self.assertFalse(router._cloud_role_slot_available(cfg, state, "integrator"))

    def test_router_counts_untracked_cloud_integrator_execs_against_cloud_cap(self) -> None:
        cfg = SimpleNamespace(
            max_cloud_feature_jobs=4,
            max_cloud_reviewer_jobs=4,
            max_cloud_integrator_jobs=1,
            max_cloud_fixer_jobs=4,
            max_total_cloud_jobs=4,
            runtime_mode_default="hybrid",
        )
        state = {
            "runtime_mode": "hybrid",
            "cloud_available": True,
        }

        with (
            mock.patch.object(router, "_count_active_feature_cloud_jobs", return_value=0),
            mock.patch.object(router, "_live_untracked_cloud_integrator_exec_pids", return_value=[9999]),
        ):
            self.assertFalse(router._cloud_role_slot_available(cfg, state, "integrator"))
            self.assertEqual(router._count_active_cloud_jobs(state), 1)

    def test_router_blocks_second_active_integrator_for_same_lane(self) -> None:
        state = {
            "cloud_integrator_jobs": {
                "feat-a2ui-contract:R__APPROVED__old.md": {
                    "lane": "feat-a2ui-contract",
                    "packet_name": "R__APPROVED__old.md",
                    "pid": 1111,
                    "result_path": "/tmp/missing-a2ui-integrator-result",
                }
            }
        }

        with mock.patch.object(router, "_pid_alive", side_effect=lambda pid: pid == 1111):
            self.assertTrue(router._lane_has_active_integrator_job(state, "feat-a2ui-contract"))
            self.assertFalse(router._lane_has_active_integrator_job(state, "feat-engine-runs"))

    def test_prepare_cloud_integrator_does_not_spawn_second_packet_for_same_lane(self) -> None:
        cfg = SimpleNamespace(
            auto_switch_to_local_on_quota=True,
            integrator_timeout=900.0,
            max_cloud_integrator_jobs=4,
        )
        state = {
            "runtime_mode": "hybrid",
            "cloud_available": True,
            "cloud_integrator_jobs": {
                "feat-a2ui-contract:R__APPROVED__old.md": {
                    "lane": "feat-a2ui-contract",
                    "packet_name": "R__APPROVED__old.md",
                    "pid": 1111,
                    "result_path": "/tmp/missing-a2ui-integrator-result",
                }
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            pkt = Path(tmpdir) / "R__APPROVED__new.md"
            pkt.write_text("## Verdict: APPROVED\n", encoding="utf-8")
            with (
                mock.patch.object(router, "_pid_alive", side_effect=lambda pid: pid == 1111),
                mock.patch.object(router, "_spawn_detached_cli_job") as spawn_mock,
            ):
                ready, output, next_state = router._prepare_cli_integrator_result(
                    cfg,
                    state,
                    str(Path(tmpdir)),
                    "feat-a2ui-contract",
                    pkt,
                    pkt.read_text(encoding="utf-8"),
                    local=False,
                )

        self.assertFalse(ready)
        self.assertEqual(output, "")
        self.assertIs(next_state, state)
        spawn_mock.assert_not_called()

    def test_router_process_command_rows_prefers_wide_process_listing(self) -> None:
        completed = mock.Mock(returncode=0, stdout=" 9999 codex exec You are the INTEGRATOR\n")

        with mock.patch.object(router.subprocess, "run", return_value=completed) as run:
            rows = router._process_command_rows()

        self.assertEqual(rows, [(9999, "codex exec You are the INTEGRATOR")])
        self.assertEqual(run.call_args.args[0], ["ps", "-wwaxo", "pid=,command="])

    def test_cloud_reviewers_can_share_total_cloud_cap(self) -> None:
        cfg = SimpleNamespace(
            max_cloud_feature_jobs=4,
            max_cloud_reviewer_jobs=1,
            max_cloud_integrator_jobs=4,
            max_cloud_fixer_jobs=4,
            max_total_cloud_jobs=4,
            runtime_mode_default="hybrid",
        )
        state = {
            "runtime_mode": "hybrid",
            "cloud_available": True,
            "cloud_reviewer_jobs": {
                "feat-a": {"pid": 1111, "result_path": "/tmp/missing-a"},
                "feat-b": {"pid": 2222, "result_path": "/tmp/missing-b"},
            },
        }

        with (
            mock.patch.object(router, "_count_active_feature_cloud_jobs", return_value=1),
            mock.patch.object(router, "_pid_alive", side_effect=lambda pid: pid in {1111, 2222}),
        ):
            self.assertTrue(router._cloud_role_slot_available(cfg, state, "reviewer"))

        state["cloud_reviewer_jobs"]["feat-c"] = {"pid": 3333, "result_path": "/tmp/missing-c"}
        with (
            mock.patch.object(router, "_count_active_feature_cloud_jobs", return_value=1),
            mock.patch.object(router, "_pid_alive", side_effect=lambda pid: pid in {1111, 2222, 3333}),
        ):
            self.assertFalse(router._cloud_role_slot_available(cfg, state, "reviewer"))

    def test_prepare_cloud_reviewer_uses_shared_total_cap(self) -> None:
        cfg = SimpleNamespace(
            runtime_mode_default="hybrid",
            auto_switch_to_local_on_quota=True,
            reviewer_timeout=180.0,
            max_cloud_feature_jobs=4,
            max_cloud_reviewer_jobs=1,
            max_cloud_integrator_jobs=4,
            max_cloud_fixer_jobs=4,
            max_total_cloud_jobs=4,
        )
        state = {
            "runtime_mode": "hybrid",
            "cloud_available": True,
            "cloud_reviewer_jobs": {
                "feat-a": {
                    "packet_name": "F__feat-a.md",
                    "pid": 1111,
                    "result_path": "/tmp/missing-a",
                }
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            pkt_path = Path(tmpdir) / "F__feat-b.md"
            pkt_path.write_text("feature packet", encoding="utf-8")
            queued_job = {
                "packet_name": pkt_path.name,
                "pid": 2222,
                "result_path": str(Path(tmpdir) / "missing-b"),
            }

            with (
                mock.patch.object(router, "_pid_alive", side_effect=lambda pid: pid == 1111),
                mock.patch.object(router, "_count_active_feature_cloud_jobs", return_value=1),
                mock.patch.object(router, "_spawn_detached_cli_job", return_value=queued_job) as spawn_mock,
            ):
                ready, text, updated = router._prepare_cli_reviewer_result(
                    cfg,
                    state,
                    str(Path(tmpdir)),
                    "feat-b",
                    pkt_path,
                    "feature packet",
                    local=False,
                )

        self.assertFalse(ready)
        self.assertEqual(text, "")
        self.assertIn("feat-b", updated["cloud_reviewer_jobs"])
        spawn_mock.assert_called_once()

    def test_coordinator_refills_features_around_active_fixer(self) -> None:
        state_doc: dict[str, object] = {}
        launched: list[str] = []

        def fake_run_cmd(cmd: list[str]) -> tuple[int, str]:
            launched.extend(cmd[cmd.index("--lanes") + 1 :])
            return 0, ""

        with (
            mock.patch.object(agents_coordinator, "_enabled_lanes", return_value=["feat-a", "feat-b", "feat-c"]),
            mock.patch.object(agents_coordinator, "_lane_queue_empty", return_value=True),
            mock.patch.object(agents_coordinator, "_lane_has_active_feature_session", return_value=False),
            mock.patch.object(agents_coordinator, "_feature_thread_state", return_value={}),
            mock.patch.object(agents_coordinator, "_local_lms_feature_launch_slots", return_value=3),
            mock.patch.object(agents_coordinator, "_active_local_router_jobs", return_value=1),
            mock.patch.object(agents_coordinator, "_has_router_priority_backlog", return_value=True),
            mock.patch.object(agents_coordinator, "_has_lane_backlog", return_value=True),
            mock.patch.object(agents_coordinator, "run_cmd", side_effect=fake_run_cmd),
        ):
            self.assertEqual(agents_coordinator._launch_free_lanes(state_doc), ["feat-a", "feat-b", "feat-c"])

        self.assertEqual(launched, ["feat-a", "feat-b", "feat-c"])

    def test_coordinator_reserves_slot_for_unstarted_fixer_backlog(self) -> None:
        state_doc: dict[str, object] = {}
        launched: list[str] = []

        def fake_run_cmd(cmd: list[str]) -> tuple[int, str]:
            launched.extend(cmd[cmd.index("--lanes") + 1 :])
            return 0, ""

        with (
            mock.patch.object(agents_coordinator, "_enabled_lanes", return_value=["feat-a", "feat-b", "feat-c"]),
            mock.patch.object(agents_coordinator, "_lane_queue_empty", return_value=True),
            mock.patch.object(agents_coordinator, "_lane_has_active_feature_session", return_value=False),
            mock.patch.object(agents_coordinator, "_feature_thread_state", return_value={}),
            mock.patch.object(agents_coordinator, "_local_lms_feature_launch_slots", return_value=3),
            mock.patch.object(agents_coordinator, "_active_local_router_jobs", return_value=0),
            mock.patch.object(agents_coordinator, "_has_router_priority_backlog", return_value=True),
            mock.patch.object(agents_coordinator, "_has_lane_backlog", return_value=True),
            mock.patch.object(agents_coordinator, "_cloud_feature_launch_slots", return_value=0),
            mock.patch.object(agents_coordinator, "run_cmd", side_effect=fake_run_cmd),
        ):
            self.assertEqual(agents_coordinator._launch_free_lanes(state_doc), ["feat-a", "feat-b"])

        self.assertEqual(launched, ["feat-a", "feat-b"])

    def test_coordinator_uses_spare_cloud_capacity_with_router_backlog(self) -> None:
        state_doc: dict[str, object] = {}
        calls: list[list[str]] = []

        def fake_run_cmd(cmd: list[str]) -> tuple[int, str]:
            calls.append(cmd)
            return 0, ""

        with (
            mock.patch.object(agents_coordinator, "_enabled_lanes", return_value=["feat-a", "feat-b"]),
            mock.patch.object(agents_coordinator, "_lane_queue_empty", return_value=True),
            mock.patch.object(agents_coordinator, "_lane_has_active_feature_session", return_value=False),
            mock.patch.object(agents_coordinator, "_feature_thread_state", return_value={}),
            mock.patch.object(agents_coordinator, "_local_lms_feature_launch_slots", return_value=1),
            mock.patch.object(agents_coordinator, "_active_local_router_jobs", return_value=1),
            mock.patch.object(agents_coordinator, "_has_router_priority_backlog", return_value=False),
            mock.patch.object(agents_coordinator, "_has_lane_backlog", return_value=True),
            mock.patch.object(agents_coordinator, "_cloud_feature_launch_slots", return_value=2),
            mock.patch.object(agents_coordinator, "run_cmd", side_effect=fake_run_cmd),
        ):
            self.assertEqual(agents_coordinator._launch_free_lanes(state_doc), ["feat-a", "feat-b"])

        self.assertEqual(len(calls), 2)
        self.assertIn("--provider", calls[0])
        self.assertEqual(calls[0][calls[0].index("--provider") + 1], "local")
        self.assertEqual(calls[0][-2:], ["--lanes", "feat-a"])
        self.assertEqual(calls[1][calls[1].index("--provider") + 1], "cloud")
        self.assertEqual(calls[1][-2:], ["--lanes", "feat-b"])

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

        self.assertEqual(calls, ["integrator", "review", "integrator", "fixer"])
        self.assertEqual((n, kicked, integrated), (0, 1, 2))
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
            max_cloud_feature_jobs=1,
            max_cloud_reviewer_jobs=1,
            max_cloud_integrator_jobs=1,
            max_total_cloud_jobs=4,
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

    def test_process_reviewer_backlog_prioritizes_milestone_closure_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            packet_root = Path(tmpdir) / "packets"
            lanes = {
                "feat-context-storage": {"branch": "codex/feat-context-storage", "enabled": True},
                "feat-a2ui-contract": {"branch": "codex/feat-a2ui-contract", "enabled": True},
                "feat-engine-runs": {"branch": "codex/feat-engine-runs", "enabled": True},
                "feat-retrieval-fts": {"branch": "codex/feat-retrieval-fts", "enabled": True},
            }
            for lane in lanes:
                lane_dir = packet_root / lane / "inbox" / "reviewer"
                lane_dir.mkdir(parents=True, exist_ok=True)
                (lane_dir / f"R__{lane}.md").write_text("## Verdict\nCHANGES_REQUESTED\n", encoding="utf-8")

            cfg = router.RouterConfig(
                model="gpt-5.1-codex",
                codex_cmd="codex",
                fallback_model="gemma-4-31b-it",
                fallback_codex_cmd="codex",
                fallback_codex_args=["-c", "model_provider=lms"],
                fallback_model_args=[],
                runtime_mode_default="hybrid",
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
                max_local_fixer_kicks_per_run=2,
                max_cloud_fixer_jobs=1,
                max_local_fixer_jobs=3,
                max_cloud_feature_jobs=1,
                max_cloud_reviewer_jobs=1,
                max_cloud_integrator_jobs=1,
                max_total_cloud_jobs=4,
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

            with mock.patch.object(router, "PACKETS_ROOT", packet_root), mock.patch.object(
                router, "ensure_lane_dirs", side_effect=fake_ensure_lane_dirs
            ), mock.patch.object(router, "_latest_fixer_log", return_value=None), mock.patch.object(
                router, "_maybe_restore_cloud", side_effect=lambda cfg, state, repo_cwd: state
            ), mock.patch.object(
                router, "_materialize_reviewer_packet", return_value="review packet"
            ), mock.patch.object(router, "run_fixer", side_effect=fake_run_fixer):
                kicked, _ = router.process_reviewer_backlog(object(), cfg, {}, str(packet_root))

        self.assertEqual(kicked, 2)
        self.assertEqual(kicked_lanes, ["feat-context-storage", "feat-retrieval-fts"])

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
            max_cloud_feature_jobs=1,
            max_cloud_reviewer_jobs=1,
            max_cloud_integrator_jobs=1,
            max_total_cloud_jobs=4,
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
                mock.patch.object(router, "_local_lms_slot_available", return_value=True),
                mock.patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, repo_cwd: state),
                mock.patch.object(router, "_materialize_reviewer_packet", return_value="review packet"),
                mock.patch.object(router, "run_fixer", side_effect=fake_run_fixer),
            ):
                kicked, updated = router.process_reviewer_backlog(object(), cfg, state, str(packet_root))

        self.assertEqual(kicked, 1)
        self.assertEqual(kicked_lanes, [(lane, True)])
        self.assertEqual(updated["fixer_quota_retry_ts"], {})

    def test_process_reviewer_backlog_uses_one_cloud_retry_after_local_no_tool_fixer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            packet_root = Path(tmpdir) / "packets"
            lane = "feat-engine-runs"
            lane_dir = packet_root / lane / "inbox" / "reviewer"
            lane_dir.mkdir(parents=True, exist_ok=True)
            (lane_dir / f"R__{lane}.md").write_text("## Verdict\nCHANGES_REQUESTED\n", encoding="utf-8")

            cfg = router.RouterConfig(
                model="gpt-5.1-codex",
                codex_cmd="codex",
                fallback_model="gemma-4-31b-it",
                fallback_codex_cmd="opencode",
                fallback_codex_args=[],
                fallback_model_args=[],
                runtime_mode_default="hybrid",
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
                max_cloud_feature_jobs=4,
                max_cloud_reviewer_jobs=4,
                max_cloud_integrator_jobs=4,
                max_total_cloud_jobs=4,
                prefer_cli_fixer=True,
                prefer_cli_reviewer=True,
                prefer_cli_integrator=True,
                use_cli_reviewer_fallback=True,
                use_cli_integrator_fallback=True,
                profiles={},
                role_profiles={},
                lanes={lane: {"branch": f"codex/{lane}", "enabled": True}},
            )

            kicked_lanes = []
            state = {"runtime_mode": "hybrid", "cloud_available": True, "fixer_prefer_cloud_once": {lane: {"reason": "no tool"}}}

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
                mock.patch.object(router, "_local_lms_slot_available", return_value=True),
                mock.patch.object(router, "_cloud_role_slot_available", return_value=True),
                mock.patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, repo_cwd: state),
                mock.patch.object(router, "_materialize_reviewer_packet", return_value="review packet"),
                mock.patch.object(router, "run_fixer", side_effect=fake_run_fixer),
            ):
                kicked, updated = router.process_reviewer_backlog(object(), cfg, state, str(packet_root))

        self.assertEqual(kicked, 1)
        self.assertEqual(kicked_lanes, [(lane, False)])
        self.assertEqual(updated["fixer_prefer_cloud_once"], {})

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
            max_cloud_feature_jobs=1,
            max_cloud_reviewer_jobs=1,
            max_cloud_integrator_jobs=1,
            max_total_cloud_jobs=4,
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
            max_cloud_feature_jobs=1,
            max_cloud_reviewer_jobs=1,
            max_cloud_integrator_jobs=1,
            max_total_cloud_jobs=4,
                prefer_cli_fixer=True,
                prefer_cli_reviewer=True,
                prefer_cli_integrator=True,
                use_cli_reviewer_fallback=True,
                use_cli_integrator_fallback=True,
                profiles={},
                role_profiles={},
                lanes=lanes,
            )

            state = {
                "fixer_fallback_jobs": {"feat-a": {"pid": 12345, "local": False}},
                "local_reviewer_jobs": {
                    "feat-local-a": {"pid": 20001, "result_path": "/tmp/missing-a.json"},
                    "feat-local-b": {"pid": 20002, "result_path": "/tmp/missing-b.json"},
                    "feat-local-c": {"pid": 20003, "result_path": "/tmp/missing-c.json"},
                    "feat-local-d": {"pid": 20004, "result_path": "/tmp/missing-d.json"},
                },
            }

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
            max_cloud_feature_jobs=1,
            max_cloud_reviewer_jobs=1,
            max_cloud_integrator_jobs=1,
            max_total_cloud_jobs=4,
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
                mock.patch.object(router, "ROUTER_ROOT", Path(tmp) / "router"),
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

    def test_fixer_prompt_blocks_control_plane_metadata_repairs(self) -> None:
        prompt = router.fixer_prompt(
            "feat-a2ui-contract",
            "codex/feat-a2ui-contract",
            "Required fix: update THREAD_PACKET.md and .codex/lane_meta/feat-a2ui-contract.json",
            "/tmp/worktree",
        )

        self.assertIn("control-plane metadata fix required", prompt)
        self.assertIn("Do not edit or commit control-plane files from this fixer", prompt)
        self.assertIn("THREAD_PACKET.md", prompt)
        self.assertIn("packet_garden/**", prompt)

    def test_reviewer_backlog_routes_metadata_repairs_to_cloud_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            packet_root = Path(tmpdir) / "packets"
            lane = "feat-engine-runs"
            lane_dir = packet_root / lane / "inbox" / "reviewer"
            lane_dir.mkdir(parents=True, exist_ok=True)
            note = lane_dir / "R__CHANGES__codex-feat-engine-runs__abc123__20260520T000000Z.md"
            note.write_text(
                "## Verdict: `CHANGES_REQUESTED`\n\n"
                "## Findings\n"
                "1. implementation range is not reviewable locally.\n"
                "2. Roadmap mapping is off-plan.\n\n"
                "## Required fixes before re-review\n"
                "1. Reissue the packet with a locally resolvable implementation target.\n"
                "2. Correct handoff metadata and THREAD_PACKET.md references.\n",
                encoding="utf-8",
            )
            cfg = SimpleNamespace(
                inline_fixer=True,
                kick_fixers_on_reviewer_backlog=True,
                lanes={lane: {"branch": "codex/feat-engine-runs", "enabled": True}},
                max_local_fixer_kicks_per_run=1,
                max_cloud_fixer_kicks_per_run=1,
                max_local_fixer_jobs=1,
                max_cloud_fixer_jobs=1,
                max_total_local_lms_jobs=4,
                max_total_cloud_jobs=4,
                reviewer_fixer_retry_cooldown_seconds=120.0,
                fixer_quota_retry_cooldown_seconds=3600.0,
                auto_switch_to_local_on_quota=True,
            )

            def fake_ensure_lane_dirs(lane_name: str) -> Path:
                lane_root = packet_root / lane_name
                (lane_root / "inbox" / "feature").mkdir(parents=True, exist_ok=True)
                (lane_root / "outbox" / "integrator").mkdir(parents=True, exist_ok=True)
                (lane_root / "archive").mkdir(parents=True, exist_ok=True)
                return lane_root

            metadata_calls: list[tuple[str, str]] = []

            def fake_prepare_metadata(*args, **kwargs):
                metadata_calls.append((args[3], args[4].name))
                return False, args[1]

            with (
                mock.patch.object(router, "ensure_lane_dirs", side_effect=fake_ensure_lane_dirs),
                mock.patch.object(router, "_local_lms_slot_available", return_value=True),
                mock.patch.object(router, "_materialize_reviewer_packet", return_value="review packet"),
                mock.patch.object(router, "_prepare_metadata_repair_job", side_effect=fake_prepare_metadata),
                mock.patch.object(router, "run_fixer") as run_fixer_mock,
            ):
                kicked, updated = router.process_reviewer_backlog(object(), cfg, {}, str(packet_root))

        self.assertEqual(kicked, 0)
        self.assertEqual(metadata_calls, [(lane, note.name)])
        run_fixer_mock.assert_not_called()
        self.assertEqual(updated.get("reviewer_fixer_cursor"), {})

    def test_missing_concrete_handoff_tasks_routes_to_metadata_repair(self) -> None:
        note_text = (
            "## Verdict: `CHANGES_REQUESTED`\n\n"
            "## Findings\n"
            "The handoff packet does not provide concrete completed tasks.\n\n"
            "## Required fixes before re-review\n"
            "1. Replace the placeholder task list with concrete numbered tasks completed.\n"
            "2. Add the canonical demo-path step advanced by the feature implementation.\n"
            "3. Correct the missing handoff fields in `.codex/lane_meta/feat-retrieval-fts.json`.\n"
        )

        self.assertTrue(router._requires_control_plane_metadata_repair(note_text))

    def test_metadata_repair_sandbox_block_falls_back_to_local_control_plane_repair(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            packet_root = root / ".codex" / "packets" / "lanes"
            lane = "feat-engine-runs"
            lane_root = packet_root / lane
            reviewer_dir = lane_root / "inbox" / "reviewer"
            feature_dir = lane_root / "inbox" / "feature"
            reviewer_dir.mkdir(parents=True, exist_ok=True)
            feature_dir.mkdir(parents=True, exist_ok=True)
            note = reviewer_dir / "R__CHANGES__codex-feat-engine-runs__abc123__20260520T000000Z.md"
            note.write_text("## Verdict: `CHANGES_REQUESTED`\n\nmetadata repair required\n", encoding="utf-8")
            (feature_dir / "F__codex-feat-engine-runs__abc123__20260520T000000Z.shared.md").write_text(
                "stale shared-only packet",
                encoding="utf-8",
            )
            lane_meta = root / ".codex" / "lane_meta" / f"{lane}.json"
            lane_meta.parent.mkdir(parents=True, exist_ok=True)
            lane_meta.write_text(
                json.dumps(
                    {
                        "roadmap_items": ["Milestone 4: Retrieval Layer (Planned)"],
                        "source_commits": ["missing..range"],
                    }
                ),
                encoding="utf-8",
            )
            planner_state = root / ".codex" / "packet_planner" / "state.json"
            planner_state.parent.mkdir(parents=True, exist_ok=True)
            planner_state.write_text(
                json.dumps({"lanes": {lane: {"last_submitted_sha": "abc123", "last_emitted_packet": "old.md"}}}),
                encoding="utf-8",
            )

            def fake_run_git(args: list[str], **_kwargs: object):
                class Result:
                    returncode = 0
                    stdout = "headsha\n"

                result = Result()
                if args[:2] == ["merge-base", "HEAD"]:
                    result.stdout = "basesha\n"
                return result

            old_cwd = os.getcwd()
            os.chdir(root)
            try:
                with (
                    mock.patch.object(router, "PACKETS_ROOT", packet_root),
                    mock.patch.object(router, "run_git", side_effect=fake_run_git),
                ):
                    repair = router._repair_control_plane_metadata_locally(
                        str(root),
                        lane,
                        "codex/feat-engine-runs",
                        note,
                    )
            finally:
                os.chdir(old_cwd)

            repaired_meta = json.loads(lane_meta.read_text(encoding="utf-8"))
            repaired_planner_state = json.loads(planner_state.read_text(encoding="utf-8"))
            self.assertEqual(repaired_meta["source_commits"], ["basesha..headsha"])
            self.assertIn("Milestone 3: Real workflow loop", " ".join(repaired_meta["roadmap_items"]))
            self.assertNotIn("Retrieval Layer", " ".join(repaired_meta["roadmap_items"]))
            self.assertFalse(note.exists())
            self.assertEqual(repair["shared_only_archived"], 1)
            self.assertNotIn("last_submitted_sha", repaired_planner_state["lanes"][lane])
            self.assertEqual(repaired_planner_state["lanes"][lane]["force_reemit_sha"], "headsha")
            self.assertEqual(
                repaired_planner_state["lanes"][lane]["force_reemit_reason"],
                "control_plane_metadata_repair",
            )

    def test_metadata_repair_writes_retrieval_specific_handoff_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            packet_root = root / ".codex" / "packets" / "lanes"
            lane = "feat-retrieval-fts"
            lane_root = packet_root / lane
            reviewer_dir = lane_root / "inbox" / "reviewer"
            reviewer_dir.mkdir(parents=True, exist_ok=True)
            note = reviewer_dir / "R__CHANGES__codex-feat-retrieval-fts__abc123__20260520T000000Z.md"
            note.write_text("## Verdict: `CHANGES_REQUESTED`\n\nmissing handoff fields\n", encoding="utf-8")
            lane_meta = root / ".codex" / "lane_meta" / f"{lane}.json"
            lane_meta.parent.mkdir(parents=True, exist_ok=True)
            lane_meta.write_text("{}", encoding="utf-8")

            def fake_run_git(args: list[str], **_kwargs: object):
                class Result:
                    returncode = 0
                    stdout = "retrievalhead\n"

                result = Result()
                if args[:2] == ["merge-base", "HEAD"]:
                    result.stdout = "retrievalbase\n"
                return result

            old_cwd = os.getcwd()
            os.chdir(root)
            try:
                with (
                    mock.patch.object(router, "PACKETS_ROOT", packet_root),
                    mock.patch.object(router, "run_git", side_effect=fake_run_git),
                ):
                    router._repair_control_plane_metadata_locally(
                        str(root),
                        lane,
                        "codex/feat-retrieval-fts",
                        note,
                    )
            finally:
                os.chdir(old_cwd)

            repaired_meta = json.loads(lane_meta.read_text(encoding="utf-8"))
            repair_text = (root / ".codex" / "metadata_repairs" / f"{lane}.md").read_text(encoding="utf-8")
            self.assertIn("deterministic FTS provenance", repaired_meta["canonical_demo_path_step"])
            self.assertIn("retrieval demo-path contract", " ".join(repaired_meta["tasks_completed"]))
            self.assertIn("Concrete tasks completed", repair_text)
            self.assertFalse((root / ".codex" / "kickoff_packets" / f"{lane}.md").exists())

    def test_metadata_repair_jobs_count_against_cloud_total_cap(self) -> None:
        state = {
            "metadata_repair_jobs": {
                "feat-engine-runs": {"pid": 12345, "local": False, "result_path": "/tmp/missing-result.json"},
            }
        }
        with (
            mock.patch.object(router, "_count_active_feature_cloud_jobs", return_value=0),
            mock.patch.object(router, "_live_untracked_cloud_integrator_exec_pids", return_value=[]),
            mock.patch.object(router, "_pid_alive", return_value=True),
        ):
            self.assertEqual(router._count_active_cloud_jobs(state), 1)

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
            max_cloud_feature_jobs=1,
            max_cloud_reviewer_jobs=1,
            max_cloud_integrator_jobs=1,
            max_total_cloud_jobs=4,
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
            rg_config = repo.resolve() / ".codex" / "agent_ripgrep_config"
            self.assertEqual(spec["env_overrides"]["RIPGREP_CONFIG_PATH"], str(rg_config))
            self.assertIn("!.codex/**", rg_config.read_text(encoding="utf-8"))
            self.assertIn("!.agents/**", rg_config.read_text(encoding="utf-8"))

    def test_spawn_detached_cli_job_sends_prompt_directly_to_opencode(self) -> None:
        cfg = router.RouterConfig(
            model="gpt-5.4-mini",
            codex_cmd="codex",
            fallback_model="gemma-4-31b-it",
            fallback_codex_cmd="opencode",
            fallback_codex_args=[],
            fallback_model_args=[],
            runtime_mode_default="local_fallback",
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
            max_cloud_feature_jobs=1,
            max_cloud_reviewer_jobs=1,
            max_cloud_integrator_jobs=1,
            max_total_cloud_jobs=4,
            prefer_cli_fixer=True,
            prefer_cli_reviewer=True,
            prefer_cli_integrator=True,
            use_cli_reviewer_fallback=True,
            use_cli_integrator_fallback=True,
            profiles={
                "worker_local": router.LaunchProfile("opencode", [], "gemma-4-31b-it", [], harness="opencode"),
            },
            role_profiles={"fixer_local": "worker_local"},
            lanes={"feat-commands": {"branch": "codex/feat-commands"}},
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            proc = SimpleNamespace(pid=7890)
            with (
                mock.patch.object(router, "LOCAL_JOB_ROOT", repo / "jobs"),
                mock.patch.object(router, "_profile_for_role", return_value=cfg.profiles["worker_local"]),
                mock.patch.object(router, "_current_resume_epoch", return_value="resume-1"),
                mock.patch.object(router.subprocess, "Popen", return_value=proc),
            ):
                job = router._spawn_detached_cli_job(
                    role="fixer",
                    cfg=cfg,
                    repo_cwd=str(repo),
                    lane="feat-commands",
                    packet_name="pkt.md",
                    prompt="very long prompt",
                    sandbox="workspace-write",
                    timeout_seconds=30.0,
                    local=True,
                )

            spec = router.load_json(Path(job["spec_path"]), {})
            self.assertEqual(spec["cmd"][-1], "very long prompt")
            self.assertNotIn(".prompt.txt", spec["cmd"][-1])
            self.assertNotIn("--add-dir", spec["cmd"])

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
            repo_root = Path(tmp) / "repo"
            repo_root.mkdir()
            with (
                mock.patch.object(launch_feature_lanes, "REPO_ROOT", repo_root),
                mock.patch.object(launch_feature_lanes.subprocess, "Popen", return_value=proc) as popen_mock,
            ):
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
                self.assertEqual(
                    popen_mock.call_args.kwargs["env"]["RIPGREP_CONFIG_PATH"],
                    str(repo_root.resolve() / ".codex" / "agent_ripgrep_config"),
                )
                rg_config = (repo_root.resolve() / ".codex" / "agent_ripgrep_config").read_text(
                    encoding="utf-8"
                )
                self.assertIn("!.codex/**", rg_config)
                self.assertIn("!.agents/**", rg_config)
                self.assertTrue(popen_mock.call_args.kwargs["start_new_session"])

    def test_feature_direct_exec_sends_prompt_directly_to_opencode(self) -> None:
        profile_cfg = {
            "cmd": "opencode",
            "cmd_args": [],
            "harness": "opencode",
            "mode": "local_fallback",
            "model": "gemma-4-31b-it",
            "model_args": [],
        }
        proc = SimpleNamespace(pid=2468)
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp) / "wt"
            workdir.mkdir()
            log_path = Path(tmp) / "lane.log"
            prompt_path = Path(tmp) / "lane.prompt.md"
            repo_root = Path(tmp) / "repo"
            repo_root.mkdir()
            with (
                mock.patch.object(launch_feature_lanes, "REPO_ROOT", repo_root),
                mock.patch.object(launch_feature_lanes.subprocess, "Popen", return_value=proc) as popen_mock,
            ):
                pid = launch_feature_lanes._spawn_direct_exec(
                    profile_cfg,
                    workdir=str(workdir),
                    prompt="lane kickoff prompt",
                    log_path=log_path,
                    prompt_path=prompt_path,
                )
                self.assertEqual(pid, 2468)
                self.assertEqual(prompt_path.read_text(), "lane kickoff prompt")
                cmd = popen_mock.call_args.args[0]
                self.assertEqual(cmd[-1], "lane kickoff prompt")
                self.assertNotIn(str(prompt_path), cmd[-1])
                self.assertEqual(cmd[:4], ["opencode", "run", "--model", "lmstudio/gemma-4-31b-it"])

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
