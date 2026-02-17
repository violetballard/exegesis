from __future__ import annotations

from src.qual.bootstrap import build_runtime
from src.qual.ui.shell import ShellUI


def run(*, project_name: str | None = None) -> int:
    runtime = build_runtime(project_name=project_name)
    ui = ShellUI()
    print(ui.render_startup(runtime))
    return 0
