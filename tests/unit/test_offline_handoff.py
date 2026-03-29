from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from codex_packet_handoff.tools import offline_handoff_probe, router, setup as setup_mod

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "offline_handoff"


class OfflineHandoffConfigTests(unittest.TestCase):
    def test_live_router_config_uses_explicit_lms_provider(self) -> None:
        cfg = json.loads((REPO_ROOT / ".codex/packet_router/config.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["fallback_codex_args"], ["-c", "model_provider=lms"])
        self.assertEqual(cfg["fallback_model"], "gpt-oss-120b")
        self.assertEqual(cfg["profiles"]["worker_local"]["codex_args"], ["-c", "model_provider=lms"])
        self.assertEqual(cfg["profiles"]["worker_local"]["model"], "gpt-oss-120b")

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

        self.assertEqual(cfg["fallback_codex_args"], ["-c", "model_provider=lms"])
        self.assertEqual(cfg["fallback_model"], "gpt-oss-120b")
        self.assertEqual(cfg["profiles"]["worker_local"]["codex_args"], ["-c", "model_provider=lms"])
        self.assertEqual(cfg["profiles"]["worker_local"]["model"], "gpt-oss-120b")


class OfflineReviewerGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = router.LaunchProfile("codex", ["-c", "model_provider=lms"], "gpt-oss-120b", [])

    def test_local_reviewer_rejects_known_bad_marker(self) -> None:
        bad_output = (FIXTURES / "reviewer_bad_text_format.txt").read_text(encoding="utf-8")
        cfg = SimpleNamespace(use_cli_reviewer_fallback=True, reviewer_timeout=30)

        with (
            patch.object(router, "_profile_for_role", return_value=self.profile),
            patch.object(router, "_run_cli_codex", return_value=(0, bad_output)),
        ):
            result = router._run_cli_reviewer(cfg, "/repo", "packet", "probe", local=True)

        self.assertIsNone(result)

    def test_local_reviewer_rejects_missing_verdict(self) -> None:
        cfg = SimpleNamespace(use_cli_reviewer_fallback=True, reviewer_timeout=30)

        with (
            patch.object(router, "_profile_for_role", return_value=self.profile),
            patch.object(router, "_run_cli_codex", return_value=(0, "Findings only, no verdict.\n")),
        ):
            result = router._run_cli_reviewer(cfg, "/repo", "packet", "probe", local=True)

        self.assertIsNone(result)

    def test_local_reviewer_accepts_valid_changes_requested_packet(self) -> None:
        good_output = (FIXTURES / "reviewer_good_changes_requested.txt").read_text(encoding="utf-8")
        cfg = SimpleNamespace(use_cli_reviewer_fallback=True, reviewer_timeout=30)

        with (
            patch.object(router, "_profile_for_role", return_value=self.profile),
            patch.object(router, "_run_cli_codex", return_value=(0, good_output)),
        ):
            result = router._run_cli_reviewer(cfg, "/repo", "packet", "probe", local=True)

        self.assertEqual(result, good_output.strip())


class OfflineIntegratorGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = router.LaunchProfile("codex", ["-c", "model_provider=lms"], "gpt-oss-120b", [])

    def test_local_integrator_rejects_known_bad_marker(self) -> None:
        bad_output = (FIXTURES / "integrator_bad_missing_required_parameter.txt").read_text(encoding="utf-8")
        cfg = SimpleNamespace(use_cli_integrator_fallback=True, integrator_timeout=30)

        with (
            patch.object(router, "_profile_for_role", return_value=self.profile),
            patch.object(router, "_run_cli_codex", return_value=(0, bad_output)),
        ):
            result = router._run_cli_integrator(cfg, "/repo", "approved", local=True)

        self.assertIsNone(result)

    def test_local_integrator_accepts_nonempty_output(self) -> None:
        cfg = SimpleNamespace(use_cli_integrator_fallback=True, integrator_timeout=30)

        with (
            patch.object(router, "_profile_for_role", return_value=self.profile),
            patch.object(router, "_run_cli_codex", return_value=(0, "Integrated successfully.\n")),
        ):
            result = router._run_cli_integrator(cfg, "/repo", "approved", local=True)

        self.assertEqual(result, "Integrated successfully.")


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

