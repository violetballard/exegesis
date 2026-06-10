from __future__ import annotations

import argparse
from collections.abc import Sequence
import os

from exegesis_textual.layout.shell import QualShellApp, reset_default_demo_project
from exegesis_textual.services.projects import is_release_mode


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Exegesis Textual shell.")
    parser.add_argument(
        "--reset-demo-project",
        action="store_true",
        help="Reset the default demo project and exit. Intended for server startup, not browser refresh.",
    )
    args = parser.parse_args(argv)
    if args.reset_demo_project:
        if is_release_mode():
            parser.error("--reset-demo-project is unavailable in release mode.")
        reset_default_demo_project()
        return 0

    # Codex shells often export NO_COLOR for command output. The browser shell is
    # visual UI, so keep Textual's web renderer in color even when launched from
    # that environment.
    os.environ.pop("NO_COLOR", None)
    os.environ.setdefault("COLORTERM", "truecolor")
    os.environ.setdefault("TERM", "xterm-256color")
    app = QualShellApp()
    result = app.run()
    if result == "restart":
        return 75
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
