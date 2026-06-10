from __future__ import annotations

import os

from exegesis_textual.desktop.launcher import main
from exegesis_textual.desktop.launcher import TERMINAL_CHILD_ENV


if __name__ == "__main__":
    if os.environ.get(TERMINAL_CHILD_ENV) == "1":
        from exegesis_textual.app.main import main as shell_main

        raise SystemExit(shell_main([]))
    raise SystemExit(main())
