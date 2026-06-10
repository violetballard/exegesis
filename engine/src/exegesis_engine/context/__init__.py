from __future__ import annotations

__all__ = [
    "ContextBasket",
    "ContextBasketStore",
    "ContextSetRecord",
    "ContextSetStore",
    "SessionState",
    "SessionStore",
    "get_corrupt_file_count",
    "clear_corrupt_files",
    "validate_and_quarantine",
    "purge_corrupt_state",
    "validate_project_name",
    "list_corrupt_files",
    "remove_all_corrupt_files",
    "is_clean_state",
]


def __getattr__(name: str):
    if name == "ContextBasket":
        from exegesis_engine.context.basket import ContextBasket as value

        return value
    if name == "ContextBasketStore":
        from exegesis_engine.context.store import ContextBasketStore as value

        return value
    if name == "ContextSetRecord":
        from exegesis_engine.context.set_store import ContextSetRecord as value

        return value
    if name == "ContextSetStore":
        from exegesis_engine.context.set_store import ContextSetStore as value

        return value
    if name == "SessionState":
        from exegesis_engine.context.session import SessionState as value

        return value
    if name == "SessionStore":
        from exegesis_engine.context.session import SessionStore as value

        return value
    if name == "clear_corrupt_files":
        from exegesis_engine.context.store import clear_corrupt_files as value

        return value
    if name == "validate_and_quarantine":
        from exegesis_engine.context.store import validate_and_quarantine as value

        return value
    if name == "validate_project_name":
        from exegesis_engine.storage.vault import validate_project_name as value

        return value
    if name == "list_corrupt_files":
        from exegesis_engine.context.store import list_corrupt_files as value

        return value
    if name == "purge_corrupt_state":
        from exegesis_engine.context.store import purge_corrupt_state as value

        return value
    if name == "remove_all_corrupt_files":
        from exegesis_engine.context.utils import remove_all_corrupt_files as value

        return value
    if name == "is_clean_state":
        from exegesis_engine.context.store import is_clean_state as value

        return value
    if name == "get_corrupt_file_count":
        from exegesis_engine.context.debug import get_corrupt_file_count as value

        return value
    raise AttributeError(name)
