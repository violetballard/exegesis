from __future__ import annotations

import time
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from codex_packet_handoff.tools.router import (
    RouterConfig,
    _apply_quota_text_safeguard,
    _integration_dependency_blockers,
    _has_real_quota_signal,
    list_new,
)


def _router_cfg() -> RouterConfig:
    return RouterConfig(
        model="gpt-5.1-codex",
        codex_cmd="codex",
        fallback_model="gpt-oss-20b",
        fallback_codex_cmd="codex",
        fallback_codex_args=["--oss", "--local-provider", "lmstudio"],
        fallback_model_args=[],
        runtime_mode_default="cloud_primary",
        auto_switch_to_local_on_quota=True,
        auto_probe_cloud_recovery=True,
        cloud_probe_cooldown_seconds=1800,
        cloud_probe_timeout_seconds=30,
        reviewer_timeout=180,
        integrator_timeout=900,
        max_packets_per_run=5,
        inline_fixer=True,
        kick_fixers_on_reviewer_backlog=True,
        fixer_kick_timeout_seconds=8,
        reviewer_fixer_retry_cooldown_seconds=120,
        fixer_quota_retry_cooldown_seconds=3600,
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
        lanes={},
    )


class RouterQuotaFallbackTests(unittest.TestCase):
    def test_list_new_ignores_companion_shared_packets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            feature_dir = Path(tmpdir) / "inbox" / "feature"
            feature_dir.mkdir(parents=True)
            shared = feature_dir / "F__codex-feat-commands__abc1234__20260516T000000Z.shared.md"
            main = feature_dir / "F__codex-feat-commands__abc1234__20260516T000000Z.md"
            shared.write_text("shared companion")
            main.write_text("main feature packet")

            self.assertEqual([path.name for path in list_new(Path(tmpdir), None)], [main.name])

    def test_integration_dependency_blockers_hold_later_engine_lanes(self) -> None:
        cfg = _router_cfg()
        cfg.lanes = {
            "feat-context-storage": {"branch": "codex/feat-context-storage", "enabled": True},
            "feat-commands": {"branch": "codex/feat-commands", "enabled": True},
        }

        def merged(_repo_cwd: str, branch: str) -> bool:
            return branch == "codex/feat-commands"

        with mock.patch("codex_packet_handoff.tools.router._branch_merged_to_head", side_effect=merged):
            blockers = _integration_dependency_blockers(cfg, "/repo", "feat-commands")

        self.assertEqual(blockers, ["feat-context-storage"])

    def test_code_like_quota_text_does_not_count_as_real_quota_signal(self) -> None:
        text = '\n'.join(
            [
                'diff --git a/codex_packet_handoff/tools/router.py b/codex_packet_handoff/tools/router.py',
                '+ REVIEWER_QUOTA_RE = re.compile(r"usage limit|quota exceeded|rate limit|too many requests|try again at", re.IGNORECASE)',
                '+ reason="fixer log quota text on lane feat-engine-runs"',
            ]
        )

        self.assertFalse(_has_real_quota_signal(text))

    def test_retry_limit_wrapper_does_not_flip_runtime_mode(self) -> None:
        cfg = _router_cfg()
        state = {"runtime_mode": "cloud_primary"}

        updated = _apply_quota_text_safeguard(
            cfg,
            state,
            "ERROR: exceeded retry limit, last status: 429 Too Many Requests, request id: abc123",
            reason="fixer log quota text on lane feat-commands",
            default_seconds=300,
        )

        self.assertIs(updated, state)
        self.assertEqual(updated["runtime_mode"], "cloud_primary")
        self.assertNotIn("last_quota_reason", updated)
        self.assertNotIn("cloud_retry_at", updated)

    def test_real_quota_text_still_switches_to_local_fallback(self) -> None:
        cfg = _router_cfg()
        state = {"runtime_mode": "cloud_primary"}

        updated = _apply_quota_text_safeguard(
            cfg,
            state,
            "You've hit your usage limit. Try again at Mar 21, 2026 4:10 PM.",
            reason="fixer log quota text on lane feat-commands",
            default_seconds=300,
        )

        self.assertEqual(updated["runtime_mode"], "local_fallback")
        self.assertEqual(updated["last_quota_reason"], "fixer log quota text on lane feat-commands")
        self.assertGreater(updated["cloud_retry_at"], time.time())

    def test_real_quota_text_marks_cloud_unavailable_in_hybrid_mode(self) -> None:
        cfg = _router_cfg()
        cfg.runtime_mode_default = "hybrid"
        state = {"runtime_mode": "hybrid", "cloud_available": True}

        updated = _apply_quota_text_safeguard(
            cfg,
            state,
            "You've hit your usage limit. Try again at Mar 21, 2026 4:10 PM.",
            reason="reviewer quota/rate-limit response",
            default_seconds=300,
        )

        self.assertEqual(updated["runtime_mode"], "hybrid")
        self.assertFalse(updated["cloud_available"])
        self.assertEqual(updated["last_quota_reason"], "reviewer quota/rate-limit response")
        self.assertGreater(updated["cloud_retry_at"], time.time())

    def test_code_like_quota_text_does_not_flip_runtime_mode(self) -> None:
        cfg = _router_cfg()
        state = {"runtime_mode": "cloud_primary"}

        updated = _apply_quota_text_safeguard(
            cfg,
            state,
            '\n'.join(
                [
                    'diff --git a/codex_packet_handoff/tools/router.py b/codex_packet_handoff/tools/router.py',
                    '+ FIXER_QUOTA_RE = REVIEWER_QUOTA_RE',
                    '+ reason="fixer log quota text on lane feat-engine-runs"',
                    '+ REVIEWER_QUOTA_RE = re.compile(r"usage limit|quota exceeded|rate limit|too many requests|try again at", re.IGNORECASE)',
                ]
            ),
            reason="fixer log quota text on lane feat-engine-runs",
            default_seconds=300,
        )

        self.assertIs(updated, state)
        self.assertEqual(updated["runtime_mode"], "cloud_primary")
        self.assertNotIn("last_quota_reason", updated)
        self.assertNotIn("cloud_retry_at", updated)


if __name__ == "__main__":
    unittest.main()
