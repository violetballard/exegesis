from __future__ import annotations


def canonical_command(name: str) -> str:
    aliases = {
        "diff": "diff-preview",
    }
    return aliases.get(name, name)
