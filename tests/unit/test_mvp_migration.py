from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import argparse
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from exegesis_engine.api.app_service import ExegesisAppService
from exegesis_engine.api.bootstrap import build_runtime as canonical_build_runtime
from exegesis_engine.api.cli import CLIArgs as CanonicalCLIArgs, parse_args as canonical_parse_args
from exegesis_engine.api.runtime_commands import run_bootstrap as canonical_run_bootstrap
from exegesis_engine.audit import AuditLog as CanonicalAuditLog
from exegesis_engine.config import AppConfig as CanonicalAppConfig
from exegesis_engine.context import ContextBasket as CanonicalContextBasket, ContextBasketStore as CanonicalContextBasketStore
from exegesis_engine.drafting import DraftingService as CanonicalDraftingService
from exegesis_engine.metrics import MetricsExporter as CanonicalMetricsExporter
from exegesis_engine.retrieval.search_service import RetrievalService as CanonicalRetrievalService
from exegesis_engine.storage import VaultService as CanonicalVaultService
from exegesis_shared.contracts.cards import A2UICapabilities as CanonicalA2UICapabilities
from packet_garden.tools.agents_coordinator import DirectRouterCtx, _should_run_cycle
from src.qual.audit import AuditLog as CompatAuditLog
from src.qual.config import AppConfig as CompatAppConfig
from src.qual.app import run_bootstrap as compat_run_bootstrap
from src.qual.bootstrap import build_runtime as compat_build_runtime
from src.qual.cli import CLIArgs as CompatCLIArgs, parse_args as compat_parse_args
from src.qual.context import ContextBasket as CompatContextBasket, ContextBasketStore as CompatContextBasketStore
from src.qual.drafting import DraftingService as CompatDraftingService
from src.qual.engine.service import EngineService as CompatEngineService
from src.qual.metrics import MetricsExporter as CompatMetricsExporter
from src.qual.retrieval.service import RetrievalService as CompatRetrievalService
from src.qual.storage import VaultService as CompatVaultService
from src.qual.ui.a2ui import A2UICapabilities as CompatA2UICapabilities

REPO_ROOT = Path(__file__).resolve().parents[2]


class CanonicalMigrationImportTests(unittest.TestCase):
    def test_compat_imports_forward_to_canonical_packages(self) -> None:
        from exegesis_engine.api.app_service import EngineService as CanonicalEngineService

        self.assertIs(CompatEngineService, CanonicalEngineService)
        self.assertIs(CompatRetrievalService, CanonicalRetrievalService)
        self.assertIs(CompatA2UICapabilities, CanonicalA2UICapabilities)
        self.assertIs(CompatCLIArgs, CanonicalCLIArgs)
        self.assertIs(compat_parse_args, canonical_parse_args)
        self.assertIs(compat_build_runtime, canonical_build_runtime)
        self.assertIs(compat_run_bootstrap, canonical_run_bootstrap)
        self.assertIs(CompatAuditLog, CanonicalAuditLog)
        self.assertIs(CompatAppConfig, CanonicalAppConfig)
        self.assertIs(CompatContextBasket, CanonicalContextBasket)
        self.assertIs(CompatContextBasketStore, CanonicalContextBasketStore)
        self.assertIs(CompatDraftingService, CanonicalDraftingService)
        self.assertIs(CompatMetricsExporter, CanonicalMetricsExporter)
        self.assertIs(CompatVaultService, CanonicalVaultService)


class ExegesisAppServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.project_root = Path(self._tmp.name)
        (self.project_root / "sessions").mkdir(parents=True, exist_ok=True)
        (self.project_root / "draft.md").write_text("hello world\n", encoding="utf-8")
        (self.project_root / "sessions" / "research.md").write_text("memo evidence\n", encoding="utf-8")
        self.service = ExegesisAppService()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_app_service_supports_project_search_basket_and_patch_flow(self) -> None:
        project = self.service.open_project(self.project_root)
        self.assertEqual(project.current_project_id_or_path, str(self.project_root))
        self.assertTrue(any(item.id == "draft.md" for item in project.project_items))
        self.assertTrue(any(item.id == "sessions/research.md" for item in project.sessions))

        result = self.service.search_project("hello")
        self.assertTrue(result.hits)

        document = self.service.open_document("draft.md")
        self.assertEqual(document.current_document_content, "hello world\n")
        self.service.add_basket_item("draft.md", item_type="document", label="Draft")
        plan = self.service.plan_from_basket()
        self.assertIn("Draft", plan.body)

        self.service.set_document_selection(start=6, end=11)
        patch = self.service.revise_selection(proposed_text="team")
        updated = self.service.apply_patch(patch.patch_id)
        self.assertEqual(updated.current_document_content, "hello team\n")

        saved = self.service.save_document()
        self.assertFalse(saved.dirty)
        self.assertEqual((self.project_root / "draft.md").read_text(encoding="utf-8"), "hello team\n")


class CliCompatibilityTests(unittest.TestCase):
    def test_src_main_entrypoint_still_runs_diff_preview(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                "src/main.py",
                "diff-preview",
                "--original",
                "alpha\n",
                "--proposed",
                "beta\n",
            ],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("--- original", proc.stdout)
        self.assertIn("+++ proposed", proc.stdout)


class ScopeCheckMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "scripts").mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / "scripts" / "common.sh", self.root / "scripts" / "common.sh")
        shutil.copy2(REPO_ROOT / "scripts" / "scope-check.sh", self.root / "scripts" / "scope-check.sh")
        (self.root / "scripts" / "scope-check.sh").chmod(0o755)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Codex Test"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "codex@example.com"], cwd=self.root, check=True)
        (self.root / "README.md").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "initial"], cwd=self.root, check=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _commit_on_branch(self, branch: str, relative_path: str, content: str) -> subprocess.CompletedProcess[str]:
        subprocess.run(["git", "checkout", "-qb", branch], cwd=self.root, check=True)
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", relative_path], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", f"update {relative_path}"], cwd=self.root, check=True)
        return subprocess.run(
            ["bash", "scripts/scope-check.sh"],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    def test_scope_check_allows_canonical_context_storage_paths(self) -> None:
        proc = self._commit_on_branch(
            "codex/feat-context-storage",
            "engine/src/exegesis_engine/state/models.py",
            "state models\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("scope-check: passed", proc.stdout)

    def test_scope_check_allows_console_shell_paths(self) -> None:
        proc = self._commit_on_branch(
            "codex/feat-console-shell",
            "client-textual/src/exegesis_textual/layout/shell.py",
            "shell layout\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("scope-check: passed", proc.stdout)

    def test_scope_check_allows_approved_shared_commands_tests(self) -> None:
        subprocess.run(["git", "checkout", "-qb", "codex/feat-commands"], cwd=self.root, check=True)
        path = self.root / "tests" / "unit" / "test_commands_catalog.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("commands catalog tests\n", encoding="utf-8")
        subprocess.run(["git", "add", "tests/unit/test_commands_catalog.py"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "update shared commands test"], cwd=self.root, check=True)

        proc = subprocess.run(
            ["bash", "scripts/scope-check.sh"],
            cwd=self.root,
            env={**os.environ, "SCOPE_ALLOW_SHARED": "1"},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("scope-check: passed", proc.stdout)

    def test_scope_check_allows_approved_shared_retrieval_tests(self) -> None:
        subprocess.run(["git", "checkout", "-qb", "codex/feat-retrieval-fts"], cwd=self.root, check=True)
        path = self.root / "tests" / "unit" / "test_unified_retrieval.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("unified retrieval tests\n", encoding="utf-8")
        subprocess.run(["git", "add", "tests/unit/test_unified_retrieval.py"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "update shared retrieval test"], cwd=self.root, check=True)

        proc = subprocess.run(
            ["bash", "scripts/scope-check.sh"],
            cwd=self.root,
            env={**os.environ, "SCOPE_ALLOW_SHARED": "1"},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("scope-check: passed", proc.stdout)

    def test_planner_runs_repo_scope_check_script_against_lane_worktree(self) -> None:
        from packet_garden.tools import planner as planner_mod

        with patch.object(planner_mod, "run", return_value=(0, "scope-check: passed")) as run_mock:
            rc, out = planner_mod.run_scope_check("/tmp/lane-worktree", env={"SCOPE_ALLOW_SHARED": "1"})

        self.assertEqual((rc, out), (0, "scope-check: passed"))
        run_mock.assert_called_once()
        self.assertIn(str(REPO_ROOT / "scripts" / "scope-check.sh"), run_mock.call_args.args[0])
        self.assertEqual(run_mock.call_args.kwargs["cwd"], str(REPO_ROOT))
        self.assertEqual(
            run_mock.call_args.kwargs["env"],
            {"SCOPE_ALLOW_SHARED": "1", "QUAL_ROOT_DIR": "/tmp/lane-worktree"},
        )
        self.assertEqual(run_mock.call_args.kwargs["timeout"], 900)

    def test_planner_runs_repo_managed_ci_steps_against_lane_worktree(self) -> None:
        from packet_garden.tools import planner as planner_mod

        calls: list[tuple[str, str, dict[str, str], int]] = []

        def fake_run(cmd: str, cwd: str, env: dict[str, str], timeout: int) -> tuple[int, str]:
            calls.append((cmd, cwd, env, timeout))
            return 0, f"ok:{cmd}"

        with patch.object(planner_mod, "run", side_effect=fake_run):
            rc, out = planner_mod.run_required_gate("make ci", "/tmp/lane-worktree", env={"SCOPE_ALLOW_SHARED": "1"})

        self.assertEqual(rc, 0)
        self.assertIn("ok:bash", out)
        self.assertEqual(len(calls), 7)
        self.assertEqual({call[1] for call in calls}, {str(REPO_ROOT)})
        self.assertTrue(all(call[2]["QUAL_ROOT_DIR"] == "/tmp/lane-worktree" for call in calls))
        self.assertTrue(any("scripts/setup.sh" in call[0] for call in calls))
        self.assertTrue(any("scripts/scope-check.sh" in call[0] for call in calls))
        self.assertTrue(any("quality-format.sh" in call[0] for call in calls))
        self.assertTrue(any("quality-lint.sh" in call[0] for call in calls))
        self.assertTrue(any("scripts/build.sh" in call[0] for call in calls))
        self.assertTrue(any("typecheck-test.sh" in call[0] for call in calls))
        self.assertTrue(any("quality-test.sh" in call[0] for call in calls))

    def test_planner_run_timeout_terminates_process_group(self) -> None:
        from packet_garden.tools import planner as planner_mod

        class FakeProc:
            pid = 4242
            returncode = None

            def __init__(self) -> None:
                self.calls = 0

            def communicate(self, timeout: int | None = None):
                self.calls += 1
                if self.calls == 1:
                    raise subprocess.TimeoutExpired(cmd="slow", timeout=timeout)
                return "partial output", None

        fake_proc = FakeProc()
        with (
            patch.object(planner_mod.subprocess, "Popen", return_value=fake_proc) as popen_mock,
            patch.object(planner_mod.os, "killpg") as killpg_mock,
        ):
            rc, out = planner_mod.run("slow", cwd=str(self.root), timeout=1)

        self.assertEqual(rc, 124)
        self.assertIn("partial output", out)
        self.assertIn("[TIMEOUT]", out)
        self.assertTrue(popen_mock.call_args_list[0].kwargs["start_new_session"])
        killpg_mock.assert_called_once_with(4242, planner_mod.signal.SIGTERM)

    def test_planner_list_git_remotes_returns_empty_without_remote(self) -> None:
        from packet_garden.tools import planner as planner_mod

        remotes = planner_mod.list_git_remotes(str(self.root))

        self.assertEqual(remotes, [])

    def test_planner_skips_fetch_when_no_remotes_exist(self) -> None:
        from packet_garden.tools import planner as planner_mod

        cfg = {
            "lanes": {
                "feat-commands": {
                    "enabled": True,
                    "branch": "codex/feat-commands",
                }
            }
        }
        planner_state = {"lanes": {}}

        with (
            patch.object(planner_mod, "load_json", side_effect=[cfg, planner_state]),
            patch.object(planner_mod, "list_git_remotes", return_value=[]),
            patch.object(planner_mod, "lane_has_pending_feature", return_value=True),
            patch.object(planner_mod, "ensure_lane_dirs"),
            patch.object(planner_mod, "run") as run_mock,
        ):
            planner_mod.main()

        self.assertFalse(run_mock.called)

    def test_planner_skips_gate_run_for_active_feature_lane(self) -> None:
        from packet_garden.tools import planner as planner_mod

        cfg = {
            "lanes": {
                "feat-context-storage": {
                    "enabled": True,
                    "branch": "codex/feat-context-storage",
                }
            }
        }
        planner_state = {"lanes": {}}
        coordinator_state = {
            "lane_refill": {
                "feat-context-storage": {
                    "feature_active": True,
                }
            }
        }

        with (
            patch.object(planner_mod, "load_json", side_effect=[cfg, planner_state]),
            patch.object(planner_mod, "load_coordinator_state", return_value=coordinator_state),
            patch.object(planner_mod, "list_git_remotes", return_value=[]),
            patch.object(planner_mod, "lane_has_pending_feature", return_value=False),
            patch.object(planner_mod, "ensure_lane_dirs"),
            patch.object(planner_mod, "run_scope_check") as scope_check,
            patch.object(planner_mod, "run_required_gate") as required_gate,
        ):
            planner_mod.main()

        scope_check.assert_not_called()
        required_gate.assert_not_called()

    def test_compute_changed_files_falls_back_to_branch_ref_diff_tree(self) -> None:
        from packet_garden.tools import planner as planner_mod

        calls: list[tuple[list[str], str, int]] = []

        def fake_require(args: list[str], cwd: str, timeout: int) -> str:
            calls.append((args, cwd, timeout))
            if args == ["merge-base", "codex/integrator", "codex/feat-context-storage"]:
                return "abc123\n"
            raise AssertionError(f"unexpected require args: {args}")

        def fake_run_git(args: list[str], cwd: str, timeout: int, **_: object):
            calls.append((args, cwd, timeout))
            if args == ["rev-list", "--reverse", "abc123..codex/feat-context-storage"]:
                return SimpleNamespace(returncode=0, stdout="def456\n")
            if args == ["diff-tree", "--no-commit-id", "--name-only", "-r", "def456"]:
                return SimpleNamespace(
                    returncode=0,
                    stdout="THREAD_PACKET.md\n.codex/lane_meta/feat-context-storage.json\n",
                )
            raise AssertionError(f"unexpected args: {args}")

        with (
            patch.object(planner_mod, "require_git_output", side_effect=fake_require),
            patch.object(planner_mod, "run_git", side_effect=fake_run_git),
        ):
            files = planner_mod.compute_changed_files(
                str(self.root),
                "codex/integrator",
                head_ref="codex/feat-context-storage",
            )

        self.assertEqual(
            files,
            ["THREAD_PACKET.md", ".codex/lane_meta/feat-context-storage.json"],
        )
        self.assertEqual(
            calls[0],
            (
                ["merge-base", "codex/integrator", "codex/feat-context-storage"],
                str(self.root),
                planner_mod.CHANGED_FILES_DIFF_TIMEOUT,
            ),
        )
        self.assertEqual(
            calls[1],
            (
                ["rev-list", "--reverse", "abc123..codex/feat-context-storage"],
                str(self.root),
                planner_mod.CHANGED_FILES_DIFF_TIMEOUT,
            ),
        )
        self.assertEqual(
            calls[2],
            (
                ["diff-tree", "--no-commit-id", "--name-only", "-r", "def456"],
                str(self.root),
                planner_mod.CHANGED_FILES_FALLBACK_TIMEOUT,
            ),
        )

    def test_scope_check_blocks_engine_work_on_console_shell_lane(self) -> None:
        proc = self._commit_on_branch(
            "codex/feat-console-shell",
            "engine/src/exegesis_engine/workflow/revise_service.py",
            "not allowed\n",
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("engine/src/exegesis_engine/workflow/revise_service.py", proc.stdout)


class CoordinatorDaemonBehaviorTests(unittest.TestCase):
    def test_daemon_mode_keeps_running_even_without_queue_changes(self) -> None:
        args = type("Args", (), {"daemon": True})()
        self.assertTrue(_should_run_cycle(args, "snapshot-a", "snapshot-a", 12, False))

    def test_once_mode_still_uses_snapshot_and_backlog_signals(self) -> None:
        args = type("Args", (), {"daemon": False})()
        self.assertTrue(_should_run_cycle(args, "snapshot-b", "snapshot-a", 4, False))
        self.assertTrue(_should_run_cycle(args, "snapshot-a", "snapshot-a", 0, False))
        self.assertTrue(_should_run_cycle(args, "snapshot-a", "snapshot-a", 4, True))
        self.assertFalse(_should_run_cycle(args, "snapshot-a", "snapshot-a", 4, False))

    def test_direct_router_bootstraps_integrator_thread_in_cloud_mode(self) -> None:
        from packet_garden.tools.agents_coordinator import _bootstrap_direct_integrator_thread

        calls: list[tuple[str, object]] = []

        class FakeRouterMod:
            STATE_FILE = Path("/tmp/router-state.json")

            @staticmethod
            def _runtime_mode(cfg: object, state: dict) -> str:
                return "cloud_primary"

            @staticmethod
            def _profile_for_role(cfg: object, role: str, *, local: bool = False) -> SimpleNamespace:
                return SimpleNamespace(model="gpt-5.1-codex")

            @staticmethod
            def save_json(path: Path, data: dict) -> None:
                calls.append(("save_json", data.copy()))

        class FakeIntegratorClient:
            def codex(self, **kwargs: object) -> tuple[str, str]:
                calls.append(("codex", kwargs))
                return "thread-123", "ready"

        state: dict = {}
        tid = _bootstrap_direct_integrator_thread(
            FakeRouterMod,
            object(),
            "/repo",
            state,
            FakeIntegratorClient(),
            "",
        )

        self.assertEqual(tid, "thread-123")
        self.assertEqual(state["integrator_thread_id"], "thread-123")
        self.assertTrue(any(call[0] == "codex" for call in calls))
        self.assertTrue(any(call[0] == "save_json" for call in calls))

    def test_direct_router_skips_integrator_thread_bootstrap_when_cli_integrator_preferred(self) -> None:
        from packet_garden.tools.agents_coordinator import _bootstrap_direct_integrator_thread

        class FakeRouterMod:
            STATE_FILE = Path("/tmp/router-state.json")

            @staticmethod
            def _runtime_mode(cfg: object, state: dict) -> str:
                return "cloud_primary"

            @staticmethod
            def _profile_for_role(cfg: object, role: str, *, local: bool = False) -> SimpleNamespace:
                return SimpleNamespace(model="gpt-5.1-codex")

            @staticmethod
            def save_json(path: Path, data: dict) -> None:
                raise AssertionError("save_json should not be called when CLI integrator is preferred")

        class FakeIntegratorClient:
            def codex(self, **kwargs: object) -> tuple[str, str]:
                raise AssertionError("codex should not be called when CLI integrator is preferred")

        state: dict = {}
        tid = _bootstrap_direct_integrator_thread(
            FakeRouterMod,
            SimpleNamespace(prefer_cli_integrator=True, integrator_timeout=30),
            "/repo",
            state,
            FakeIntegratorClient(),
            "",
        )

        self.assertEqual(tid, "")
        self.assertEqual(state, {})

    def test_init_direct_router_ctx_restores_cloud_before_building_clients(self) -> None:
        from packet_garden.tools.agents_coordinator import _init_direct_router_ctx

        calls: list[tuple[str, object, object]] = []

        def fake_profile_for_role(cfg: object, role: str, *, local: bool = False) -> SimpleNamespace:
            calls.append(("profile", role, local))
            return SimpleNamespace(model=f"{role}-{'local' if local else 'cloud'}")

        def fake_build_mcp_client(profile: SimpleNamespace, _approval: object) -> object:
            calls.append(("client", profile.model, None))
            return SimpleNamespace(close=lambda: None)

        fake_router = SimpleNamespace(
            STATE_FILE=Path("/tmp/router-state.json"),
            ApprovalPolicy=lambda *args: SimpleNamespace(args=args),
            load_cfg=lambda: SimpleNamespace(lanes={"feat-commands": {}}),
            load_json=lambda _path, _default: {"runtime_mode": "local_fallback", "integrator_thread_id": "thread-cloud"},
            save_json=lambda _path, _data: None,
            ensure_lane_dirs=lambda _lane: None,
            _maybe_restore_cloud=lambda _cfg, state, _cwd: {**state, "runtime_mode": "cloud_primary"},
            _runtime_mode=lambda _cfg, state: str(state.get("runtime_mode", "cloud_primary")),
            _profile_for_role=fake_profile_for_role,
            _build_mcp_client=fake_build_mcp_client,
        )

        with patch("packet_garden.tools.agents_coordinator._load_tool_module", return_value=fake_router):
            ctx = _init_direct_router_ctx()

        self.assertFalse(ctx.local_mode)
        self.assertIn(("profile", "reviewer", False), calls)
        self.assertIn(("profile", "integrator", False), calls)
        self.assertNotIn(("profile", "reviewer", True), calls)
        self.assertNotIn(("profile", "integrator", True), calls)

    def test_run_router_direct_once_rebuilds_clients_after_mode_restore(self) -> None:
        from packet_garden.tools.agents_coordinator import _run_router_direct_once

        close_calls: list[str] = []
        build_calls: list[str] = []

        class FakeClient:
            def __init__(self, name: str) -> None:
                self.name = name

            def close(self) -> None:
                close_calls.append(self.name)

        def fake_profile_for_role(cfg: object, role: str, *, local: bool = False) -> SimpleNamespace:
            suffix = "local" if local else "cloud"
            return SimpleNamespace(model=f"{role}-{suffix}")

        def fake_build_mcp_client(profile: SimpleNamespace, _approval: object) -> FakeClient:
            build_calls.append(profile.model)
            return FakeClient(profile.model)

        fake_router = SimpleNamespace(
            STATE_FILE=Path("/tmp/router-state.json"),
            ApprovalPolicy=lambda *args: SimpleNamespace(args=args),
            _maybe_restore_cloud=lambda _cfg, state, _cwd: {**state, "runtime_mode": "cloud_primary"},
            _runtime_mode=lambda _cfg, state: str(state.get("runtime_mode", "cloud_primary")),
            _profile_for_role=fake_profile_for_role,
            _build_mcp_client=fake_build_mcp_client,
            save_json=lambda _path, _data: None,
            process_once=lambda reviewer_client, integrator_client, _cfg, state, _cwd, reviewer_thread_ids, integrator_tid: (0, state, reviewer_thread_ids, integrator_tid),
            process_reviewer_backlog=lambda reviewer_client, _cfg, state, _cwd: (0, state),
            process_integrator_backlog=lambda integrator_client, _cfg, state, _cwd, integrator_tid: (0, state, integrator_tid),
        )

        ctx = DirectRouterCtx(
            router_mod=fake_router,
            cfg=SimpleNamespace(),
            state={"runtime_mode": "local_fallback", "integrator_thread_id": "thread-cloud"},
            repo_cwd="/repo",
            reviewer_client=FakeClient("reviewer-local"),
            integrator_client=FakeClient("integrator-local"),
            reviewer_thread_ids={},
            integrator_tid="thread-cloud",
            local_mode=True,
        )

        rc, out = _run_router_direct_once(ctx)

        self.assertEqual(rc, 0, out)
        self.assertFalse(ctx.local_mode)
        self.assertEqual(sorted(close_calls), ["integrator-local", "reviewer-local"])
        self.assertIn("reviewer-cloud", build_calls)
        self.assertIn("integrator-cloud", build_calls)

    def test_run_router_direct_falls_back_to_subprocess_when_profiles_are_cli_only(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        ctx = SimpleNamespace()
        with (
            patch.object(
                coordinator,
                "_run_router_direct_once",
                side_effect=coordinator.DirectRouterUnsupported("current runtime uses opencode"),
            ),
            patch.object(coordinator, "_run_router_subprocess", return_value=(0, "[router] queued local reviewer job\n", 1)) as subprocess_router,
        ):
            rc, out, attempts = coordinator._run_router_direct(ctx, retries=2)

        self.assertEqual(rc, 0)
        self.assertIn("queued local reviewer", out)
        self.assertEqual(attempts, 1)
        subprocess_router.assert_called_once_with(2)

    def test_launch_free_lanes_relaunches_idle_lane_without_active_feature_session(self) -> None:
        from packet_garden.tools.agents_coordinator import _launch_free_lanes

        commands: list[list[str]] = []

        def fake_run_cmd(cmd: list[str]) -> tuple[int, str]:
            commands.append(cmd)
            return 0, ""

        state_doc = {"lane_refill": {"feat-commands": {"queue_empty": True}}}
        with (
            patch("packet_garden.tools.agents_coordinator._enabled_lanes", return_value=["feat-commands"]),
            patch("packet_garden.tools.agents_coordinator._lane_queue_empty", return_value=True),
            patch("packet_garden.tools.agents_coordinator._lane_has_active_feature_session", return_value=False),
            patch("packet_garden.tools.agents_coordinator._cloud_feature_launch_slots", return_value=0),
            patch("packet_garden.tools.agents_coordinator._local_lms_feature_launch_slots", return_value=1),
            patch("packet_garden.tools.agents_coordinator._has_lane_backlog", return_value=False),
            patch("packet_garden.tools.agents_coordinator._has_router_priority_backlog", return_value=False),
            patch("packet_garden.tools.agents_coordinator.run_cmd", side_effect=fake_run_cmd),
        ):
            launched = _launch_free_lanes(state_doc)

        self.assertEqual(launched, ["feat-commands"])
        self.assertEqual(commands[0][-2:], ["--lanes", "feat-commands"])

    def test_launch_free_lanes_fills_local_before_cloud(self) -> None:
        from packet_garden.tools.agents_coordinator import _launch_free_lanes

        commands: list[list[str]] = []

        def fake_run_cmd(cmd: list[str]) -> tuple[int, str]:
            commands.append(cmd)
            return 0, ""

        lanes = ["feat-commands", "feat-retrieval-fts", "feat-a2ui-contract"]
        state_doc = {"lane_refill": {lane: {"queue_empty": True} for lane in lanes}}
        with (
            patch("packet_garden.tools.agents_coordinator._enabled_lanes", return_value=lanes),
            patch("packet_garden.tools.agents_coordinator._lane_queue_empty", return_value=True),
            patch("packet_garden.tools.agents_coordinator._lane_has_active_feature_session", return_value=False),
            patch("packet_garden.tools.agents_coordinator._cloud_feature_launch_slots", return_value=1),
            patch("packet_garden.tools.agents_coordinator._local_lms_feature_launch_slots", return_value=2),
            patch("packet_garden.tools.agents_coordinator._active_local_fixer_jobs", return_value=0),
            patch("packet_garden.tools.agents_coordinator._has_reviewer_notes_backlog", return_value=False),
            patch("packet_garden.tools.agents_coordinator._has_lane_backlog", return_value=False),
            patch("packet_garden.tools.agents_coordinator._has_router_priority_backlog", return_value=False),
            patch("packet_garden.tools.agents_coordinator.run_cmd", side_effect=fake_run_cmd),
        ):
            launched = _launch_free_lanes(state_doc)

        self.assertEqual(launched, lanes)
        self.assertIn("--provider", commands[0])
        self.assertEqual(commands[0][commands[0].index("--provider") + 1], "local")
        self.assertEqual(commands[0][-3:], ["--lanes", "feat-commands", "feat-retrieval-fts"])
        self.assertEqual(commands[1][commands[1].index("--provider") + 1], "cloud")
        self.assertEqual(commands[1][-2:], ["--lanes", "feat-a2ui-contract"])

    def test_launch_free_lanes_skips_idle_lane_with_active_feature_session(self) -> None:
        from packet_garden.tools.agents_coordinator import _launch_free_lanes

        state_doc = {"lane_refill": {"feat-commands": {"queue_empty": True}}}
        with (
            patch("packet_garden.tools.agents_coordinator._enabled_lanes", return_value=["feat-commands"]),
            patch("packet_garden.tools.agents_coordinator._lane_queue_empty", return_value=True),
            patch("packet_garden.tools.agents_coordinator._lane_has_active_feature_session", return_value=True),
            patch("packet_garden.tools.agents_coordinator.run_cmd") as run_cmd,
        ):
            launched = _launch_free_lanes(state_doc)

        self.assertEqual(launched, [])
        run_cmd.assert_not_called()

    def test_launch_free_lanes_throttles_repeat_relaunch_attempts(self) -> None:
        from packet_garden.tools.agents_coordinator import _launch_free_lanes

        state_doc = {
            "lane_refill": {
                "feat-commands": {
                    "queue_empty": True,
                    "last_launch_attempt_ts": time.time(),
                }
            }
        }
        with (
            patch("packet_garden.tools.agents_coordinator._enabled_lanes", return_value=["feat-commands"]),
            patch("packet_garden.tools.agents_coordinator._lane_queue_empty", return_value=True),
            patch("packet_garden.tools.agents_coordinator._lane_has_active_feature_session", return_value=False),
            patch("packet_garden.tools.agents_coordinator.run_cmd") as run_cmd,
        ):
            launched = _launch_free_lanes(state_doc)

        self.assertEqual(launched, [])
        run_cmd.assert_not_called()

    def test_lane_has_active_feature_session_handles_direct_exec_pid_state(self) -> None:
        from packet_garden.tools.agents_coordinator import _lane_has_active_feature_session

        self.assertFalse(
            _lane_has_active_feature_session(
                "feat-commands",
                feature_threads={
                    "feat-commands": {
                        "status": "direct_exec_running",
                        "pid": 0,
                    }
                },
            )
        )


class StatusStateTests(unittest.TestCase):
    def test_queue_empty_but_active_feature_session_is_not_reported_idle(self) -> None:
        from packet_garden.tools.status import _derive_lane_state

        state, note = _derive_lane_state([], [], [], "abc123", "abc123", feature_active=True)
        self.assertEqual(state, "feature_in_progress")
        self.assertIn("actively working", note)


class CoordinatorStateReconcileTests(unittest.TestCase):
    def test_reconcile_control_plane_state_prunes_dead_feature_and_router_jobs(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            completed_result = root / "done.result.json"
            completed_result.write_text(json.dumps({"status": "ok"}), encoding="utf-8")

            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-stale": {"status": "direct_exec_running", "pid": 4242},
                            "feat-live": {"status": "direct_exec_running", "pid": 1111},
                            "feat-managed": {"status": "managed_thread", "thread_id": "tid-1"},
                        }
                    }
                ),
                encoding="utf-8",
            )
            router_state.write_text(
                json.dumps(
                    {
                        "fixer_fallback_jobs": {
                            "feat-stale": {"pid": 4242, "log": "fixer.log"},
                            "feat-live": {"pid": 1111, "log": "fixer-live.log"},
                        },
                        "local_reviewer_jobs": {
                            "feat-stale": {"pid": 4242, "result_path": str(root / "missing.result.json")},
                        },
                        "local_integrator_jobs": {
                            "feat-done:packet": {"pid": 4242, "result_path": str(completed_result)},
                        },
                        "cloud_integrator_jobs": {
                            "feat-cloud:packet": {"pid": 4242, "result_path": str(root / "missing-cloud.result.json")},
                        },
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 1111),
            ):
                summary = coordinator._reconcile_control_plane_state({})

            self.assertEqual(summary["feature_runner_removed"], ["feat-stale"])
            self.assertEqual(summary["router_removed"]["fixer_fallback_jobs"], ["feat-stale"])
            self.assertEqual(summary["router_removed"]["local_reviewer_jobs"], ["feat-stale"])
            self.assertEqual(summary["router_removed"]["cloud_integrator_jobs"], ["feat-cloud:packet"])

            feature_doc = json.loads(feature_state.read_text(encoding="utf-8"))
            router_doc = json.loads(router_state.read_text(encoding="utf-8"))

            self.assertNotIn("feat-stale", feature_doc["lanes"])
            self.assertIn("feat-live", feature_doc["lanes"])
            self.assertIn("feat-managed", feature_doc["lanes"])

            self.assertNotIn("feat-stale", router_doc["fixer_fallback_jobs"])
            self.assertIn("feat-live", router_doc["fixer_fallback_jobs"])
            self.assertNotIn("feat-stale", router_doc["local_reviewer_jobs"])
            self.assertIn("feat-done:packet", router_doc["local_integrator_jobs"])
            self.assertNotIn("feat-cloud:packet", router_doc["cloud_integrator_jobs"])

    def test_run_cycle_reloads_cleaned_router_state_before_direct_router(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        router_state = {"runtime_mode": "local_fallback", "fixer_fallback_jobs": {}}
        fake_router_mod = SimpleNamespace(
            STATE_FILE=Path("/tmp/router_state.json"),
            load_json=lambda path, default: dict(router_state),
        )
        ctx = DirectRouterCtx(
            router_mod=fake_router_mod,
            cfg=SimpleNamespace(),
            state={"fixer_fallback_jobs": {"feat-stale": {"pid": 4242}}},
            repo_cwd="/repo",
            reviewer_client=SimpleNamespace(),
            integrator_client=SimpleNamespace(),
            reviewer_thread_ids={},
            integrator_tid="",
            local_mode=False,
        )
        args = argparse.Namespace(execution_mode="direct", planner_retries=0, router_retries=0)

        with (
            patch.object(coordinator, "_reconcile_control_plane_state", return_value={"feature_runner_removed": [], "router_removed": {"fixer_fallback_jobs": ["feat-stale"]}}),
            patch.object(coordinator, "_run_planner_direct", return_value=(0, "", 1)),
            patch.object(coordinator, "_run_router_direct", return_value=(0, "", 1)),
            patch.object(coordinator, "_launch_free_lanes", return_value=[]),
        ):
            coordinator._run_cycle(args, ctx, {})

        self.assertEqual(ctx.state, router_state)


class RouterReviewerBootstrapTests(unittest.TestCase):
    def test_offline_reviewer_fallback_never_approves_without_live_review(self) -> None:
        from packet_garden.tools import router

        packet = "\n".join(
            [
                "## Tasks completed",
                "1. Did the thing.",
                "## Files changed",
                "- src/qual/retrieval/service.py",
                "## Commands run and outcomes",
                "- `./quality-format.sh --check`: PASS",
                "- `./quality-lint.sh`: PASS",
                "- `./quality-test.sh`: PASS",
                "- `./typecheck-test.sh`: PASS",
                "- `make ci`: PASS",
                "## Risks / blockers",
                "- Blockers: none",
            ]
        )

        result = router._offline_reviewer_fallback(packet, "timed out after 180.0s")

        self.assertIn("Verdict: `CHANGES_REQUESTED`", result)
        self.assertIn("live reviewer", result)
        self.assertNotIn("Verdict: `APPROVED`", result)

    def test_offline_reviewer_fallback_note_is_not_fixer_work(self) -> None:
        from packet_garden.tools import router

        note = router._offline_reviewer_fallback("feature packet", "timed out after 600.0s")

        self.assertTrue(router._requires_live_reviewer_rerun(note))

    def test_reviewer_backlog_restores_archived_packet_for_fallback_note(self) -> None:
        from packet_garden.tools import router

        with tempfile.TemporaryDirectory() as tmp:
            lane_dir = Path(tmp)
            sha = "040ef749ba4a001da8642a134f41c8ab626c4f3d"
            archived = lane_dir / "archive" / f"F__codex-feat-retrieval-fts__{sha}__20260513T172457Z.md"
            archived.parent.mkdir(parents=True, exist_ok=True)
            archived.write_text("Feature packet body\n", encoding="utf-8")
            note = lane_dir / "inbox" / "reviewer" / f"R__CHANGES__codex-feat-retrieval-fts__{sha}__20260513T172457Z.md"
            note.parent.mkdir(parents=True, exist_ok=True)
            note.write_text(
                router._offline_reviewer_fallback("Feature packet body\n", "bad local cli marker"),
                encoding="utf-8",
            )
            cfg = SimpleNamespace(
                inline_fixer=True,
                kick_fixers_on_reviewer_backlog=True,
                max_local_fixer_kicks_per_run=1,
                max_cloud_fixer_kicks_per_run=1,
                max_local_fixer_jobs=1,
                max_cloud_fixer_jobs=1,
                lanes={"feat-retrieval-fts": {"branch": "codex/feat-retrieval-fts"}},
            )

            with (
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "_local_lms_slot_available", return_value=True),
                patch.object(router, "run_fixer") as run_fixer,
            ):
                kicked, _state = router.process_reviewer_backlog(object(), cfg, {}, "/repo")

            restored = list((lane_dir / "inbox" / "feature").glob(f"F__codex-feat-retrieval-fts__{sha}__*.md"))

        self.assertEqual(kicked, 0)
        self.assertEqual(len(restored), 1)
        self.assertFalse(note.exists())
        run_fixer.assert_not_called()

    def test_local_reviewer_failure_keeps_packet_pending(self) -> None:
        from packet_garden.tools import router

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result_path = root / "review.result.json"
            output_path = root / "review.out.log"
            result_path.write_text('{"status": "error", "rc": 1, "error": "timed out"}', encoding="utf-8")
            output_path.write_text("", encoding="utf-8")
            pkt = root / "F__codex-feat-retrieval-fts__abc1234__20260508T000000Z.md"
            pkt.write_text("Feature packet", encoding="utf-8")
            cfg = SimpleNamespace(auto_switch_to_local_on_quota=True)
            state = {
                "runtime_mode": "local_fallback",
                "local_reviewer_jobs": {
                    "feat-retrieval-fts": {
                        "packet_name": pkt.name,
                        "pid": 999999,
                        "result_path": str(result_path),
                        "output_path": str(output_path),
                    }
                },
            }

            ready, reviewer_text, new_state = router._prepare_cli_reviewer_result(
                cfg,
                state,
                "/repo",
                "feat-retrieval-fts",
                pkt,
                "Feature packet",
                local=True,
            )

        self.assertFalse(ready)
        self.assertEqual(reviewer_text, "")
        self.assertEqual(new_state["local_reviewer_jobs"], {})

    def test_process_once_prefers_cli_reviewer_in_cloud_mode(self) -> None:
        from packet_garden.tools import router

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

            with (
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "list_new", return_value=[pkt]),
                patch.object(router, "load_json", return_value={}),
                patch.object(router, "save_json"),
                patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, cwd: state),
                patch.object(router, "_runtime_mode", return_value="cloud_primary"),
                patch.object(router, "_apply_quota_text_safeguard", side_effect=lambda cfg, state, text, reason: state),
                patch.object(router, "archive_reviewer_notes"),
                patch.object(router, "clear_stale_integrator_handoffs", return_value=0),
                patch.object(router, "archive"),
                patch.object(router, "_ensure_lane_reviewer_thread") as ensure_thread,
                patch.object(router, "_run_cli_reviewer", return_value="Verdict: `CHANGES_REQUESTED`\n\nPlease revise.\n"),
            ):
                processed, _state, _reviewer_threads, _integrator_tid = router.process_once(
                    SimpleNamespace(),
                    SimpleNamespace(),
                    cfg,
                    {},
                    "/repo",
                    {},
                    "",
                )

        self.assertEqual(processed, 1)
        ensure_thread.assert_not_called()

    def test_process_once_cli_reviewer_timeout_does_not_flip_to_local_fallback(self) -> None:
        from packet_garden.tools import router

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
            state = {"runtime_mode": "cloud_primary"}

            with (
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "list_new", return_value=[pkt]),
                patch.object(router, "load_json", return_value={}),
                patch.object(router, "save_json"),
                patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, cwd: state),
                patch.object(router, "_runtime_mode", return_value="cloud_primary"),
                patch.object(router, "_apply_quota_text_safeguard", side_effect=lambda cfg, state, text, reason: state),
                patch.object(router, "archive_reviewer_notes"),
                patch.object(router, "clear_stale_integrator_handoffs", return_value=0),
                patch.object(router, "archive"),
                patch.object(router, "_ensure_lane_reviewer_thread") as ensure_thread,
                patch.object(router, "_switch_to_local_fallback") as switch_to_local_fallback,
                patch.object(router, "_run_cli_reviewer", return_value=None),
                patch.object(
                    router,
                    "_offline_reviewer_fallback",
                    return_value="Verdict: `CHANGES_REQUESTED`\n\nRecovery review.\n",
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
        self.assertEqual(new_state["runtime_mode"], "cloud_primary")
        ensure_thread.assert_not_called()
        switch_to_local_fallback.assert_not_called()

    def test_process_once_passes_local_flag_when_bootstrapping_reviewer_thread(self) -> None:
        from packet_garden.tools import router

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
                prefer_cli_reviewer=False,
                prefer_cli_integrator=True,
            )

            calls: list[bool] = []

            class FakeReviewerClient:
                def codex_reply(self, tid: str, prompt: str, timeout: float) -> tuple[str, str]:
                    return tid, "Verdict: `CHANGES_REQUESTED`\n\nPlease revise.\n"

            with (
                patch.object(router, "ensure_lane_dirs", return_value=lane_dir),
                patch.object(router, "list_new", return_value=[pkt]),
                patch.object(router, "load_json", return_value={}),
                patch.object(router, "save_json"),
                patch.object(router, "_maybe_restore_cloud", side_effect=lambda cfg, state, cwd: state),
                patch.object(router, "_runtime_mode", return_value="cloud_primary"),
                patch.object(router, "_apply_quota_text_safeguard", side_effect=lambda cfg, state, text, reason: state),
                patch.object(router, "archive_reviewer_notes"),
                patch.object(router, "clear_stale_integrator_handoffs", return_value=0),
                patch.object(router, "archive"),
                patch.object(
                    router,
                    "_ensure_lane_reviewer_thread",
                    side_effect=lambda reviewer_client, cfg, repo_cwd, lane, reviewer_thread_ids, *, local: calls.append(local) or "reviewer-thread",
                ),
            ):
                processed, _state, _reviewer_threads, _integrator_tid = router.process_once(
                    FakeReviewerClient(),
                    SimpleNamespace(),
                    cfg,
                    {},
                    "/repo",
                    {},
                    "",
                )

        self.assertEqual(processed, 1)
        self.assertEqual(calls, [False])


class CloudDirectExecLaunchTests(unittest.TestCase):
    def test_runtime_launch_config_prefers_cloud_direct_exec_by_default(self) -> None:
        from packet_garden.tools.launch_feature_lanes import runtime_launch_config

        cfg = {
            "runtime_mode_default": "cloud_primary",
            "role_profiles": {},
            "profiles": {},
            "prefer_direct_exec_feature_cloud": True,
            "codex_cmd": "codex",
            "model": "gpt-5.4-mini",
            "fallback_codex_cmd": "codex",
            "fallback_codex_args": ["-c", "model_provider=lms"],
            "fallback_model": "gpt-oss-20b",
        }
        state = {"runtime_mode": "cloud_primary"}

        with (
            patch("packet_garden.tools.launch_feature_lanes.load_json", side_effect=[cfg, state]),
        ):
            launch_cfg = runtime_launch_config()

        self.assertTrue(launch_cfg["prefer_direct_exec_cloud"])

    def test_launch_one_lane_uses_cloud_direct_exec_by_default(self) -> None:
        from packet_garden.tools.launch_feature_lanes import _launch_one_lane

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prompts_dir = tmp_path / "prompts"
            logs_dir = tmp_path / "logs"
            prompts_dir.mkdir()
            logs_dir.mkdir()
            workdir = str(tmp_path / "worktree")
            Path(workdir).mkdir()
            feature_state = {"lanes": {}}
            launch_cfg = {
                "mode": "cloud_primary",
                "profile_name": "worker_cloud",
                "cmd": "codex",
                "cmd_args": [],
                "model": "gpt-5.4-mini",
                "model_args": [],
                "prefer_direct_exec_cloud": True,
                "launch_timeout_seconds": 300,
                "disable_local_fallback_on_cloud_timeout": True,
                "local_profile_name": "worker_local",
                "local_profile": {
                    "cmd": "codex",
                    "cmd_args": ["-c", "model_provider=lms"],
                    "model": "gpt-oss-20b",
                    "model_args": [],
                },
            }
            args = argparse.Namespace(restart_existing=False, dry_run=False)

            with (
                patch("packet_garden.tools.launch_feature_lanes.build_prompt", return_value="prompt"),
                patch("packet_garden.tools.launch_feature_lanes._spawn_direct_exec", return_value=4242),
            ):
                result = _launch_one_lane(
                    "feat-commands",
                    args=args,
                    launch_cfg=launch_cfg,
                    worktrees={"refs/heads/codex/feat-commands": workdir},
                    prompts_dir=prompts_dir,
                    logs_dir=logs_dir,
                    feature_state=feature_state,
                )

        self.assertEqual(result["status"], "direct_exec_running")
        self.assertEqual(result["mode"], "cloud_primary")
        self.assertEqual(result["pid"], 4242)

    def test_launch_one_lane_skips_missing_kickoff_packet(self) -> None:
        from packet_garden.tools.launch_feature_lanes import _launch_one_lane

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prompts_dir = tmp_path / "prompts"
            logs_dir = tmp_path / "logs"
            prompts_dir.mkdir()
            logs_dir.mkdir()
            workdir = str(tmp_path / "worktree")
            Path(workdir).mkdir()
            launch_cfg = {
                "branch": "codex/feat-retrieval-fts",
                "mode": "local_fallback",
                "profile_name": "worker_local",
            }
            args = argparse.Namespace(restart_existing=False, dry_run=False)

            with patch("packet_garden.tools.launch_feature_lanes.build_prompt", side_effect=FileNotFoundError("missing")):
                result = _launch_one_lane(
                    "feat-retrieval-fts",
                    args=args,
                    launch_cfg=launch_cfg,
                    worktrees={"refs/heads/codex/feat-retrieval-fts": workdir},
                    prompts_dir=prompts_dir,
                    logs_dir=logs_dir,
                    feature_state={"lanes": {}},
                )

        self.assertEqual(result["status"], "skipped")
        self.assertIn("missing kickoff packet", result["reason"])


if __name__ == "__main__":
    unittest.main()
