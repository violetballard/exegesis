from __future__ import annotations

__all__ = [
    "ContextBasket",
    "VaultService",
    "VaultState",
    "validate_project_name",
    "ProjectItem",
    "ProjectStore",
    "ContextBasketStore",
    "ContextSetRecord",
    "ContextSetStore",
    "SessionState",
    "SessionStore",
    "clear_corrupt_files",
    "remove_all_corrupt_files",
    "validate_and_quarantine",
    "purge_corrupt_state",
    "list_corrupt_files",
    "is_clean_state",
    "get_corrupt_file_count",
]


def __getattr__(name: str):
    if name == "ContextBasket":
        from .context import ContextBasket as value

        return value
    if name == "ContextBasketStore":
        from .context import ContextBasketStore as value

        return value
    if name == "ContextSetRecord":
        from .context import ContextSetRecord as value

        return value
    if name == "ContextSetStore":
        from .context import ContextSetStore as value

        return value
    if name == "SessionState":
        from .context import SessionState as value

        return value
    if name == "SessionStore":
        from .context import SessionStore as value

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
    if name == "ProjectItem":
        from .project_store import ProjectItem as value

        return value
    if name == "ProjectStore":
        from .project_store import ProjectStore as value

        return value
    if name == "clear_corrupt_files":
        from .context import clear_corrupt_files as value

        return value
    if name == "remove_all_corrupt_files":
        from .context import remove_all_corrupt_files as value

        return value
    if name == "validate_and_quarantine":
        from .context import validate_and_quarantine as value

        return value
    if name == "purge_corrupt_state":
        from .context import purge_corrupt_state as value

        return value
    if name == "list_corrupt_files":
        from .context import list_corrupt_files as value

        return value
    if name == "is_clean_state":
        from .context import is_clean_state as value

        return value
    if name == "get_corrupt_file_count":
        from .context import get_corrupt_file_count as value

        return value
    raise AttributeError(name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
