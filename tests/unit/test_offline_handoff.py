from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from codex_packet_handoff.tools import local_codex_runtime
from codex_packet_handoff.tools import offline_handoff_probe, router, setup as setup_mod

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "offline_handoff"


class OfflineHandoffConfigTests(unittest.TestCase):
    def test_live_router_config_uses_explicit_lms_provider(self) -> None:
        cfg = json.loads((REPO_ROOT / ".codex/packet_router/config.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["fallback_codex_args"], ["--oss", "--local-provider", "lmstudio"])
        self.assertEqual(cfg["fallback_model"], "gpt-oss-120b")
        self.assertEqual(cfg["fallback_model_args"], [])
        self.assertEqual(cfg["profiles"]["worker_local"]["codex_args"], ["--oss", "--local-provider", "lmstudio"])
        self.assertEqual(cfg["profiles"]["worker_local"]["model"], "gpt-oss-120b")
        self.assertEqual(cfg["profiles"]["worker_local"]["model_args"], [])
        self.assertEqual(cfg["profiles"]["orchestrator"]["model_args"], [])
        self.assertEqual(cfg["profiles"]["worker_local_heavy"]["model"], "gpt-oss-120b")
        self.assertEqual(cfg["role_profiles"]["integrator_local"], "worker_local")
        self.assertEqual(cfg["lanes"]["feat-retrieval-fts"]["integrator_local_profile"], "worker_local_heavy")
        self.assertEqual(cfg["lanes"]["feat-a2ui-contract"]["fixer_local_profile"], "worker_local_heavy")
        self.assertEqual(cfg["lanes"]["feat-engine-runs"]["fixer_local_profile"], "worker_local_heavy")

    def test_setup_example_uses_explicit_lms_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            prev_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                setup_mod.ensure_dirs()
                setup_mod.write_example_config()
                cfg = json.loads(Path(".codex/packet_router/example.json").read_text(encoding="utf-8"))
            finally:
                os.chdir(prev_cwd)

        self.assertEqual(cfg["fallback_codex_args"], ["--oss", "--local-provider", "lmstudio"])
        self.assertEqual(cfg["fallback_model"], "gpt-oss-120b")
        self.assertEqual(cfg["fallback_model_args"], [])
        self.assertEqual(cfg["profiles"]["worker_local"]["codex_args"], ["--oss", "--local-provider", "lmstudio"])
        self.assertEqual(cfg["profiles"]["worker_local"]["model"], "gpt-oss-120b")
        self.assertEqual(cfg["profiles"]["worker_local"]["model_args"], [])
        self.assertEqual(cfg["profiles"]["orchestrator"]["model_args"], [])
        self.assertEqual(cfg["profiles"]["worker_local_heavy"]["model"], "gpt-oss-120b")
        self.assertEqual(cfg["role_profiles"]["integrator_local"], "worker_local")
        self.assertEqual(cfg["lanes"]["feat-retrieval-fts"]["integrator_local_profile"], "worker_local_heavy")
        self.assertEqual(cfg["lanes"]["feat-a2ui-contract"]["fixer_local_profile"], "worker_local_heavy")
        self.assertEqual(cfg["lanes"]["feat-engine-runs"]["fixer_local_profile"], "worker_local_heavy")


class OfflineReviewerGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = router.LaunchProfile("codex", ["--oss", "--local-provider", "lmstudio"], "gpt-oss-120b", [])

    def test_local_reviewer_rejects_known_bad_marker(self) -> None:
        bad_output = (FIXTURES / "reviewer_bad_text_format.txt").read_text(encoding="utf-8")
        cfg = SimpleNamespace(use_cli_reviewer_fallback=True, reviewer_timeout=30)

        with (
            patch.object(router, "isolated_codex_env", return_value={"CODEX_HOME": "/tmp/codex"}),
            patch.object(router, "_profile_for_role", return_value=self.profile),
            patch.object(router, "_run_cli_codex", return_value=(0, bad_output)),
        ):
            result = router._run_cli_reviewer(cfg, "/repo", "packet", "probe", local=True)

        self.assertIsNone(result)

    def test_local_reviewer_rejects_missing_verdict(self) -> None:
        cfg = SimpleNamespace(use_cli_reviewer_fallback=True, reviewer_timeout=30)

        with (
            patch.object(router, "isolated_codex_env", return_value={"CODEX_HOME": "/tmp/codex"}),
            patch.object(router, "_profile_for_role", return_value=self.profile),
            patch.object(router, "_run_cli_codex", return_value=(0, "Findings only, no verdict.\n")),
        ):
            result = router._run_cli_reviewer(cfg, "/repo", "packet", "probe", local=True)

        self.assertIsNone(result)

    def test_local_reviewer_accepts_valid_changes_requested_packet(self) -> None:
        good_output = (FIXTURES / "reviewer_good_changes_requested.txt").read_text(encoding="utf-8")
        cfg = SimpleNamespace(use_cli_reviewer_fallback=True, reviewer_timeout=30)

        with (
            patch.object(router, "isolated_codex_env", return_value={"CODEX_HOME": "/tmp/codex"}),
            patch.object(router, "_profile_for_role", return_value=self.profile),
            patch.object(router, "_run_cli_codex", return_value=(0, good_output)),
        ):
            result = router._run_cli_reviewer(cfg, "/repo", "packet", "probe", local=True)

        self.assertEqual(result, good_output.strip())

    def test_local_reviewer_uses_isolated_codex_home_and_skip_git_repo_check(self) -> None:
        cfg = SimpleNamespace(use_cli_reviewer_fallback=True, reviewer_timeout=30)
        with tempfile.TemporaryDirectory() as tmp:
            source_home = Path(tmp) / "source"
            source_home.mkdir()
            (source_home / "config.toml").write_text("[model_providers.lms]\nname='LM Studio'\n", encoding="utf-8")
            repo_root = Path(tmp) / "repo"
            repo_root.mkdir()
            with (
                patch.dict(os.environ, {"CODEX_HOME": str(source_home)}, clear=False),
                patch.object(router, "_profile_for_role", return_value=self.profile),
                patch.object(router, "_run_cli_codex", return_value=(0, "Verdict: `APPROVED`\n")) as run_cli,
            ):
                router._run_cli_reviewer(cfg, str(repo_root), "packet", "probe", local=True)

        env = run_cli.call_args.kwargs["env"]
        self.assertTrue(env["CODEX_HOME"].endswith(".codex/local_codex_runtime"))
        self.assertTrue(run_cli.call_args.kwargs["skip_git_repo_check"])

    def test_run_cli_codex_uses_devnull_stdin(self) -> None:
        completed = SimpleNamespace(returncode=0, stdout="ok")
        with patch.object(router.subprocess, "run", return_value=completed) as run_mock:
            rc, out = router._run_cli_codex(
                "codex",
                ["-c", "model_provider=lms"],
                "gpt-oss-120b",
                [],
                "read-only",
                "/repo",
                "Prompt",
                30,
            )

        self.assertEqual((rc, out), (0, "ok"))
        self.assertIs(run_mock.call_args.kwargs["stdin"], router.subprocess.DEVNULL)

    def test_expired_explicit_quota_retry_distinguishes_past_from_future(self) -> None:
        text = (
            "ERROR: You've hit your usage limit. Visit https://chatgpt.com/codex/settings/usage "
            "to purchase more credits or try again at Apr 16th, 2026 9:55 AM."
        )

        retry_at = router._parse_retry_epoch_from_quota_log(text)
        self.assertIsNotNone(retry_at)
        self.assertFalse(router._expired_explicit_quota_retry(text, now=float(retry_at) - 1))
        self.assertTrue(router._expired_explicit_quota_retry(text, now=float(retry_at) + 1))


class OfflineIntegratorGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = router.LaunchProfile("codex", ["-c", "model_provider=lms"], "gpt-oss-120b", [])

    def test_local_integrator_rejects_known_bad_marker(self) -> None:
        bad_output = (FIXTURES / "integrator_bad_missing_required_parameter.txt").read_text(encoding="utf-8")
        cfg = SimpleNamespace(use_cli_integrator_fallback=True, integrator_timeout=30)

        with (
            patch.object(router, "isolated_codex_env", return_value={"CODEX_HOME": "/tmp/codex"}),
            patch.object(router, "_profile_for_role", return_value=self.profile),
            patch.object(router, "_run_cli_codex", return_value=(0, bad_output)),
        ):
            result = router._run_cli_integrator(cfg, "/repo", "approved", local=True)

        self.assertIsNone(result)

    def test_local_integrator_accepts_nonempty_output(self) -> None:
        cfg = SimpleNamespace(use_cli_integrator_fallback=True, integrator_timeout=30)

        with (
            patch.object(router, "isolated_codex_env", return_value={"CODEX_HOME": "/tmp/codex"}),
            patch.object(router, "_profile_for_role", return_value=self.profile),
            patch.object(router, "_run_cli_codex", return_value=(0, "Integrated successfully.\n")),
        ):
            result = router._run_cli_integrator(cfg, "/repo", "approved", local=True)

        self.assertEqual(result, "Integrated successfully.")


class LocalFallbackDetachedJobTests(unittest.TestCase):
    def test_process_once_queues_detached_local_reviewer_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lane_dir = Path(tmp)
            pkt = lane_dir / "inbox" / "feature" / "F__codex-feat-commands__abc1234__20260328T000000Z.md"
            pkt.parent.mkdir(parents=True, exist_ok=True)
            pkt.write_text("Feature packet body\n", encoding="utf-8")

            cfg = SimpleNamespace(
                lanes={"feat-commands": {}},
                max_packets_per_run=1,
                auto_switch_to_local_on_quota=True,
                reviewer_timeout=30,
                integrator_timeout=30,
                inline_fixer=False,
                prefer_cli_reviewer=True,
                prefer_cli_integrator=True,
            )
            state = {"runtime_mode": "local_fallback"}
            queued_job = {"packet_name": pkt.name, "pid": 123, "result_path": str(lane_dir / "reviewer.result.json")}

            with (
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "list_new", return_value=[pkt]),
                patch.object(router, "load_json", return_value={}),
                patch.object(router, "save_json"),
                patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, cwd: state),
                patch.object(router, "_runtime_mode", return_value="local_fallback"),
                patch.object(router, "_spawn_detached_local_cli_job", return_value=queued_job),
                patch.object(router, "archive") as archive_mock,
            ):
                processed, new_state, _reviewer_threads, _integrator_tid = router.process_once(
                    SimpleNamespace(),
                    SimpleNamespace(),
                    cfg,
                    state,
                    "/repo",
                    {},
                    "",
                )

        self.assertEqual(processed, 0)
        self.assertEqual(new_state["local_reviewer_jobs"]["feat-commands"]["packet_name"], pkt.name)
        archive_mock.assert_not_called()

    def test_process_once_defers_local_reviewer_when_global_lms_cap_reached(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lane_dir = root / "lane"
            pkt = lane_dir / "inbox" / "feature" / "F__codex-feat-commands__abc1234__20260328T000000Z.md"
            pkt.parent.mkdir(parents=True, exist_ok=True)
            pkt.write_text("Feature packet body\n", encoding="utf-8")
            feature_state = root / "feature_state.json"
            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-context-storage": {
                                "mode": "local_fallback",
                                "status": "direct_exec_running",
                                "pid": 999,
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            cfg = SimpleNamespace(
                lanes={"feat-commands": {}},
                max_packets_per_run=1,
                max_total_local_lms_jobs=1,
                auto_switch_to_local_on_quota=True,
                reviewer_timeout=30,
                integrator_timeout=30,
                inline_fixer=False,
                prefer_cli_reviewer=True,
                prefer_cli_integrator=True,
            )
            state = {"runtime_mode": "local_fallback"}
            real_load_json = router.load_json

            def fake_load_json(path, default=None):
                if Path(path) == feature_state:
                    return real_load_json(path, default)
                return {}

            with (
                patch.object(router, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "list_new", return_value=[pkt]),
                patch.object(router, "load_json", side_effect=fake_load_json),
                patch.object(router, "save_json"),
                patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, cwd: state),
                patch.object(router, "_runtime_mode", return_value="local_fallback"),
                patch.object(router, "_pid_alive", side_effect=lambda pid: pid == 999),
                patch.object(router, "_spawn_detached_local_cli_job") as spawn_mock,
            ):
                processed, new_state, _reviewer_threads, _integrator_tid = router.process_once(
                    SimpleNamespace(),
                    SimpleNamespace(),
                    cfg,
                    state,
                    "/repo",
                    {},
                    "",
                )

        self.assertEqual(processed, 0)
        self.assertEqual(new_state.get("local_reviewer_jobs"), {})
        spawn_mock.assert_not_called()

    def test_process_once_completes_detached_local_reviewer_job_on_later_tick(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lane_dir = Path(tmp)
            pkt = lane_dir / "inbox" / "feature" / "F__codex-feat-commands__abc1234__20260328T000000Z.md"
            pkt.parent.mkdir(parents=True, exist_ok=True)
            pkt.write_text("Feature packet body\n", encoding="utf-8")

            cfg = SimpleNamespace(
                lanes={"feat-commands": {}},
                max_packets_per_run=1,
                auto_switch_to_local_on_quota=True,
                reviewer_timeout=30,
                integrator_timeout=30,
                inline_fixer=False,
                prefer_cli_reviewer=True,
                prefer_cli_integrator=True,
            )
            state = {
                "runtime_mode": "local_fallback",
                "local_reviewer_jobs": {
                    "feat-commands": {
                        "packet_name": pkt.name,
                        "pid": 0,
                        "result_path": str(lane_dir / "reviewer.result.json"),
                        "output_path": str(lane_dir / "reviewer.out.log"),
                    }
                },
            }

            with (
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "list_new", return_value=[pkt]),
                patch.object(router, "load_json", return_value={}),
                patch.object(router, "save_json"),
                patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, cwd: state),
                patch.object(router, "_runtime_mode", return_value="local_fallback"),
                patch.object(
                    router,
                    "_poll_detached_local_cli_job",
                    return_value={
                        "done": True,
                        "status": "ok",
                        "rc": 0,
                        "error": "",
                        "output": "Verdict: `CHANGES_REQUESTED`\n\nPlease revise.\n",
                    },
                ),
            ):
                processed, new_state, _reviewer_threads, _integrator_tid = router.process_once(
                    SimpleNamespace(),
                    SimpleNamespace(),
                    cfg,
                    state,
                    "/repo",
                    {},
                    "",
                )

        self.assertEqual(processed, 1)
        self.assertEqual(new_state["local_reviewer_jobs"], {})

    def test_process_integrator_backlog_queues_detached_local_integrator_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lane_dir = Path(tmp)
            pkt = lane_dir / "outbox" / "integrator" / "R__APPROVED__codex-feat-commands__abc1234__20260328T000000Z.md"
            pkt.parent.mkdir(parents=True, exist_ok=True)
            pkt.write_text("Verdict: `APPROVED`\n", encoding="utf-8")

            cfg = SimpleNamespace(
                lanes={"feat-commands": {}},
                max_packets_per_run=1,
                integrator_timeout=30,
                prefer_cli_integrator=True,
            )
            state = {"runtime_mode": "local_fallback"}
            queued_job = {"packet_name": pkt.name, "pid": 456, "result_path": str(lane_dir / "integrator.result.json")}

            with (
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, cwd: state),
                patch.object(router, "_runtime_mode", return_value="local_fallback"),
                patch.object(router, "_spawn_detached_cli_job", return_value=queued_job),
                patch.object(router, "archive") as archive_mock,
            ):
                processed, new_state, _integrator_tid = router.process_integrator_backlog(
                    SimpleNamespace(),
                    cfg,
                    state,
                    "/repo",
                    "",
                )

        self.assertEqual(processed, 0)
        self.assertEqual(len(new_state["local_integrator_jobs"]), 1)
        archive_mock.assert_not_called()

    def test_process_integrator_backlog_sanitizes_transcript_wrapped_approval_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lane_dir = Path(tmp)
            pkt = lane_dir / "outbox" / "integrator" / "R__APPROVED__codex-feat-commands__abc1234__20260328T000000Z.md"
            pkt.parent.mkdir(parents=True, exist_ok=True)
            pkt.write_text(
                "\n".join(
                    [
                        "Reading additional input from stdin...",
                        "tests/fixtures/offline_handoff/integrator_bad_missing_required_parameter.txt",
                        "",
                        "## Verdict",
                        "`APPROVED`",
                        "",
                        "## Findings (highest severity first)",
                        "- None.",
                    ]
                ),
                encoding="utf-8",
            )

            cfg = SimpleNamespace(
                lanes={"feat-commands": {}},
                max_packets_per_run=1,
                integrator_timeout=30,
                prefer_cli_integrator=True,
            )
            state = {"runtime_mode": "local_fallback"}
            queued_job = {"packet_name": pkt.name, "pid": 456, "result_path": str(lane_dir / "integrator.result.json")}

            with (
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, cwd: state),
                patch.object(router, "_runtime_mode", return_value="local_fallback"),
                patch.object(router, "_spawn_detached_cli_job", return_value=queued_job) as spawn_mock,
                patch.object(router, "archive") as archive_mock,
            ):
                processed, new_state, _integrator_tid = router.process_integrator_backlog(
                    SimpleNamespace(),
                    cfg,
                    state,
                    "/repo",
                    "",
                )

        self.assertEqual(processed, 0)
        self.assertEqual(len(new_state["local_integrator_jobs"]), 1)
        archive_mock.assert_not_called()
        prompt = spawn_mock.call_args.kwargs["prompt"]
        self.assertIn("## Verdict\n`APPROVED`", prompt)
        self.assertNotIn("Reading additional input from stdin", prompt)
        self.assertNotIn("integrator_bad_missing_required_parameter.txt", prompt)

    def test_process_integrator_backlog_queues_detached_cloud_integrator_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lane_dir = Path(tmp)
            pkt = lane_dir / "outbox" / "integrator" / "R__APPROVED__codex-feat-commands__abc1234__20260328T000000Z.md"
            pkt.parent.mkdir(parents=True, exist_ok=True)
            pkt.write_text("Verdict: `APPROVED`\n", encoding="utf-8")

            cfg = SimpleNamespace(
                lanes={"feat-commands": {}},
                max_packets_per_run=1,
                integrator_timeout=30,
                prefer_cli_integrator=True,
                auto_switch_to_local_on_quota=True,
                cloud_probe_cooldown_seconds=30,
            )
            state = {"runtime_mode": "cloud_primary"}
            queued_job = {"packet_name": pkt.name, "pid": 456, "result_path": str(lane_dir / "integrator.result.json")}

            with (
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, cwd: state),
                patch.object(router, "_runtime_mode", return_value="cloud_primary"),
                patch.object(router, "_spawn_detached_cli_job", return_value=queued_job),
                patch.object(router, "archive") as archive_mock,
            ):
                processed, new_state, _integrator_tid = router.process_integrator_backlog(
                    SimpleNamespace(),
                    cfg,
                    state,
                    "/repo",
                    "",
                )

        self.assertEqual(processed, 0)
        self.assertEqual(len(new_state["cloud_integrator_jobs"]), 1)
        archive_mock.assert_not_called()

    def test_process_integrator_backlog_completes_detached_local_job_on_later_tick(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lane_dir = Path(tmp)
            pkt = lane_dir / "outbox" / "integrator" / "R__APPROVED__codex-feat-commands__abc1234__20260328T000000Z.md"
            pkt.parent.mkdir(parents=True, exist_ok=True)
            pkt.write_text("Verdict: `APPROVED`\n", encoding="utf-8")

            cfg = SimpleNamespace(
                lanes={"feat-commands": {}},
                max_packets_per_run=1,
                integrator_timeout=30,
                prefer_cli_integrator=True,
            )
            job_key = f"feat-commands:{pkt.name}"
            state = {
                "runtime_mode": "local_fallback",
                "local_integrator_jobs": {
                    job_key: {
                        "packet_name": pkt.name,
                        "pid": 0,
                        "result_path": str(lane_dir / "integrator.result.json"),
                        "output_path": str(lane_dir / "integrator.out.log"),
                    }
                },
                "local_integrator_retry_ts": {},
            }

            with (
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, cwd: state),
                patch.object(router, "_runtime_mode", return_value="local_fallback"),
                patch.object(
                    router,
                    "_poll_detached_local_cli_job",
                    return_value={
                        "done": True,
                        "status": "ok",
                        "rc": 0,
                        "error": "",
                        "output": "Integrated successfully.\n",
                    },
                ),
            ):
                processed, new_state, _integrator_tid = router.process_integrator_backlog(
                    SimpleNamespace(),
                    cfg,
                    state,
                    "/repo",
                    "",
                )

        self.assertEqual(processed, 1)
        self.assertEqual(new_state["local_integrator_jobs"], {})

    def test_process_integrator_backlog_hands_failed_local_job_back_to_fixer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lane_dir = Path(tmp)
            pkt = lane_dir / "outbox" / "integrator" / "R__APPROVED__codex-feat-commands__abc1234__20260328T000000Z.md"
            pkt.parent.mkdir(parents=True, exist_ok=True)
            pkt.write_text("Verdict: `APPROVED`\n", encoding="utf-8")

            cfg = SimpleNamespace(
                lanes={"feat-commands": {}},
                max_packets_per_run=1,
                integrator_timeout=30,
                prefer_cli_integrator=True,
            )
            job_key = f"feat-commands:{pkt.name}"
            state = {
                "runtime_mode": "local_fallback",
                "local_integrator_jobs": {
                    job_key: {
                        "packet_name": pkt.name,
                        "pid": 0,
                        "result_path": str(lane_dir / "integrator.result.json"),
                        "output_path": str(lane_dir / "integrator.out.log"),
                    }
                },
                "local_integrator_retry_ts": {job_key: 123.0},
            }

            with (
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, cwd: state),
                patch.object(router, "_runtime_mode", return_value="local_fallback"),
                patch.object(
                    router,
                    "_poll_detached_local_cli_job",
                    return_value={
                        "done": True,
                        "status": "error",
                        "rc": 1,
                        "error": "local integrator job failed",
                        "output": "FAILED test_scope_check_blocks_engine_work_on_console_shell_lane",
                    },
                ),
            ):
                processed, new_state, _integrator_tid = router.process_integrator_backlog(
                    SimpleNamespace(),
                    cfg,
                    state,
                    "/repo",
                    "",
                )

            reviewer_notes = list((lane_dir / "inbox" / "reviewer").glob("R__CHANGES__codex-feat-commands__abc1234__*.md"))
            failed_approvals = list((lane_dir / "archive" / "integrator_failed").glob(pkt.name))
            self.assertEqual(processed, 0)
            self.assertEqual(new_state["local_integrator_jobs"], {})
            self.assertEqual(new_state["local_integrator_retry_ts"], {})
            self.assertFalse(pkt.exists())
            self.assertEqual(len(failed_approvals), 1)
            self.assertEqual(len(reviewer_notes), 1)
            note = reviewer_notes[0].read_text(encoding="utf-8")
            self.assertIn("Verdict: `CHANGES_REQUESTED`", note)
            self.assertIn("failed during integrator merge/check execution", note)
            self.assertIn("test_scope_check_blocks_engine_work_on_console_shell_lane", note)

    def test_process_integrator_backlog_completes_detached_cloud_job_on_later_tick(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lane_dir = Path(tmp)
            pkt = lane_dir / "outbox" / "integrator" / "R__APPROVED__codex-feat-commands__abc1234__20260328T000000Z.md"
            pkt.parent.mkdir(parents=True, exist_ok=True)
            pkt.write_text("Verdict: `APPROVED`\n", encoding="utf-8")

            cfg = SimpleNamespace(
                lanes={"feat-commands": {}},
                max_packets_per_run=1,
                integrator_timeout=30,
                prefer_cli_integrator=True,
                auto_switch_to_local_on_quota=True,
                cloud_probe_cooldown_seconds=30,
            )
            job_key = f"feat-commands:{pkt.name}"
            state = {
                "runtime_mode": "cloud_primary",
                "cloud_integrator_jobs": {
                    job_key: {
                        "packet_name": pkt.name,
                        "pid": 0,
                        "result_path": str(lane_dir / "integrator.result.json"),
                        "output_path": str(lane_dir / "integrator.out.log"),
                    }
                },
                "cloud_integrator_retry_ts": {},
            }

            with (
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, cwd: state),
                patch.object(router, "_runtime_mode", return_value="cloud_primary"),
                patch.object(
                    router,
                    "_poll_detached_local_cli_job",
                    return_value={
                        "done": True,
                        "status": "ok",
                        "rc": 0,
                        "error": "",
                        "output": "Integrated successfully.\n",
                    },
                ),
            ):
                processed, new_state, _integrator_tid = router.process_integrator_backlog(
                    SimpleNamespace(),
                    cfg,
                    state,
                    "/repo",
                    "",
                )

        self.assertEqual(processed, 1)
        self.assertEqual(new_state["cloud_integrator_jobs"], {})


class OfflineHandoffProbeTests(unittest.TestCase):
    def test_probe_uses_scratch_workspace_and_returns_output(self) -> None:
        fixture = FIXTURES / "feature_packet.md"

        with (
            patch.object(offline_handoff_probe, "load_cfg", return_value=SimpleNamespace()),
            patch.object(
                offline_handoff_probe,
                "_run_cli_reviewer",
                return_value="Verdict: `APPROVED`\n\nLooks good.\n",
            ) as run_reviewer,
        ):
            result = offline_handoff_probe.run_probe("reviewer", fixture)

        self.assertTrue(result["ok"])
        self.assertEqual(result["fixture"], str(fixture))
        self.assertIn("offline-handoff-probe-", Path(result["scratch_workspace"]).name)
        self.assertEqual(result["output"], "Verdict: `APPROVED`\n\nLooks good.\n")
        scratch = run_reviewer.call_args.args[1]
        self.assertNotEqual(Path(scratch), REPO_ROOT)
        self.assertNotEqual(Path(scratch).parent, REPO_ROOT)


class LocalCodexRuntimeTests(unittest.TestCase):
    def test_isolated_codex_env_writes_minimal_local_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source_home = Path(tmp) / "source"
            source_home.mkdir()
            (source_home / "config.toml").write_text(
                "\n".join(
                    [
                        "model = 'gpt-5.4'",
                        "model_reasoning_effort = 'xhigh'",
                        "oss_provider = 'lmstudio'",
                        "",
                        "[projects.\"/tmp/repo\"]",
                        "trust_level = 'trusted'",
                        "",
                        "[model_providers.lms]",
                        "name = 'LM Studio'",
                        "base_url = 'http://127.0.0.1:1234/v1'",
                        "",
                        "[profiles.gpt-oss-20b-lms]",
                        "model_provider = 'lms'",
                        "model = 'gpt-oss-20b'",
                        "",
                        "[plugins.\"github@openai-curated\"]",
                        "enabled = true",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            repo_root = Path(tmp) / "repo"
            repo_root.mkdir()

            with patch.dict(os.environ, {"CODEX_HOME": str(source_home)}, clear=False):
                env = local_codex_runtime.isolated_codex_env(str(repo_root))

            target_home = Path(env["CODEX_HOME"])
            written = (target_home / "config.toml").read_text(encoding="utf-8")
            self.assertIn('model = "gpt-oss-120b"', written)
            self.assertIn('oss_provider = "lmstudio"', written)
            self.assertIn('[model_providers.lms]', written)
            self.assertIn('base_url = "http://127.0.0.1:1234/v1"', written)
            self.assertIn(f'[projects."{repo_root.resolve()}"]', written)
            self.assertIn("[features]", written)
            self.assertIn("plugins = false", written)
            self.assertIn("responses_websockets = false", written)
            self.assertIn("responses_websockets_v2 = false", written)
            self.assertNotIn("gpt-5.4", written)
            self.assertNotIn('[plugins."github@openai-curated"]', written)
