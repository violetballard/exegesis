from __future__ import annotations

from pathlib import Path
import sys

_SHARED_SRC = Path(__file__).resolve().parents[4] / "shared" / "src"
if str(_SHARED_SRC) not in sys.path:
    sys.path.insert(0, str(_SHARED_SRC))

from exegesis_shared.contracts.a2ui import *  # noqa: F403
from exegesis_shared.contracts.a2ui import __all__
