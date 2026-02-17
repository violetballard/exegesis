from __future__ import annotations

from src.qual.bootstrap import build_runtime
from src.qual.commands.diff_preview import DiffPreviewInput, run_diff_preview
from src.qual.ui.shell import ShellUI


def run_bootstrap(*, project_name: str | None = None) -> int:
    runtime = build_runtime(project_name=project_name)
    ui = ShellUI()
    print(ui.render_startup(runtime))
    return 0


def run_diff_preview_command(*, original: str | None, proposed: str | None) -> int:
    before = original if original is not None else "The first draft paragraph.\n"
    after = proposed if proposed is not None else "The revised draft paragraph with evidence.\n"
    print(run_diff_preview(DiffPreviewInput(original=before, proposed=after)))
    return 0
