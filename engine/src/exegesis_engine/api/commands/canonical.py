from __future__ import annotations

import re

from exegesis_engine.api.commands.catalog import canonical_command as _canonical_command


def canonical_command(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    if "\x00" in name:
        raise ValueError("name cannot contain null bytes")
    if not name.strip():
        raise ValueError("name cannot be empty or whitespace only")
    stripped = name.strip()
    for word in re.split(r"[\-_ ]+", stripped):
        if len(word) > 50:
            raise ValueError("individual words in name cannot exceed 50 characters")
    return _canonical_command(name)
