from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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

    def test_scope_check_blocks_engine_work_on_console_shell_lane(self) -> None:
        proc = self._commit_on_branch(
            "codex/feat-console-shell",
            "engine/src/exegesis_engine/workflow/revise_service.py",
            "not allowed\n",
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("engine/src/exegesis_engine/workflow/revise_service.py", proc.stdout)


if __name__ == "__main__":
    unittest.main()
