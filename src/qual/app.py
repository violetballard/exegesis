from __future__ import annotations

from src.qual.bootstrap import build_runtime
from src.qual.cli import CLIArgs
from src.qual.commands.diff_preview import DiffPreviewInput, run_diff_preview
from src.qual.ui.shell import ShellUI


def _run_bootstrap(*, project_name: str | None = None) -> int:
    runtime = build_runtime(project_name=project_name)
    ui = ShellUI()
    print(ui.render_startup(runtime))
    return 0


def _run_diff_preview(*, original: str | None, proposed: str | None) -> int:
    before = original if original is not None else "The first draft paragraph.\n"
    after = proposed if proposed is not None else "The revised draft paragraph with evidence.\n"
    print(run_diff_preview(DiffPreviewInput(original=before, proposed=after)))
    return 0


def run(cli: CLIArgs) -> int:
    if cli.command == "diff-preview":
        return _run_diff_preview(original=cli.original, proposed=cli.proposed)
    return _run_bootstrap(project_name=cli.project)
