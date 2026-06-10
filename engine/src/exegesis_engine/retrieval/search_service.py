"""Compatibility exports for the canonical retrieval package."""

from importlib import import_module as _import_module

_canonical = _import_module("exegesis_engine.retrieval")

for _name in getattr(_canonical, "__all__", ()):  # mirror exact package objects
    globals()[_name] = getattr(_canonical, _name)

__all__ = list(getattr(_canonical, "__all__", ()))
