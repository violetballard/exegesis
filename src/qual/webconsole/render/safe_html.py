from __future__ import annotations

from html import escape
from typing import Any


def escape_text(value: Any) -> str:
    """Escape user/model-provided values for HTML text nodes and attributes."""
    return escape(str(value), quote=True)


def json_compact(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def json_pretty(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True)
