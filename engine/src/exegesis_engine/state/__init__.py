"""Canonical persistence state models for the engine contract."""

from __future__ import annotations

__all__ = ["ContextBasket", "ContextSetRecord", "SessionState", "VaultState"]


def __getattr__(name: str):
    if name == "ContextBasket":
        from exegesis_engine.context import ContextBasket as value

        return value
    if name == "ContextSetRecord":
        from exegesis_engine.context import ContextSetRecord as value

        return value
    if name == "SessionState":
        from exegesis_engine.context import SessionState as value

        return value
    if name == "VaultState":
        from exegesis_engine.storage import VaultState as value

        return value
    raise AttributeError(name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
