from __future__ import annotations

__all__ = [
    "ContextBasket",
    "ContextBasketStore",
    "ContextSetRecord",
    "ContextSetStore",
    "ProjectItem",
    "ProjectStore",
    "SessionState",
    "SessionStore",
    "clear_corrupt_files",
    "remove_all_corrupt_files",
    "validate_and_quarantine",
    "purge_corrupt_state",
    "list_corrupt_files",
    "is_clean_state",
    "get_corrupt_file_count",
    "VaultService",
    "VaultState",
    "validate_project_name",
]


def __getattr__(name: str):
    if name in {
        "ContextBasket",
        "ContextBasketStore",
        "clear_corrupt_files",
        "remove_all_corrupt_files",
        "validate_and_quarantine",
        "purge_corrupt_state",
        "list_corrupt_files",
        "is_clean_state",
        "get_corrupt_file_count",
    }:
        from exegesis_engine import context as engine_context

        return getattr(engine_context, name)
    if name == "ProjectItem":
        from .project_store import ProjectItem as value

        return value
    if name == "ProjectStore":
        from .project_store import ProjectStore as value

        return value
    if name == "VaultService":
        from .vault import VaultService as value

        return value
    if name == "VaultState":
        from .vault import VaultState as value

        return value
    if name == "validate_project_name":
        from .vault import validate_project_name as value

        return value
    if name == "ContextSetRecord":
        from .set_store import ContextSetRecord as value

        return value
    if name == "ContextSetStore":
        from .set_store import ContextSetStore as value

        return value
    if name == "SessionState":
        from .session import SessionState as value

        return value
    if name == "SessionStore":
        from .session import SessionStore as value

        return value
    raise AttributeError(name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
