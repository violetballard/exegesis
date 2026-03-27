from __future__ import annotations

from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
_canonical_path = Path(__file__).resolve().parent.parent / "engine" / "src" / "exegesis_engine"
if _canonical_path.is_dir():
    __path__.append(str(_canonical_path))
