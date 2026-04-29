from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from codex_packet_handoff.tools import local_exec_sweeper


class LocalExecSweeperTests(unittest.TestCase):
    def test_find_orphaned_repo_local_exec_pids_filters_by_repo_prompt_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / ".codex/feature_runner/prompts").mkdir(parents=True, exist_ok=True)
            owned_prompt = repo_root / ".codex/feature_runner/prompts" / "lane.prompt.md"
            owned_prompt.write_text("prompt", encoding="utf-8")
            foreign_prompt = Path(tmp) / "foreign.prompt.md"
            foreign_prompt.write_text("prompt", encoding="utf-8")
            ps_output = "\n".join(
                [
                    f"101 /Applications/Codex.app/Contents/Resources/codex --oss --local-provider lmstudio exec --skip-git-repo-check -m gpt-oss-120b -s workspace-write Read and follow the exact instructions in {owned_prompt}. Treat that file as the full user prompt and obey it completely.",
                    "202 /Applications/Codex.app/Contents/Resources/codex --oss --local-provider lmstudio exec --skip-git-repo-check -m gpt-oss-20b -s workspace-write -",
                    "303 /Applications/Codex.app/Contents/Resources/codex exec hello",
                ]
            )

            def fake_run(args, **kwargs):
                if args[:2] == ["ps", "-axo"]:
                    return mock.Mock(returncode=0, stdout=ps_output)
                if args[:3] == ["lsof", "-a", "-p"] and args[3] == "101":
                    return mock.Mock(returncode=0, stdout=f"p101\nf0\nn{owned_prompt}\n")
                if args[:3] == ["lsof", "-a", "-p"] and args[3] == "202":
                    return mock.Mock(returncode=0, stdout=f"p202\nf0\nn{foreign_prompt}\n")
                return mock.Mock(returncode=1, stdout="")

            with mock.patch.object(local_exec_sweeper.subprocess, "run", side_effect=fake_run):
                orphaned = local_exec_sweeper.find_orphaned_repo_local_exec_pids(repo_root, tracked_pids=[303])

        self.assertEqual(orphaned, [101])


if __name__ == "__main__":
    unittest.main()
