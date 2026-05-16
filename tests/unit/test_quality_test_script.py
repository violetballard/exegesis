from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class QualityTestScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        shutil.copy2(REPO_ROOT / "quality-test.sh", self.root / "quality-test.sh")
        (self.root / "quality-test.sh").chmod(0o755)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_quality_test(self) -> subprocess.CompletedProcess[str]:
        env = dict(**os.environ)
        # The control-plane planner sets QUAL_ROOT_DIR so repo-owned gate scripts
        # can run against lane worktrees. These script unit tests execute a
        # copied fixture and must not inherit that repo override, or the fixture
        # re-enters the full repo test suite recursively.
        env.pop("QUAL_ROOT_DIR", None)
        return subprocess.run(
            [str(self.root / "quality-test.sh")],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            env=env,
        )

    def test_runs_shell_tests_when_present(self) -> None:
        tests_dir = self.root / "tests"
        tests_dir.mkdir()
        (tests_dir / "smoke.sh").write_text("#!/usr/bin/env sh\necho shell smoke\n", encoding="utf-8")

        proc = self.run_quality_test()

        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("[test] tests/smoke.sh", proc.stdout)
        self.assertIn("shell smoke", proc.stdout)

    def test_falls_back_to_python_unittest_discovery(self) -> None:
        tests_dir = self.root / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_gate.py").write_text(
            "import unittest\n\n"
            "class GateTest(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n",
            encoding="utf-8",
        )

        proc = self.run_quality_test()

        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("[test] python unittest discovery", proc.stdout)
        self.assertIn("test_ok", proc.stdout)

    def test_discovers_nested_unit_python_tests(self) -> None:
        tests_dir = self.root / "tests" / "unit"
        tests_dir.mkdir(parents=True)
        (tests_dir / "test_nested_gate.py").write_text(
            "import unittest\n\n"
            "class NestedGateTest(unittest.TestCase):\n"
            "    def test_nested_ok(self):\n"
            "        self.assertEqual(1 + 1, 2)\n",
            encoding="utf-8",
        )

        proc = self.run_quality_test()

        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("[test] python unittest discovery", proc.stdout)
        self.assertIn("test_nested_ok", proc.stdout)

    def test_fails_when_no_tests_are_present(self) -> None:
        (self.root / "tests").mkdir()

        proc = self.run_quality_test()

        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("No test files found in tests/.", proc.stdout)


if __name__ == "__main__":
    sys.exit(unittest.main())
