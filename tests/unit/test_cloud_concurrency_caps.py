from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from codex_packet_handoff.tools import launch_feature_lanes, router


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
            "max_parallel_feature_lanes_cloud": 1,
            "max_parallel_feature_lanes_local": 2,
        }
        state = {"runtime_mode": "cloud_primary"}
        with mock.patch.object(launch_feature_lanes, "load_json", side_effect=[cfg, state]):
            launch_cfg = launch_feature_lanes.runtime_launch_config()

        self.assertEqual(launch_cfg["max_parallel_feature_lanes_cloud"], 1)
        self.assertEqual(launch_cfg["max_parallel_feature_lanes_local"], 2)

    def test_runtime_launch_config_honors_lane_cloud_profile_override(self) -> None:
        cfg = {
            "runtime_mode_default": "cloud_primary",
            "profiles": {
                "worker_cloud": {"codex_cmd": "codex", "model": "gpt-5.4-mini"},
                "worker_cloud_standard_medium": {
                    "codex_cmd": "codex",
                    "model": "gpt-5.4",
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
        self.assertEqual(launch_cfg["model"], "gpt-5.4")
        self.assertEqual(launch_cfg["model_args"], ["-c", "model_reasoning_effort=medium"])

    def test_router_profile_for_role_honors_lane_cloud_profile_override(self) -> None:
        cfg = router.RouterConfig(
            model="gpt-5.1-codex",
            codex_cmd="codex",
            fallback_model="gpt-oss-120b",
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
            prefer_cli_fixer=True,
            prefer_cli_reviewer=True,
            prefer_cli_integrator=True,
            use_cli_reviewer_fallback=True,
            use_cli_integrator_fallback=True,
            profiles={
                "worker_cloud": router.LaunchProfile("codex", [], "gpt-5.4-mini", []),
                "worker_cloud_standard_medium": router.LaunchProfile(
                    "codex",
                    [],
                    "gpt-5.4",
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

        self.assertEqual(profile.model, "gpt-5.4")
        self.assertEqual(profile.model_args, ["-c", "model_reasoning_effort=medium"])

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
                fallback_model="gpt-oss-120b",
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


if __name__ == "__main__":
    unittest.main()
