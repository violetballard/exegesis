from __future__ import annotations

import json
import os
import re
import shutil
import stat
import unicodedata
import weakref
from collections import OrderedDict, UserList
from collections.abc import Iterable as AbstractIterable
from collections.abc import Mapping as AbstractMapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass, field
from pathlib import Path

from exegesis_engine.context.audit import (
    _audit_corrupt_path,
    append_audit_record,
    audit_log_path,
    parse_recovered_timestamp,
    utc_now_iso,
)
from exegesis_engine.storage._corrupt_artifacts import (
    _available_corrupt_path,
    clear_corrupt_artifact_family as _clear_corrupt_artifact_family,
    fsync_file_path as _fsync_file_path,
    fsync_parent_path as _fsync_parent_path,
    quarantine_corrupt_artifact as _quarantine_corrupt_artifact,
    state_root_uses_symlink_alias as _session_state_root_uses_symlink_alias,
)

from .basket import ContextBasket, _canonical_json_dumps, _has_non_finite_float, _is_one_shot_basket_id_snapshot, _mapping_wrapper_exposes_non_plain_json_shape, _payload_as_plain_dict, _payload_has_non_plain_json_shapes, _safe_json_value, _safe_repr

__all__ = ["SessionState", "SessionStore"]

_SESSION_KEYS = {"schema_version", "updated_at", "project_name", "document_path", "basket_item_ids", "recovered_from"}
_SESSION_LEGACY_SEQUENCE_SNAPSHOTS: weakref.WeakKeyDictionary[object, list[object]] = weakref.WeakKeyDictionary()
_SESSION_LEGACY_SEQUENCE_ID_SNAPSHOTS: OrderedDict[int, tuple[object, list[object] | tuple[()]]] = OrderedDict()
_SESSION_BASKET_ITEM_ID_SNAPSHOTS: weakref.WeakKeyDictionary[object, list[object]] = weakref.WeakKeyDictionary()
_SESSION_BASKET_ITEM_ID_SNAPSHOT_IDS: OrderedDict[int, tuple[object, list[object]]] = OrderedDict()
_SESSION_BASKET_ITEM_ID_RECOVERY_SNAPSHOTS: weakref.WeakKeyDictionary[object, bool] = weakref.WeakKeyDictionary()
_SESSION_BASKET_ITEM_ID_RECOVERY_ID_SNAPSHOTS: OrderedDict[int, tuple[object, bool]] = OrderedDict()
_SESSION_LEGACY_SEQUENCE_ID_CACHE_LIMIT = 1024
_SESSION_BASKET_ITEM_ID_CACHE_LIMIT = 1024
_SESSION_BASKET_ITEM_ID_RECOVERY_CACHE_LIMIT = 1024
_SESSION_WINDOWS_RESERVED_DOCUMENT_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}
_SESSION_NONPORTABLE_DOCUMENT_NAME_CHARS = set('<>:"|?*')
_SESSION_NONPORTABLE_PROJECT_NAME_CHARS = set('/\\<>:"|?*')


def _session_payload_is_legacy_sequence(payload: object) -> bool:
    """Return ``True`` when *payload* is a legacy sequence-shaped session envelope."""

    return isinstance(payload, (list, tuple)) or (
        isinstance(payload, AbstractIterable)
        and not isinstance(payload, (str, bytes, bytearray, memoryview, AbstractMapping))
    )


def _read_session_json_text(path: Path) -> str:
    flags = os.O_RDONLY
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if nofollow:
        flags |= nofollow
    fd = os.open(path, flags)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError(f"session payload is not a regular file: {path!r}")
        with os.fdopen(fd, "r", encoding="utf-8") as handle:
            fd = -1
            return handle.read()
    finally:
        if fd >= 0:
            os.close(fd)


def _session_legacy_sequence_item_ids(payload: object) -> list[object] | tuple[()] | None:
    """Return a stable snapshot for legacy sequence payload item ids."""

    if not _session_payload_is_legacy_sequence(payload):
        return None
    if isinstance(payload, list):
        return payload
    if isinstance(payload, tuple):
        if not payload:
            return tuple()
        return list(payload)
    if isinstance(payload, UserList):
        if not payload:
            # An empty UserList is not a canonical JSON type. Signal it as
            # non-canonical empty (same sentinel as exhausted generators) so
            # the quarantine path treats it as malformed session state.
            return tuple()
        return list(payload)
    try:
        raw_values = ContextBasket._ordered_item_id_values(payload)
    except Exception:
        return None
    if raw_values is not None:
        if not raw_values:
            # Preserve the difference between an intentionally empty legacy
            # list and an exhausted non-list iterable. The load path treats
            # empty non-list sequences as malformed basket state and should
            # quarantine them instead of rewriting them into ``[]``.
            return tuple()
        return raw_values
    return None


def _session_cached_legacy_sequence_item_ids(payload: object) -> list[object] | tuple[()] | None:
    """Return a cached legacy sequence snapshot when one is available.

    One-shot iterables such as generators are consumed as soon as they are
    materialized. Caching the first snapshot lets the recovery helpers reuse
    the same recovered basket content across separate helper calls instead of
    collapsing the generator to an empty sequence on the second pass.
    """

    if not _session_payload_is_legacy_sequence(payload):
        return None
    if isinstance(payload, (list, tuple)):
        return _session_legacy_sequence_item_ids(payload)
    if not ContextBasket._is_one_shot_iterator(payload):
        return _session_legacy_sequence_item_ids(payload)
    try:
        cached_item_ids = _SESSION_LEGACY_SEQUENCE_SNAPSHOTS[payload]
    except (KeyError, TypeError):
        payload_id = id(payload)
        cached_entry = _SESSION_LEGACY_SEQUENCE_ID_SNAPSHOTS.get(payload_id)
        if cached_entry is not None:
            cached_payload, cached_item_ids = cached_entry
            if cached_payload is payload:
                _SESSION_LEGACY_SEQUENCE_ID_SNAPSHOTS.move_to_end(payload_id)
                return cached_item_ids
        cached_item_ids = _session_legacy_sequence_item_ids(payload)
        if cached_item_ids is None:
            return None
        try:
            _SESSION_LEGACY_SEQUENCE_SNAPSHOTS[payload] = cached_item_ids
        except TypeError:
            _SESSION_LEGACY_SEQUENCE_ID_SNAPSHOTS[payload_id] = (payload, cached_item_ids)
            _SESSION_LEGACY_SEQUENCE_ID_SNAPSHOTS.move_to_end(payload_id)
            if len(_SESSION_LEGACY_SEQUENCE_ID_SNAPSHOTS) > _SESSION_LEGACY_SEQUENCE_ID_CACHE_LIMIT:
                _SESSION_LEGACY_SEQUENCE_ID_SNAPSHOTS.popitem(last=False)
    return cached_item_ids


def _mapping_is_empty(raw_mapping: AbstractMapping) -> bool:
    """Return ``True`` when *raw_mapping* has no items without trusting truthiness."""

    try:
        iterator = iter(raw_mapping)
    except Exception:
        return False
    try:
        next(iterator)
    except StopIteration:
        return True
    except Exception:
        return False
    return False


def _materialize_session_payload(
    payload: object,
    *,
    preserve_equivalent_raw_wrapper: bool = False,
) -> object:
    """Snapshot live basket-item iterables on a session payload in place."""

    original_payload = payload if isinstance(payload, AbstractMapping) and type(payload) is not dict else None
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        try:
            payload = dict(payload)
        except Exception:
            return original_payload if original_payload is not None else payload
    if isinstance(payload, dict) and "basket_item_ids" in payload:
        raw_item_ids = payload.get("basket_item_ids")
        if isinstance(raw_item_ids, AbstractMapping):
            if _mapping_is_empty(raw_item_ids):
                payload["basket_item_ids"] = []
                _sync_session_payload_mapping_wrapper(
                    original_payload,
                    payload,
                    preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
                )
            return payload
        raw_values = ContextBasket._ordered_item_id_values(raw_item_ids)
        if raw_values is None:
            return payload
        if not raw_values and not isinstance(raw_item_ids, (list, tuple, UserList)):
            # Keep exhausted generators and other empty non-list iterables in
            # their original shape so later quarantine checks still see the
            # malformed source instead of an innocuous empty list.
            return payload
        if not isinstance(raw_item_ids, list):
            # Materialize non-list iterables (generators, tuples, UserLists)
            # to raw list form. Do NOT normalize existing lists here — raw
            # values from a pre-materialized generator must stay intact so
            # callers can inspect them before normalization.
            payload["basket_item_ids"] = list(raw_values)
        _sync_session_payload_mapping_wrapper(
            original_payload,
            payload,
            preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
        )
        return payload
    if _session_payload_is_legacy_sequence(payload):
        raw_values = _session_legacy_sequence_item_ids(payload)
        if raw_values is None:
            return payload
        if not raw_values and not isinstance(payload, (list, tuple, UserList)):
            # Preserve empty legacy iterator shapes for the same reason as
            # dict payloads: the load path needs to distinguish a durable
            # empty list from an exhausted non-list iterable.
            return payload
        return list(raw_values)
    return payload


def _normalize_updated_at(raw_updated_at: object) -> str | None:
    # Delegate to the single shared recovery parser so a session timestamp
    # recovers identically to the document store. The prior body was the same
    # strip/fold/parse/normalize sequence inlined here; sharing it keeps the two
    # readers from drifting apart over time.
    return parse_recovered_timestamp(raw_updated_at)


def _strip_control_chars(value: str) -> str:
    return "".join(
        char
        for char in value
        if ord(char) >= 32
        and ord(char) != 127
        and unicodedata.category(char) not in {"Cc", "Cf", "Zl", "Zp"}
    )


def _normalize_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    candidate = _strip_control_chars(value).strip()
    return candidate or None


def _normalize_project_name(value: object) -> str | None:
    candidate = _normalize_text(value)
    if candidate is None:
        return None
    if candidate in {".", ".."}:
        return None
    if candidate.startswith(".") or candidate.endswith("."):
        return None
    if any(char in _SESSION_NONPORTABLE_PROJECT_NAME_CHARS for char in candidate):
        return None
    if candidate.split(".", 1)[0].upper() in _SESSION_WINDOWS_RESERVED_DOCUMENT_NAMES:
        return None
    return candidate


def _normalize_document_path(value: object) -> str | None:
    if isinstance(value, os.PathLike):
        try:
            value = os.fspath(value)
        except Exception:
            return None
        if not isinstance(value, str):
            return None
    candidate = _normalize_text(value)
    if candidate is None:
        return None
    if "\\" in candidate or candidate.startswith("/"):
        return None
    parts = candidate.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    for part in parts:
        if part != part.strip():
            return None
        if part.startswith(".") or part.endswith("."):
            return None
        if any(char in _SESSION_NONPORTABLE_DOCUMENT_NAME_CHARS for char in part):
            return None
        if part.split(".", 1)[0].upper() in _SESSION_WINDOWS_RESERVED_DOCUMENT_NAMES:
            return None
    return candidate


def _session_payload_needs_recovery_marker_sync(original_payload: object, payload: object) -> bool:
    """Return ``True`` when a wrapper still needs its recovery marker reconciled."""

    if not isinstance(original_payload, AbstractMapping) or not isinstance(payload, dict):
        return False
    try:
        marker_sentinel = object()
        original_payload_snapshot = _payload_as_plain_dict(original_payload)
        # Compare every marker view the wrapper exposes -- both the
        # iteration-visible snapshot and a direct ``.get()`` -- against the
        # canonical payload. A wrapper whose backing store disagrees with its
        # own iteration view (hides the marker from ``__iter__`` or exposes a
        # divergent stale value) must still trigger reconciliation.
        payload_marker = payload.get("recovered_from", marker_sentinel)
        observed_markers = [original_payload.get("recovered_from", marker_sentinel)]
        if original_payload_snapshot is not None:
            observed_markers.append(
                original_payload_snapshot.get("recovered_from", marker_sentinel)
            )
        present_markers = [
            marker for marker in observed_markers if marker is not marker_sentinel
        ]
        if present_markers:
            return any(marker != payload_marker for marker in present_markers)
        return marker_sentinel != payload_marker
    except Exception:
        return True


def _sync_session_payload_mapping_wrapper(
    original_payload: object | None,
    payload: object,
    *,
    preserve_equivalent_raw_wrapper: bool = False,
    preserve_raw_basket_ids: bool = False,
) -> None:
    """Copy a materialized payload back into a caller-owned mapping wrapper."""

    if original_payload is None or original_payload is payload or not isinstance(payload, dict):
        return
    try:
        original_payload_snapshot = _payload_as_plain_dict(original_payload)
        needs_marker_sync = _session_payload_needs_recovery_marker_sync(original_payload, payload)
        if preserve_equivalent_raw_wrapper:
            if original_payload_snapshot == payload and not needs_marker_sync:
                return
        elif (
            original_payload_snapshot == payload
            and not needs_marker_sync
            # A non-``str`` top-level key (e.g. a ``str`` subclass) serializes as
            # its plain ``str`` base, so the wrapper diverges from disk even when
            # dict equality and the marker views agree -- the shared guard
            # normalizes it rather than skipping reconciliation.
            and not _mapping_wrapper_exposes_non_plain_json_shape(original_payload)
        ):
            return
    except Exception:
        pass
    try:
        safe_payload = _safe_json_value(payload) if _has_non_finite_float(payload) else payload
        if safe_payload is not payload and isinstance(safe_payload, dict):
            payload = safe_payload
        if preserve_equivalent_raw_wrapper:
            # Key-by-key sync to avoid replacing equivalent non-plain values
            # (e.g. custom iterables that compare equal to []) with their
            # normalized form.  clear()+update() would overwrite them even
            # when the data content is semantically identical.
            # Only use this path when key sets are identical — if keys must be
            # added or deleted, fall through to clear()+update() which is
            # authoritative and properly tracked by wrapper subclasses.
            try:
                original_keys = set(original_payload.keys())  # type: ignore[union-attr]
                target_keys = set(payload.keys())
                if original_keys == target_keys:
                    # If the only differences between snapshot and payload are
                    # in metadata-stamped fields (updated_at, schema_version),
                    # skip those to avoid spurious mutations in wrappers that
                    # track changes — the disk write already captured the new
                    # value.  When data-content keys also changed, sync
                    # everything including metadata.
                    _META = frozenset({"updated_at", "schema_version"})
                    _snapshot_for_meta = original_payload_snapshot or {}
                    _metadata_only_drift = all(
                        _snapshot_for_meta.get(k) == payload.get(k)
                        for k in payload
                        if k not in _META
                    )
                    for key, value in payload.items():
                        if _metadata_only_drift and key in _META:
                            continue
                        try:
                            existing = original_payload[key]  # type: ignore[index]
                            if existing == value:
                                continue
                            # When the caller holds a materialized raw snapshot
                            # from a one-shot generator, preserve the raw
                            # values instead of overwriting with the normalized
                            # form.  Replayable iterables should still be
                            # normalized; only cached one-shot snapshots are
                            # preserved.  Only applies in the normal success
                            # path where basket ids are not being re-sourced
                            # from a backup or recovery.
                            if (
                                preserve_raw_basket_ids
                                and key == "basket_item_ids"
                                and _is_one_shot_basket_id_snapshot(existing)
                            ):
                                continue
                        except (KeyError, Exception):
                            pass
                        # Use update() so wrapper subclasses that track
                        # mutations via clear()/update() see the change.
                        original_payload.update({key: value})  # type: ignore[union-attr]
                    # Some wrappers hide keys from __iter__ (e.g. recovered_from).
                    # Explicitly remove any such keys that are present via .get()
                    # but absent from the target payload.
                    _hidden_sentinel = object()
                    for _hidden_key in ("recovered_from",):
                        if (
                            _hidden_key not in target_keys
                            and original_payload.get(_hidden_key, _hidden_sentinel) is not _hidden_sentinel  # type: ignore[union-attr]
                        ):
                            del original_payload[_hidden_key]  # type: ignore[union-attr]
                    return
            except Exception:
                pass
        original_payload.clear()
        original_payload.update(payload)
    except Exception:
        pass


def _session_payload_has_non_plain_json_shapes(value: object) -> bool:
    """Return ``True`` when *value* still contains non-plain JSON container shapes.

    Delegates to the shared :func:`_payload_has_non_plain_json_shapes` so session
    classification cannot drift from ``_vault_payload_has_non_plain_json_shapes``.
    """

    return _payload_has_non_plain_json_shapes(value)


def _session_canonical_payload_snapshot(payload: object, raw_item_ids: object | None = None) -> dict[str, object] | None:
    """Return a canonicalized snapshot for caller-owned mapping wrappers.

    The load path uses this to keep live mapping wrappers aligned with the
    canonical basket and text-field normalization even when the payload is
    ultimately quarantined. That keeps the in-memory snapshot audit-friendly
    without changing the persisted quarantine decision.
    """

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return None
    snapshot = dict(payload)
    snapshot.pop("recovered_from", None)
    if raw_item_ids is None:
        raw_item_ids = _snapshot_basket_item_ids(snapshot.get("basket_item_ids", []))
    snapshot["project_name"] = _normalize_project_name(snapshot.get("project_name"))
    snapshot["document_path"] = _normalize_document_path(snapshot.get("document_path"))
    snapshot["basket_item_ids"] = _normalize_item_ids(
        raw_item_ids if raw_item_ids is not None else snapshot.get("basket_item_ids", [])
    )
    return snapshot


def _session_text_field_has_control_chars(value: object) -> bool:
    """Return ``True`` when a session text field contains hard-invalid bytes."""

    if not isinstance(value, str):
        return False
    return any(ord(char) < 32 or ord(char) == 127 for char in value)


def _session_text_field_is_recoverable(value: object) -> bool:
    """Return ``True`` when a session text field can be normalized safely.

    Session metadata is allowed to contain blank or whitespace-only strings
    because the load path can deterministically trim them back to ``None``.
    Non-string values and control characters should force quarantine because
    they are not safe to preserve in persisted local state.
    """

    return value is None or (isinstance(value, str) and not _session_text_field_has_control_chars(value))


def _session_document_path_is_recoverable(value: object) -> bool:
    """Return ``True`` when ``document_path`` can be normalized safely."""

    if value is None:
        return True
    if isinstance(value, os.PathLike):
        try:
            value = os.fspath(value)
        except Exception:
            return False
        if not isinstance(value, str):
            return False
    if not isinstance(value, str) or _session_text_field_has_control_chars(value):
        return False
    if not value.strip():
        return True
    return _normalize_document_path(value) is not None


def _session_project_name_is_recoverable(value: object) -> bool:
    """Return ``True`` when ``project_name`` can be normalized safely."""

    if value is None:
        return True
    if not isinstance(value, str) or _session_text_field_has_control_chars(value):
        return False
    if not value.strip():
        return True
    return _normalize_project_name(value) is not None


def _session_schema_version_is_recoverable(payload: object) -> bool:
    """Return ``True`` when ``schema_version`` is absent or canonical.

    Session state should tolerate missing schema metadata because the load
    path can rewrite it deterministically. Explicit schema values, however,
    must still stay within the supported version range so malformed local
    state gets quarantined instead of being silently normalized.
    """

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if "schema_version" not in payload:
        return True
    schema_version = payload.get("schema_version")
    return isinstance(schema_version, int) and not isinstance(schema_version, bool) and schema_version in {0, 1}


def _session_updated_at_needs_audit_quarantine(payload: object) -> bool:
    """Return ``True`` when ``updated_at`` is present but malformed."""

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if _session_payload_can_preserve_metadata_with_empty_basket(payload):
        return False
    if "updated_at" not in payload or payload.get("updated_at") is None:
        return False
    raw_updated_at = payload.get("updated_at")
    if isinstance(raw_updated_at, str) and not raw_updated_at.strip():
        # Blank timestamps are equivalent to missing metadata. The load path
        # can rewrite them deterministically, so they should not be forced
        # through quarantine.
        return False
    return _normalize_updated_at(raw_updated_at) is None


def _normalize_item_ids(raw_item_ids: object) -> list[str]:
    raw_values = ContextBasket._ordered_item_id_values(raw_item_ids)
    if raw_values is None:
        raw_values = [raw_item_ids]
    normalized: list[str] = []
    seen: set[str] = set()
    for raw_item_id in raw_values:
        item_id = ContextBasket._normalize_item_id(raw_item_id)
        if not item_id or item_id in seen:
            continue
        normalized.append(item_id)
        seen.add(item_id)
    return normalized


def _snapshot_basket_item_ids(raw_item_ids: object) -> object | None:
    """Return a stable snapshot of ``basket_item_ids`` for repeated use.

    Session recovery inspects raw basket values more than once. One-shot
    iterables such as generators would otherwise be consumed during the first
    normalization pass and then appear empty when recovery later decides
    whether the backup should donate its basket contents.
    """

    if isinstance(raw_item_ids, (list, UserList)):
        return raw_item_ids
    if isinstance(raw_item_ids, tuple):
        return list(raw_item_ids)
    if isinstance(raw_item_ids, AbstractSet):
        return sorted(
            raw_item_ids,
            key=lambda value: (ContextBasket._normalize_item_id(value), type(value).__name__, _safe_repr(value)),
        )
    raw_values = ContextBasket._ordered_item_id_values(raw_item_ids)
    if raw_values is None:
        return raw_item_ids
    if not ContextBasket._is_one_shot_iterator(raw_item_ids):
        return list(raw_values)
    try:
        cached_item_ids = _SESSION_BASKET_ITEM_ID_SNAPSHOTS[raw_item_ids]
    except (KeyError, TypeError):
        payload_id = id(raw_item_ids)
        cached_entry = _SESSION_BASKET_ITEM_ID_SNAPSHOT_IDS.get(payload_id)
        if cached_entry is not None:
            cached_payload, cached_item_ids = cached_entry
            if cached_payload is raw_item_ids:
                _SESSION_BASKET_ITEM_ID_SNAPSHOT_IDS.move_to_end(payload_id)
                return cached_item_ids
        cached_item_ids = list(raw_values)
        try:
            _SESSION_BASKET_ITEM_ID_SNAPSHOTS[raw_item_ids] = cached_item_ids
        except TypeError:
            _SESSION_BASKET_ITEM_ID_SNAPSHOT_IDS[payload_id] = (raw_item_ids, cached_item_ids)
            _SESSION_BASKET_ITEM_ID_SNAPSHOT_IDS.move_to_end(payload_id)
            if len(_SESSION_BASKET_ITEM_ID_SNAPSHOT_IDS) > _SESSION_BASKET_ITEM_ID_CACHE_LIMIT:
                _SESSION_BASKET_ITEM_ID_SNAPSHOT_IDS.popitem(last=False)
    return cached_item_ids


def _session_payload_raw_basket_item_ids(
    payload: object,
    *,
    preserve_equivalent_raw_wrapper: bool = False,
) -> object | None:
    """Return the raw basket item ids from *payload* without consuming them twice."""

    original_payload = payload if isinstance(payload, AbstractMapping) and type(payload) is not dict else None
    if _session_payload_is_legacy_sequence(payload):
        return _session_cached_legacy_sequence_item_ids(payload)
    payload = _payload_as_plain_dict(payload)
    if payload is None or "basket_item_ids" not in payload:
        return None
    raw_item_ids = payload.get("basket_item_ids")
    if isinstance(raw_item_ids, UserList):
        materialized_item_ids = list(raw_item_ids)
        payload["basket_item_ids"] = materialized_item_ids
        _sync_session_payload_mapping_wrapper(
            original_payload,
            payload,
            preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
        )
        return materialized_item_ids
    if isinstance(raw_item_ids, AbstractIterable) and not isinstance(
        raw_item_ids,
        (str, bytes, bytearray, memoryview, AbstractMapping, AbstractSet, list, tuple),
    ):
        try:
            raw_values = ContextBasket._ordered_item_id_values(raw_item_ids)
        except Exception:
            return raw_item_ids
        if raw_values is None:
            return raw_item_ids
        if not raw_values:
            # When the caller owns a non-plain-dict mapping wrapper and asks
            # for the original shape to be preserved, keep the raw iterable
            # so quarantine checks can see the non-standard type instead of
            # a recoverable empty tuple.
            if preserve_equivalent_raw_wrapper and original_payload is not None:
                return raw_item_ids
            return tuple()
        # Preserve the raw_values reference so _is_one_shot_basket_id_snapshot
        # can identify the cached snapshot and protect it from normalization
        # during later UserDict sync (preserve_raw_basket_ids guard).
        materialized_item_ids = raw_values if isinstance(raw_values, list) else list(raw_values)
        payload["basket_item_ids"] = materialized_item_ids
        _sync_session_payload_mapping_wrapper(
            original_payload,
            payload,
            preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
        )
        return materialized_item_ids
    raw_values = ContextBasket._ordered_item_id_values(raw_item_ids)
    if raw_values is None:
        return raw_item_ids
    if isinstance(raw_item_ids, AbstractSet):
        # Preserve set-like identity for recovery classification. Empty sets
        # are explicit empty baskets, unlike exhausted iterators or tuples.
        return raw_item_ids
    if isinstance(raw_item_ids, tuple):
        # Preserve tuple-shaped baskets as immutable snapshots so the recovery
        # path can distinguish them from canonical on-disk lists.
        return tuple(raw_values)
    if not raw_values and not isinstance(raw_item_ids, (list, UserList)):
        # Snapshot empty one-shot iterables too so later recovery checks see a
        # stable empty container instead of an exhausted generator object.
        return tuple()
    return list(raw_values)


def _session_basket_item_ids_are_recoverable(raw_item_ids: object) -> bool:
    """Return ``True`` when ``basket_item_ids`` can be normalized safely.

    Session state should tolerate the same recoverable item-id shapes as the
    basket store, but it should still quarantine values that would collapse to
    an empty basket because they are fundamentally malformed rather than just
    needing normalization.
    """

    raw_values = ContextBasket._ordered_item_id_values(raw_item_ids)
    if raw_values is None:
        if isinstance(raw_item_ids, AbstractMapping):
            return _mapping_is_empty(raw_item_ids)
        if isinstance(raw_item_ids, str):
            return bool(raw_item_ids.strip())
        return bool(ContextBasket._normalize_item_id(raw_item_ids))
    if not raw_values:
        # Empty lists and explicit set-like containers are intentional empty
        # baskets. Tuple-shaped legacy payloads are also durable snapshots,
        # unlike exhausted generators, so they can be rewritten safely.
        return isinstance(raw_item_ids, (list, tuple, UserList, AbstractSet))

    saw_recoverable_item_id = False
    for raw_item_id in raw_values:
        normalized_item_id = ContextBasket._normalize_item_id(raw_item_id)
        if isinstance(raw_item_id, str) and not raw_item_id.strip():
            continue
        if not normalized_item_id:
            return False
        saw_recoverable_item_id = True
    return saw_recoverable_item_id


def _prefer_session_timestamp(primary_updated_at: str | None, backup_updated_at: str | None) -> str | None:
    """Return the newest recoverable session timestamp.

    Session rewrites should preserve an existing clean timestamp when they
    can, rather than always inventing a fresh ``updated_at`` value. When both
    sides are available we keep the newest one so a clean backup can donate a
    better audit time to a rewritten primary payload.
    """

    if primary_updated_at is None:
        return backup_updated_at
    if backup_updated_at is None:
        return primary_updated_at
    return max(primary_updated_at, backup_updated_at)


def _prefer_session_state_candidate(
    current_state: SessionState | None,
    current_updated_at: str | None,
    candidate_state: SessionState | None,
    candidate_updated_at: str | None,
) -> tuple[SessionState | None, str | None]:
    """Return the newest available session candidate."""

    if candidate_state is None:
        return current_state, current_updated_at
    if current_state is None:
        return candidate_state, candidate_updated_at
    if candidate_updated_at is not None and (
        current_updated_at is None or candidate_updated_at > current_updated_at
    ):
        return candidate_state, candidate_updated_at
    return current_state, current_updated_at


def _session_states_conflict(
    left_state: SessionState | None,
    left_updated_at: str | None,
    right_state: SessionState | None,
    right_updated_at: str | None,
) -> bool:
    """Return true when staged session candidates are equally fresh but divergent."""

    if left_state is None or right_state is None:
        return False
    if left_updated_at != right_updated_at:
        return False
    return left_state != right_state


def _merge_session_state(primary_state: SessionState, backup_state: SessionState | None) -> SessionState:
    """Fill missing session text fields from *backup_state* when available.

    A partially populated primary session should not discard recoverable
    document or project metadata that the backup still knows about. The
    primary basket contents remain authoritative unless the primary state is
    entirely unavailable.
    """

    if backup_state is None:
        return primary_state
    return SessionState(
        project_name=primary_state.project_name if primary_state.project_name is not None else backup_state.project_name,
        document_path=primary_state.document_path if primary_state.document_path is not None else backup_state.document_path,
        basket_item_ids=list(primary_state.basket_item_ids),
    )


def _session_recoverable_metadata_fields(
    payload: object,
    *,
    allow_recovered_from: bool = False,
) -> tuple[str | None, str | None]:
    """Return recoverable ``project_name`` and ``document_path`` values from *payload*."""

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return None, None
    if not allow_recovered_from and "recovered_from" in payload:
        return None, None
    project_name = payload.get("project_name")
    document_path = payload.get("document_path")
    return (
        _normalize_project_name(project_name) if _session_project_name_is_recoverable(project_name) else None,
        _normalize_document_path(document_path) if _session_document_path_is_recoverable(document_path) else None,
    )


def _session_primary_metadata_can_donate(payload: object) -> bool:
    """Return ``True`` when a primary payload can donate metadata during recovery.

    Recovery should only reuse primary document/project metadata when the
    envelope itself is still trustworthy. Basket item id corruption is fine to
    recover around, but unexpected fields or unrecoverable text values are not.
    """

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if "recovered_from" in payload:
        return False
    if any(key not in _SESSION_KEYS for key in payload):
        return False
    if not _session_schema_version_is_recoverable(payload):
        return False
    project_name = payload.get("project_name")
    if not _session_project_name_is_recoverable(project_name):
        return False
    document_path = payload.get("document_path")
    return _session_document_path_is_recoverable(document_path)


def _session_recovered_primary_metadata_can_donate(payload: object) -> bool:
    """Return ``True`` when a recovered primary payload can still donate metadata."""

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if "recovered_from" not in payload:
        return False
    if any(key not in _SESSION_KEYS for key in payload):
        return False
    if not _session_schema_version_is_recoverable(payload):
        return False
    project_name = payload.get("project_name")
    if not _session_project_name_is_recoverable(project_name):
        return False
    document_path = payload.get("document_path")
    return _session_document_path_is_recoverable(document_path)


def _session_basket_item_ids_should_recover_from_backup(raw_item_ids: object) -> bool:
    """Return ``True`` when a backup basket should donate its item ids.

    Explicitly empty baskets remain authoritative, but missing or malformed
    basket fields that collapse to an empty normalized list can safely borrow
    the backup contents instead of rewriting the session with an empty basket.
    """

    if ContextBasket._is_one_shot_iterator(raw_item_ids):
        try:
            cached_recovery_decision = _SESSION_BASKET_ITEM_ID_RECOVERY_SNAPSHOTS[raw_item_ids]
        except (KeyError, TypeError):
            payload_id = id(raw_item_ids)
            cached_entry = _SESSION_BASKET_ITEM_ID_RECOVERY_ID_SNAPSHOTS.get(payload_id)
            if cached_entry is not None:
                cached_payload, cached_recovery_decision = cached_entry
                if cached_payload is raw_item_ids:
                    _SESSION_BASKET_ITEM_ID_RECOVERY_ID_SNAPSHOTS.move_to_end(payload_id)
                    return cached_recovery_decision
            cached_recovery_decision = _session_basket_item_ids_should_recover_from_backup_uncached(raw_item_ids)
            try:
                _SESSION_BASKET_ITEM_ID_RECOVERY_SNAPSHOTS[raw_item_ids] = cached_recovery_decision
            except TypeError:
                _SESSION_BASKET_ITEM_ID_RECOVERY_ID_SNAPSHOTS[payload_id] = (raw_item_ids, cached_recovery_decision)
                _SESSION_BASKET_ITEM_ID_RECOVERY_ID_SNAPSHOTS.move_to_end(payload_id)
                if len(_SESSION_BASKET_ITEM_ID_RECOVERY_ID_SNAPSHOTS) > _SESSION_BASKET_ITEM_ID_RECOVERY_CACHE_LIMIT:
                    _SESSION_BASKET_ITEM_ID_RECOVERY_ID_SNAPSHOTS.popitem(last=False)
            return cached_recovery_decision
        return cached_recovery_decision
    return _session_basket_item_ids_should_recover_from_backup_uncached(raw_item_ids)


def _session_basket_item_ids_should_recover_from_backup_uncached(raw_item_ids: object) -> bool:
    """Return the recovery decision for *raw_item_ids* without iterator caching."""

    if raw_item_ids is None:
        return True
    if isinstance(raw_item_ids, (list, UserList)):
        # Only donate backup item ids when the primary list would otherwise
        # normalize to an empty basket. Recoverable non-empty primary lists
        # should stay authoritative so a richer backup does not overwrite the
        # user's current basket contents.
        return bool(raw_item_ids) and not _normalize_item_ids(raw_item_ids)
    if isinstance(raw_item_ids, AbstractMapping):
        # Empty mapping-shaped baskets behave like explicit empty baskets and
        # should not be replaced by backup contents. Non-empty mappings still
        # need the backup donation path because they do not normalize safely.
        return not _mapping_is_empty(raw_item_ids)
    if isinstance(raw_item_ids, str):
        return not raw_item_ids.strip()
    raw_values = ContextBasket._ordered_item_id_values(raw_item_ids)
    if raw_values is None:
        # Scalar numeric / path-like ids already normalize in place, so a
        # backup should not replace them just because the primary used a
        # non-list shape. Mapping-shaped payloads, however, collapse to an
        # empty normalized basket and can safely borrow the backup contents.
        if ContextBasket._normalize_item_id(raw_item_ids):
            return False
        return isinstance(raw_item_ids, AbstractMapping)
    if not raw_values:
        # Empty non-list iterables are still malformed session state; let the
        # backup donate a real basket instead of freezing the empty shape.
        # Empty tuples and sets are durable snapshots, so keep them
        # authoritative instead of replacing them with backup contents.
        return not isinstance(raw_item_ids, (list, tuple, UserList, AbstractSet))
    # Reuse the snapshot we already built above so one-shot iterables do not
    # get consumed a second time and accidentally appear empty.
    return not _normalize_item_ids(raw_values)


def _session_basket_item_ids_are_empty_non_list_iterable(raw_item_ids: object) -> bool:
    """Return ``True`` when *raw_item_ids* is an empty malformed iterable.

    A blank tuple, set, or generator is not a canonical basket, but the
    surrounding session metadata may still be usable. The load path uses this
    helper to keep that metadata when no backup can donate a better basket.
    """

    raw_values = ContextBasket._ordered_item_id_values(raw_item_ids)
    return raw_values == [] and not isinstance(raw_item_ids, (list, tuple, UserList, AbstractSet))


def _session_basket_item_ids_can_preserve_metadata_without_backup(raw_item_ids: object) -> bool:
    """Return ``True`` when basket corruption should not drop recoverable metadata.

    Non-list basket values are the main case where the basket itself is
    unrecoverable but the rest of the session still should survive. Concrete
    tuple- or set-shaped inputs that can still be materialized are eligible as
    metadata-only recovery sources when their item ids do not normalize cleanly.
    Mapping-shaped inputs are also treated as metadata-only corruption so
    caller-provided mapping objects do not cause the session floor to discard
    recoverable project or document state. Lists stay on the stricter
    quarantine path so blank-list payloads continue to be treated as explicitly
    malformed session state.
    """

    if raw_item_ids is None or isinstance(raw_item_ids, (list, UserList)):
        return False
    if isinstance(raw_item_ids, AbstractMapping):
        return True
    # Use the stable snapshot helper so one-shot iterables are classified
    # against the same materialized values on repeated calls.
    raw_snapshot = _snapshot_basket_item_ids(raw_item_ids)
    if raw_snapshot is raw_item_ids:
        if isinstance(raw_item_ids, str):
            return bool(raw_item_ids.strip())
        return bool(ContextBasket._normalize_item_id(raw_item_ids))
    if isinstance(raw_snapshot, list) and not raw_snapshot:
        return True
    return not _session_basket_item_ids_are_recoverable(raw_snapshot)


def _session_recovered_from_source(value: object) -> str | None:
    """Return a normalized recovery source tag when *value* is recognized."""

    if not isinstance(value, str):
        return None
    normalized = re.sub(r"[-\s]+", "_", value.strip().lower())
    if normalized in {"tmp", "backup", "seed"}:
        return normalized
    if normalized == "backup_tmp":
        return "backup"
    if normalized == "seed_tmp":
        return "seed"
    return None


def _audit_basket_item_ids(payload: dict[str, object]) -> list[str]:
    """Return the canonical basket snapshot used in session audit records."""

    return _normalize_item_ids(payload.get("basket_item_ids", []))


def _session_payload_can_preserve_metadata_with_empty_basket(raw_payload: object, raw_item_ids: object | None = None) -> bool:
    """Return ``True`` when a malformed payload can still donate session metadata.

    The recovery path accepts missing baskets, empty non-list baskets, and
    other inspectable non-list basket shapes that still need quarantine.
    """

    raw_payload = _payload_as_plain_dict(raw_payload)
    if raw_payload is None or "recovered_from" in raw_payload:
        return False
    if not _session_schema_version_is_recoverable(raw_payload):
        return False
    project_name, document_path = _session_recoverable_metadata_fields(raw_payload)
    if project_name is None and document_path is None:
        return False
    basket_source = raw_item_ids if raw_item_ids is not None else raw_payload.get("basket_item_ids")
    if basket_source is None:
        # A missing basket field is recoverable metadata-only state, just like
        # an explicitly empty non-list basket iterable. Keep it eligible for
        # the empty-basket rewrite path so callers do not have to special-case
        # the absent-field shape.
        return "basket_item_ids" not in raw_payload
    if isinstance(basket_source, (list, UserList)):
        # A canonical empty basket should still preserve recoverable session
        # metadata when the rest of the payload is dirty, such as when an
        # unexpected field forces quarantine.
        return not basket_source
    if isinstance(basket_source, AbstractMapping):
        # Dict-shaped basket payloads are never authoritative basket content,
        # but they can still donate project/document metadata even when the
        # basket contents themselves need quarantine. Treat them the same way
        # whether they are empty or carry malformed values.
        return True
    return _session_basket_item_ids_can_preserve_metadata_without_backup(basket_source)


def _session_payload_needs_audit_quarantine(payload: object, raw_item_ids: object | None = None) -> bool:
    if _session_payload_is_legacy_sequence(payload):
        # Legacy list-shaped backups can still be recovered into session
        # basket state, so only quarantine them when the item ids themselves
        # are malformed.
        legacy_item_ids = raw_item_ids if raw_item_ids is not None else _session_cached_legacy_sequence_item_ids(payload)
        if legacy_item_ids == ():
            return True
        return not _session_basket_item_ids_are_recoverable(
            legacy_item_ids,
        )
    payload = _materialize_session_payload(payload)
    if not isinstance(payload, dict):
        return True
    if "recovered_from" in payload:
        return True
    if any(key not in _SESSION_KEYS for key in payload):
        return True
    if not _session_schema_version_is_recoverable(payload):
        return True
    project_name = payload.get("project_name")
    if not _session_project_name_is_recoverable(project_name):
        return True
    document_path = payload.get("document_path")
    if not _session_document_path_is_recoverable(document_path):
        return True
    if raw_item_ids is None:
        if "basket_item_ids" not in payload:
            return False
        raw_item_ids = payload.get("basket_item_ids")
    if raw_item_ids is None:
        # An explicit ``null`` basket is malformed even though a missing
        # basket field can still be recovered deterministically.
        return True
    if isinstance(raw_item_ids, AbstractMapping):
        return not _mapping_is_empty(raw_item_ids)
    return not _session_basket_item_ids_are_recoverable(raw_item_ids)


def _session_recovered_backup_is_last_resort_recoverable(
    payload: object,
    raw_item_ids: object | None = None,
) -> bool:
    """Return ``True`` when a recovered backup can still donate session state."""

    if _session_payload_is_legacy_sequence(payload):
        legacy_item_ids = raw_item_ids if raw_item_ids is not None else _session_cached_legacy_sequence_item_ids(payload)
        if not legacy_item_ids:
            return False
        return _session_basket_item_ids_are_recoverable(
            legacy_item_ids,
        )
    payload = _materialize_session_payload(payload)
    if not isinstance(payload, dict) or "recovered_from" not in payload:
        return False
    if _session_recovered_from_source(payload.get("recovered_from")) is None:
        return False
    raw_updated_at = payload.get("updated_at")
    if isinstance(raw_updated_at, str) and not raw_updated_at.strip():
        return False
    candidate_payload = dict(payload)
    candidate_payload.pop("recovered_from", None)
    if raw_item_ids is None:
        raw_item_ids = _session_payload_raw_basket_item_ids(candidate_payload)
    if raw_item_ids == ():
        source_item_ids = candidate_payload.get("basket_item_ids")
        if not isinstance(source_item_ids, (list, UserList, AbstractSet)):
            return False
    if isinstance(raw_item_ids, AbstractMapping):
        # Mapping-shaped baskets collapse to an empty normalized basket. Let a
        # recovered backup donate that empty basket only when the surrounding
        # envelope is still canonical. Unknown fields should continue to force
        # quarantine even if the basket itself is recoverable.
        if any(key not in _SESSION_KEYS for key in candidate_payload):
            return False
        if _session_payload_can_preserve_metadata_with_empty_basket(candidate_payload, []):
            return True
        return not _session_updated_at_needs_audit_quarantine(candidate_payload)
    if raw_item_ids is not None:
        candidate_payload["basket_item_ids"] = raw_item_ids
    return not _session_payload_needs_audit_quarantine(candidate_payload, raw_item_ids)


def _session_recovered_backup_state(payload: object, raw_item_ids: object | None = None) -> SessionState | None:
    """Return recoverable session state from a backup payload."""

    original_payload = payload if isinstance(payload, AbstractMapping) and type(payload) is not dict else None
    if not _session_recovered_backup_is_last_resort_recoverable(payload, raw_item_ids):
        return None
    if _session_payload_is_legacy_sequence(payload):
        if raw_item_ids is None:
            raw_item_ids = _session_cached_legacy_sequence_item_ids(payload)
        return SessionState(
            basket_item_ids=_normalize_item_ids(raw_item_ids if raw_item_ids is not None else payload),
        )
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return None
    if not isinstance(payload, dict):
        return None
    if raw_item_ids is None:
        raw_item_ids = _snapshot_basket_item_ids(payload.get("basket_item_ids", []))
    recovered_state = SessionState(
        project_name=_normalize_project_name(payload.get("project_name")),
        document_path=_normalize_document_path(payload.get("document_path")),
        basket_item_ids=_normalize_item_ids(raw_item_ids if raw_item_ids is not None else payload.get("basket_item_ids", [])),
    )
    if original_payload is not None:
        canonical_snapshot = _session_canonical_payload_snapshot(payload, raw_item_ids)
        if canonical_snapshot is not None:
            _sync_session_payload_mapping_wrapper(
                original_payload,
                canonical_snapshot,
                preserve_equivalent_raw_wrapper=True,
            )
    return recovered_state


def _quarantine_path(path: Path) -> None:
    # Route the session quarantine target through the shared
    # ``_available_corrupt_path`` rather than a session-local collision walk.
    # The two had drifted: the local copy capped at ``range(1, 1000)`` (vs the
    # shared ``_MAX_CORRUPT_PATH_CANDIDATES``) and probed each candidate with a
    # bare ``exists()``/``is_symlink()`` that let an ``OSError``/``RuntimeError``
    # propagate instead of skipping the unprobeable name -- so the same blocking
    # alias could quarantine to a different path (or fail outright) depending on
    # which store handled it. The shared helper's ``_corrupt_path_is_available``
    # treats a failed probe as occupied and walks on, and emits the identical
    # ``{stem}.{index}.corrupt.json`` numbering for the ``.corrupt.json`` target
    # below, so recovery stays deterministic and consistent across every store.
    _quarantine_corrupt_artifact(path, _available_corrupt_path(path.with_suffix(".corrupt.json")))


def _quarantine_blocking_session_artifact(path: Path) -> bool:
    try:
        if path.is_symlink():
            _quarantine_path(path)
            return True
        if path.exists() and not path.is_file():
            _quarantine_path(path)
            return True
    except (OSError, RuntimeError):
        # Treat transient probe failures as non-blocking. The atomic replace
        # path can still overwrite a regular file, and the read path can fall
        # back to backup/staged state instead of surfacing filesystem probe
        # noise as a session recovery failure.
        return False
    return False


def _quarantine_blocking_session_artifact_and_fsync(path: Path) -> bool:
    quarantined = _quarantine_blocking_session_artifact(path)
    if quarantined:
        _fsync_session_parent(path)
    return quarantined


def _quarantine_session_path_and_fsync(path: Path) -> None:
    _quarantine_path(path)
    _fsync_session_parent(path)


def _session_write_temp_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.tmp")


def _session_legacy_write_temp_path(path: Path) -> Path:
    return path.with_suffix(".tmp")


def _session_undotted_write_temp_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.tmp")


def _session_staged_temp_paths(path: Path) -> tuple[Path, ...]:
    temp_paths = (
        _session_write_temp_path(path),
        _session_legacy_write_temp_path(path),
        _session_undotted_write_temp_path(path),
    )
    return tuple(dict.fromkeys(temp_paths))


def _session_noncanonical_staged_temp_paths(path: Path) -> tuple[Path, ...]:
    """Return staged temp siblings of *path* that are not the active write temp.

    The canonical ``.{name}.tmp`` temp is the current writer's own working file
    and is recreated on every save, so it is removed outright. The legacy
    ``{stem}.tmp`` and undotted ``{name}.tmp`` siblings are only ever remnants of
    an interrupted older writer; an interrupted legacy write leaves partial
    old-format state stranded under one of these names. Return them so callers
    can stale-quarantine that state for audit instead of silently deleting it --
    the same contract the context-basket and context-set stores give on save.
    """

    canonical_temp = _session_write_temp_path(path)
    return tuple(temp for temp in _session_staged_temp_paths(path) if temp != canonical_temp)


def _quarantine_stale_session_temp_artifact(path: Path) -> None:
    if path.exists() or path.is_symlink():
        # Preserve the stale temp under its full ``{name}.stale.corrupt.json``
        # name for every artifact kind, not just plain files. A symlink (or other
        # non-file) at a legacy ``{stem}.tmp`` path previously fell back to
        # ``path.with_suffix(".corrupt.json")``, which collapses the ``.tmp``
        # segment (``session.tmp`` -> ``session.corrupt.json``) and misfiles the
        # interrupted-temp artifact into the *primary* state's corrupt family --
        # so ``SessionStore.clear``'s per-temp ``.stale.`` family sweep never
        # matched it. Keeping the full name lands the quarantine in the temp's own
        # family; ``_quarantine_corrupt_artifact`` still numbers any collision as
        # ``{name}.stale.{N}.corrupt.json``, which that sweep also recognizes.
        _quarantine_corrupt_artifact(path, path.with_name(f"{path.name}.stale.corrupt.json"))


def _quarantine_stale_session_temp_artifact_and_fsync(path: Path) -> None:
    parent_existed = path.parent.exists()
    _quarantine_stale_session_temp_artifact(path)
    if parent_existed:
        _fsync_session_parent(path)


def _remove_session_temp_path(path: Path) -> bool:
    try:
        if path.is_symlink():
            _quarantine_path(path)
            return True
        elif path.exists() and not path.is_file():
            _quarantine_path(path)
            return True
        elif path.exists():
            path.unlink()
            return True
    except (OSError, RuntimeError):
        return False
    return False


def _remove_session_temp_path_and_fsync(path: Path) -> None:
    if _remove_session_temp_path(path):
        _fsync_session_parent(path)


def _cleanup_session_write_temp_path(path: Path) -> None:
    if _remove_session_temp_path(path):
        _fsync_session_parent(path)


def _remove_session_staged_temp_paths_and_fsync(*paths: Path) -> None:
    for path in paths:
        # The canonical write temp is the active writer's own file and is safe
        # to delete before re-staging. The legacy/undotted siblings carry
        # partial old-format state from an interrupted writer, so quarantine
        # them for audit rather than dropping them on the floor.
        noncanonical = set(_session_noncanonical_staged_temp_paths(path))
        for temp_path in _session_staged_temp_paths(path):
            if temp_path in noncanonical:
                _quarantine_stale_session_temp_artifact_and_fsync(temp_path)
            else:
                _remove_session_temp_path_and_fsync(temp_path)


def _remove_session_corrupt_artifacts(state_root: Path, base_path: Path) -> None:
    """Remove all quarantine artifacts for *base_path* under *state_root*.

    The quarantine path generator produces ``{base_name}.corrupt.json`` and
    ``{base_name}.<N>.corrupt.json`` variants.  This helper sweeps the state
    root to remove every matching artifact so :meth:`SessionStore.clear` can
    perform a deterministic reset.
    """

    base_name = base_path.with_suffix("").name
    pattern = re.compile(re.escape(base_name) + r"(\.\d+)?\.corrupt\.json$")
    removed = False
    try:
        for entry in state_root.iterdir():
            if entry.name == base_path.name:
                continue
            if pattern.fullmatch(entry.name):
                removed = _remove_session_clear_artifact(entry) or removed
    except (OSError, RuntimeError):
        # Sweeping quarantine artifacts for a deterministic ``SessionStore.clear``
        # reset is best-effort: a directory listing that fails leaves the
        # already-handled corrupt files in place rather than crashing the reset.
        # ``state_root.iterdir()`` raises ``OSError`` on a filesystem rejection,
        # and a constrained runtime can surface the same rejection as
        # ``RuntimeError``; the inner :func:`_remove_session_clear_artifact` and
        # :func:`_fsync_session_parent` already tolerate both, so close the
        # divergence here rather than force a defensive one-off repair on the
        # engine workflow loop.
        pass
    if removed:
        _fsync_session_parent(state_root)


def _remove_session_clear_artifact(path: Path) -> bool:
    try:
        if path.is_symlink() or path.is_file():
            path.unlink()
            return True
        if path.is_dir():
            shutil.rmtree(path)
            return True
    except (OSError, RuntimeError):
        return False
    return False


def _stage_session_payload(path: Path, encoded: str) -> Path:
    temp_path = _session_write_temp_path(path)
    _remove_session_temp_path_and_fsync(temp_path)
    raw = encoded.encode("utf-8")
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    fd = -1
    try:
        fd = os.open(temp_path, flags, 0o666)
        os.write(fd, raw)
        os.fsync(fd)
    except FileExistsError:
        if fd >= 0:
            os.close(fd)
            fd = -1
        _cleanup_session_write_temp_path(temp_path)
        raise
    except OSError:
        if fd >= 0:
            os.close(fd)
            fd = -1
        _cleanup_session_write_temp_path(temp_path)
        raise
    finally:
        if fd >= 0:
            os.close(fd)
    _fsync_session_parent(temp_path)
    return temp_path


def _write_session_temp_payload(path: Path, encoded: str) -> Path:
    """Write *encoded* to a temp file for *path* using write_text and _fsync_session_path.

    Unlike _stage_session_payload this path is monkeypatchable via Path.write_text
    and _fsync_session_path. Raises FileExistsError if a symlink or unexpected
    file appears at the temp path after cleanup.
    """
    temp_path = _session_write_temp_path(path)
    _remove_session_temp_path_and_fsync(temp_path)
    if temp_path.is_symlink() or temp_path.exists():
        raise FileExistsError(f"temp path already exists after cleanup: {temp_path!r}")
    try:
        temp_path.write_text(encoded, encoding="utf-8")
    except OSError:
        _cleanup_session_write_temp_path(temp_path)
        raise
    if temp_path.is_symlink():
        _cleanup_session_write_temp_path(temp_path)
        raise FileExistsError(f"session temp path became a symlink: {temp_path!r}")
    _fsync_session_path(temp_path)
    _fsync_session_parent(temp_path)
    return temp_path


def _replace_staged_session_payload(temp_path: Path, path: Path) -> None:
    if _quarantine_blocking_session_artifact_and_fsync(temp_path):
        raise ValueError(f"staged session payload is not a regular file: {temp_path!r}")
    _quarantine_blocking_session_artifact_and_fsync(path)
    temp_path.replace(path)
    _fsync_session_parent(path)


def _fsync_session_path(path: Path) -> None:
    # Named content-flush seam hardening tests patch in isolation; the body is
    # the shared :func:`_corrupt_artifacts.fsync_file_path` so the durability
    # flush stays one audited path across all stores.
    _fsync_file_path(path)


def _fsync_session_parent(path: Path) -> None:
    # Named best-effort parent-fsync seam hardening tests patch in isolation; the
    # body is the shared :func:`_corrupt_artifacts.fsync_parent_path` so the
    # directory flush stays one audited path across all stores.
    _fsync_parent_path(path)


def _ensure_session_state_root(path: Path) -> None:
    try:
        is_symlink = path.is_symlink()
        exists = path.exists()
        is_dir = path.is_dir() if exists else False
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"session state root cannot be probed safely: {path!r}") from exc
    if is_symlink or (exists and not is_dir):
        _quarantine_session_path_and_fsync(path)
    try:
        existed = path.exists()
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"session state root cannot be probed safely: {path!r}") from exc
    path.mkdir(parents=True, exist_ok=True)
    if not existed:
        _fsync_session_parent(path)


def _reject_session_state_root_alias(path: Path) -> None:
    if _session_state_root_uses_symlink_alias(path):
        raise ValueError(f"session state root uses a symlink alias: {path!r}")


@dataclass
class SessionState:
    project_name: str | None = None
    document_path: str | None = None
    basket_item_ids: list[str] = field(default_factory=list)

    def normalize(self) -> None:
        self.project_name = _normalize_project_name(self.project_name)
        self.document_path = _normalize_document_path(self.document_path)
        self.basket_item_ids = _normalize_item_ids(self.basket_item_ids)

    def __post_init__(self) -> None:
        self.normalize()


class SessionStore:
    """Persist the engine session floor in a deterministic, recoverable form."""

    def __init__(self, state_root: Path | str):
        self.state_root = Path(state_root)
        if _session_state_root_uses_symlink_alias(self.state_root):
            raise ValueError(f"session state root uses a symlink alias: {state_root!r}")
        self.primary_path = self.state_root / "session.json"
        self.backup_path = self.state_root / "session.bak.json"

    def _write_payload(self, payload: dict[str, object]) -> None:
        _reject_session_state_root_alias(self.state_root)
        _quarantine_blocking_session_artifact_and_fsync(self.primary_path)
        _quarantine_blocking_session_artifact_and_fsync(self.backup_path)
        _ensure_session_state_root(self.primary_path.parent)
        encoded = _canonical_json_dumps(payload)
        primary_temp_path = _session_write_temp_path(self.primary_path)
        backup_temp_path = _session_write_temp_path(self.backup_path)
        try:
            _remove_session_staged_temp_paths_and_fsync(self.primary_path, self.backup_path)
            primary_temp_path = _write_session_temp_payload(self.primary_path, encoded)
            backup_temp_path = _write_session_temp_payload(self.backup_path, encoded)
            _replace_staged_session_payload(backup_temp_path, self.backup_path)
            _replace_staged_session_payload(primary_temp_path, self.primary_path)
        finally:
            _cleanup_session_write_temp_path(primary_temp_path)
            _cleanup_session_write_temp_path(backup_temp_path)
        try:
            append_audit_record(
                audit_log_path(self.primary_path, self.__class__.__name__),
                {
                    "event": "save",
                    "timestamp": utc_now_iso(),
                    "project_name": payload.get("project_name"),
                    "document_path": payload.get("document_path"),
                    "basket_item_ids": _audit_basket_item_ids(payload),
                },
            )
        except Exception:  # pragma: no cover - audit logging must not block persistence
            pass

    def _write_backup_payload(self, payload: dict[str, object]) -> None:
        _reject_session_state_root_alias(self.state_root)
        _quarantine_blocking_session_artifact_and_fsync(self.backup_path)
        _ensure_session_state_root(self.backup_path.parent)
        encoded = _canonical_json_dumps(payload)
        primary_temp_path = _session_write_temp_path(self.primary_path)
        backup_temp_path = _session_write_temp_path(self.backup_path)
        try:
            _remove_session_staged_temp_paths_and_fsync(self.primary_path, self.backup_path)
            backup_temp_path = _write_session_temp_payload(self.backup_path, encoded)
            _replace_staged_session_payload(backup_temp_path, self.backup_path)
        finally:
            _cleanup_session_write_temp_path(primary_temp_path)
            _cleanup_session_write_temp_path(backup_temp_path)
        try:
            append_audit_record(
                audit_log_path(self.primary_path, self.__class__.__name__),
                {
                    "event": "save",
                    "timestamp": utc_now_iso(),
                    "path": "backup",
                    "project_name": payload.get("project_name"),
                    "document_path": payload.get("document_path"),
                    "basket_item_ids": _audit_basket_item_ids(payload),
                },
            )
        except Exception:  # pragma: no cover - audit logging must not block persistence
            pass

    def _payload_from_state(self, state: SessionState, *, updated_at: str | None = None, recovered_from: str | None = None) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": 1,
            "updated_at": updated_at or utc_now_iso(),
            "project_name": state.project_name,
            "document_path": state.document_path,
            "basket_item_ids": list(state.basket_item_ids),
        }
        if recovered_from is not None:
            payload["recovered_from"] = recovered_from
        return payload

    def _load_payload(self, path: Path) -> object | None:
        _reject_session_state_root_alias(self.state_root)
        probe_failed = False
        try:
            if path.is_symlink():
                _quarantine_path(path)
                return None
            if not path.exists():
                return None
        except (OSError, RuntimeError):
            probe_failed = True
        try:
            payload = json.loads(_read_session_json_text(path))
        except Exception:
            if not probe_failed:
                _quarantine_path(path)
            return None
        if payload is None:
            # JSON ``null`` is syntactically valid but still malformed session
            # state. Quarantine it instead of treating it like an absent file.
            _quarantine_path(path)
            return None
        if not isinstance(payload, dict) and not _session_payload_is_legacy_sequence(payload):
            # Scalar JSON payloads cannot represent session state. Quarantine
            # them here so direct loader callers see the same safety boundary
            # as the higher-level recovery flow.
            _quarantine_path(path)
            return None
        return payload

    def _peek_json_payload(self, path: Path) -> object | None:
        try:
            if path.is_symlink():
                return None
            if not path.exists():
                return None
        except (OSError, RuntimeError):
            return None
        try:
            return json.loads(_read_session_json_text(path))
        except Exception:  # pragma: no cover - read-only snapshot helper
            return None

    def _load_candidate_state(
        self,
        path: Path,
    ) -> tuple[object | None, object | None, object | None, SessionState | None, str | None]:
        source_payload = self._load_payload(path)
        raw_item_ids = _session_payload_raw_basket_item_ids(
            source_payload,
            preserve_equivalent_raw_wrapper=True,
        )
        payload = _materialize_session_payload(
            source_payload,
            preserve_equivalent_raw_wrapper=True,
        )
        state = self._payload_to_state(
            payload,
            raw_item_ids,
            preserve_equivalent_raw_wrapper=True,
        )
        recovered_staged_state = False
        if state is None and _session_recovered_backup_is_last_resort_recoverable(payload, raw_item_ids):
            state = _session_recovered_backup_state(payload, raw_item_ids)
            recovered_staged_state = state is not None
        updated_at = _normalize_updated_at(payload.get("updated_at")) if isinstance(payload, dict) else None
        # An empty tuple source payload materializes cleanly to an empty list
        # and is recoverable as an empty basket — skip quarantine so the load
        # path can rewrite it in place rather than treating it as corruption.
        source_is_empty_tuple = isinstance(source_payload, tuple) and not source_payload
        quarantine_needed = payload is not None and (
            (
                not recovered_staged_state
                and not source_is_empty_tuple
                and _session_payload_needs_audit_quarantine(payload, raw_item_ids)
            )
            or _session_updated_at_needs_audit_quarantine(payload)
        )
        if quarantine_needed:
            _quarantine_path(path)
            state = None
        return source_payload, payload, raw_item_ids, state, updated_at

    def _payload_to_state(
        self,
        payload: object,
        raw_item_ids: object | None = None,
        *,
        preserve_equivalent_raw_wrapper: bool = False,
    ) -> SessionState | None:
        original_payload = payload if isinstance(payload, AbstractMapping) and type(payload) is not dict else None
        if _session_payload_is_legacy_sequence(payload):
            if raw_item_ids is None:
                raw_item_ids = _snapshot_basket_item_ids(payload)
            if not _session_basket_item_ids_are_recoverable(raw_item_ids if raw_item_ids is not None else payload):
                return None
            return SessionState(
                basket_item_ids=_normalize_item_ids(raw_item_ids if raw_item_ids is not None else payload),
            )
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return None
        if raw_item_ids is None:
            raw_item_ids = _snapshot_basket_item_ids(payload.get("basket_item_ids", []))
        payload_item_ids = payload.get("basket_item_ids")
        # An exhausted generator as basket_item_ids is not a canonical empty
        # basket — unlike a tuple or list, a one-shot iterator cannot be
        # distinguished from one that was partially consumed before being
        # stored. Treat it as unrecoverable so callers quarantine the payload
        # rather than promoting an indeterminate generator as valid state.
        if (
            raw_item_ids == ()
            and payload_item_ids is not None
            and ContextBasket._is_one_shot_iterator(payload_item_ids)
        ):
            return None
        normalized_raw_item_ids: list[str] | None = None
        if raw_item_ids is not None:
            try:
                normalized_raw_item_ids = _normalize_item_ids(raw_item_ids)
            except Exception:
                normalized_raw_item_ids = None
        if (
            normalized_raw_item_ids is not None
            and payload_item_ids is not None
            and isinstance(payload_item_ids, AbstractIterable)
            and not isinstance(payload_item_ids, (str, bytes, bytearray, memoryview, AbstractMapping))
            and payload_item_ids != normalized_raw_item_ids
            # Only normalize in-place for non-plain-dict wrappers so that
            # raw-materialized generator values in plain dicts are preserved
            # for callers that need the pre-normalization shape.
            and (original_payload is not None or not isinstance(payload_item_ids, list))
        ):
            payload["basket_item_ids"] = (
                normalized_raw_item_ids
                if isinstance(payload_item_ids, (list, tuple, UserList))
                else raw_item_ids
            )
        if _session_payload_needs_audit_quarantine(payload, raw_item_ids):
            if original_payload is not None:
                canonical_snapshot = _session_canonical_payload_snapshot(payload, raw_item_ids)
                if canonical_snapshot is not None:
                    _sync_session_payload_mapping_wrapper(
                        original_payload,
                        canonical_snapshot,
                        preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
                    )
            return None
        recoverability_source = raw_item_ids if raw_item_ids is not None else payload.get("basket_item_ids", [])
        if not _session_basket_item_ids_are_recoverable(recoverability_source):
            if original_payload is not None:
                canonical_snapshot = _session_canonical_payload_snapshot(payload, raw_item_ids)
                if canonical_snapshot is not None:
                    _sync_session_payload_mapping_wrapper(
                        original_payload,
                        canonical_snapshot,
                        preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
                    )
            return None
        if "project_name" in payload:
            payload["project_name"] = _normalize_project_name(payload.get("project_name"))
        if "document_path" in payload:
            payload["document_path"] = _normalize_document_path(payload.get("document_path"))
        state = SessionState(
            project_name=_normalize_project_name(payload.get("project_name")),
            document_path=_normalize_document_path(payload.get("document_path")),
            basket_item_ids=(
                normalized_raw_item_ids
                if normalized_raw_item_ids is not None
                else _normalize_item_ids(payload.get("basket_item_ids", []))
            ),
        )
        _sync_session_payload_mapping_wrapper(
            original_payload,
            payload,
            preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
        )
        return state

    def load(self) -> SessionState:
        _reject_session_state_root_alias(self.state_root)
        _ensure_session_state_root(self.state_root)
        # Harden primary and backup paths before recovery logic runs so blocking
        # artifacts cannot participate in the state selection path.
        _quarantine_blocking_session_artifact_and_fsync(self.primary_path)
        _quarantine_blocking_session_artifact_and_fsync(self.backup_path)
        primary_source_payload = self._load_payload(self.primary_path)
        primary_raw_item_ids = _session_payload_raw_basket_item_ids(
            primary_source_payload,
            preserve_equivalent_raw_wrapper=True,
        )
        primary_payload = _materialize_session_payload(
            primary_source_payload,
            preserve_equivalent_raw_wrapper=True,
        )

        backup_source_payload = self._load_payload(self.backup_path)
        backup_raw_item_ids = _session_payload_raw_basket_item_ids(
            backup_source_payload,
            preserve_equivalent_raw_wrapper=True,
        )
        backup_payload = _materialize_session_payload(
            backup_source_payload,
            preserve_equivalent_raw_wrapper=True,
        )

        primary_state = self._payload_to_state(
            primary_payload,
            primary_raw_item_ids,
            preserve_equivalent_raw_wrapper=True,
        )
        backup_state = self._payload_to_state(
            backup_payload,
            backup_raw_item_ids,
            preserve_equivalent_raw_wrapper=True,
        )
        backup_recovered_state = None
        primary_recovered_state = None
        if backup_state is None and _session_recovered_backup_is_last_resort_recoverable(backup_payload, backup_raw_item_ids):
            backup_recovered_state = _session_recovered_backup_state(backup_payload, backup_raw_item_ids)
        if primary_state is None and _session_recovered_backup_is_last_resort_recoverable(primary_payload, primary_raw_item_ids):
            primary_recovered_state = _session_recovered_backup_state(primary_payload, primary_raw_item_ids)
        primary_updated_at = _normalize_updated_at(primary_payload.get("updated_at")) if isinstance(primary_payload, dict) else None
        backup_updated_at = (
            _normalize_updated_at(backup_payload.get("updated_at"))
            if isinstance(backup_payload, dict) and (backup_state is not None or backup_recovered_state is not None)
            else None
        )
        staged_entries = [
            (path, *self._load_candidate_state(path))
            for path in (
                *_session_staged_temp_paths(self.primary_path),
                *_session_staged_temp_paths(self.backup_path),
            )
        ]
        staged_conflict = False
        staged_state: SessionState | None = None
        staged_updated_at: str | None = None
        for path, _, _, _, candidate_state, candidate_updated_at in staged_entries:
            if _session_states_conflict(
                staged_state,
                staged_updated_at,
                candidate_state,
                candidate_updated_at,
            ):
                staged_conflict = True
            staged_state, staged_updated_at = _prefer_session_state_candidate(
                staged_state,
                staged_updated_at,
                candidate_state,
                candidate_updated_at,
            )
        if staged_conflict:
            for path, *_ in staged_entries:
                _quarantine_path(path)
            staged_state = None
            staged_updated_at = None

        def _sync_source_payload(
            source_payload: object | None,
            payload: dict[str, object],
            *,
            preserve_equivalent_raw_wrapper: bool = False,
            preserve_raw_basket_ids: bool = False,
        ) -> None:
            if isinstance(source_payload, AbstractMapping) and type(source_payload) is not dict:
                cleaned_payload = dict(payload)
                cleaned_payload.pop("recovered_from", None)
                _sync_session_payload_mapping_wrapper(
                    source_payload,
                    cleaned_payload,
                    preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
                    preserve_raw_basket_ids=preserve_raw_basket_ids,
                )

        def _metadata_only_backup_updated_at() -> str | None:
            if not isinstance(backup_payload, dict):
                return None
            if not _session_payload_can_preserve_metadata_with_empty_basket(backup_payload, backup_raw_item_ids):
                return None
            normalized_backup_updated_at = _normalize_updated_at(backup_payload.get("updated_at"))
            if not isinstance(backup_raw_item_ids, AbstractMapping):
                return normalized_backup_updated_at
            if not isinstance(primary_payload, dict):
                return None
            raw_primary_updated_at = primary_payload.get("updated_at")
            if isinstance(raw_primary_updated_at, str) and raw_primary_updated_at.strip():
                # Keep a clean primary timestamp authoritative. Mapping-shaped
                # backups may still donate a fallback timestamp when the
                # primary timestamp is simply missing or blank.
                return None
            return normalized_backup_updated_at

        def _clear_staged_session_artifacts() -> None:
            for path, *_ in staged_entries:
                _remove_session_temp_path_and_fsync(path)

        def _sync_staged_source_payloads(payload: dict[str, object]) -> None:
            for _, source_payload, *_ in staged_entries:
                _sync_source_payload(
                    source_payload,
                    payload,
                    preserve_equivalent_raw_wrapper=True,
                )

        if primary_state is not None and staged_state is not None and (
            staged_updated_at is not None
            and (primary_updated_at is None or staged_updated_at > primary_updated_at)
        ):
            backup_candidate_state, backup_candidate_updated_at = _prefer_session_state_candidate(
                backup_state,
                backup_updated_at,
                backup_recovered_state,
                backup_updated_at,
            )
            recovered_state, recovered_updated_at = _prefer_session_state_candidate(
                primary_state,
                primary_updated_at,
                backup_candidate_state,
                backup_candidate_updated_at,
            )
            recovered_state, recovered_updated_at = _prefer_session_state_candidate(
                recovered_state,
                recovered_updated_at,
                staged_state,
                staged_updated_at,
            )
            if recovered_state is not None:
                resolved_updated_at = recovered_updated_at or utc_now_iso()
                rewritten_payload = self._payload_from_state(recovered_state, updated_at=resolved_updated_at)
                self._write_payload(rewritten_payload)
                _sync_source_payload(primary_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
                _sync_source_payload(backup_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
                _sync_staged_source_payloads(rewritten_payload)
                _clear_staged_session_artifacts()
                return recovered_state
        if primary_state is None and staged_state is not None:
            backup_candidate_state, backup_candidate_updated_at = _prefer_session_state_candidate(
                backup_state,
                backup_updated_at,
                backup_recovered_state,
                backup_updated_at,
            )
            recovered_state, recovered_updated_at = _prefer_session_state_candidate(
                backup_candidate_state,
                backup_candidate_updated_at,
                staged_state,
                staged_updated_at,
            )
            if recovered_state is not None:
                resolved_updated_at = recovered_updated_at or utc_now_iso()
                rewritten_payload = self._payload_from_state(recovered_state, updated_at=resolved_updated_at)
                self._write_payload(rewritten_payload)
                _sync_source_payload(primary_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
                _sync_source_payload(backup_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
                _sync_staged_source_payloads(rewritten_payload)
                _clear_staged_session_artifacts()
                return recovered_state

        # When the backup is a recovery artifact (recovered_from) and the
        # primary has a clean non-empty basket, handle two sub-cases:
        #
        # Case A – baskets differ: the recovery artifact has stale basket
        # content.  Quarantine the backup and return the primary unchanged.
        #
        # Case B – baskets match but primary lacks metadata the backup fills:
        # merge backup metadata into primary state, keep the primary timestamp,
        # quarantine the backup, and stamp the primary with recovered_from.
        #
        # When primary already has all metadata and baskets match, the backup's
        # newer timestamp may still be authoritative — that path falls through
        # to the existing promotion branch below.
        if (
            primary_state is not None
            and isinstance(backup_payload, dict)
            and _session_recovered_from_source(backup_payload.get("recovered_from")) is not None
            and backup_recovered_state is not None
            and list(primary_state.basket_item_ids)
        ):
            primary_basket = list(primary_state.basket_item_ids)
            backup_basket = list(backup_recovered_state.basket_item_ids)
            primary_missing_meta = (
                primary_state.project_name is None or primary_state.document_path is None
            )
            backup_fills_meta = (
                backup_recovered_state.project_name is not None
                or backup_recovered_state.document_path is not None
            )
            if primary_basket != backup_basket:
                # Case A: stale recovery artifact — primary wins outright.
                _quarantine_path(self.backup_path)
                resolved_updated_at = primary_updated_at or utc_now_iso()
                rewritten_payload = self._payload_from_state(primary_state, updated_at=resolved_updated_at)
                self._write_payload(rewritten_payload)
                _sync_source_payload(primary_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
                _clear_staged_session_artifacts()
                return primary_state
            if primary_missing_meta and backup_fills_meta:
                # Case B: same basket, backup fills metadata primary lacks.
                merged_state = SessionState(
                    project_name=(
                        primary_state.project_name
                        if primary_state.project_name is not None
                        else backup_recovered_state.project_name
                    ),
                    document_path=(
                        primary_state.document_path
                        if primary_state.document_path is not None
                        else backup_recovered_state.document_path
                    ),
                    basket_item_ids=primary_basket,
                )
                _quarantine_path(self.backup_path)
                resolved_updated_at = primary_updated_at or utc_now_iso()
                rewritten_primary_payload = self._payload_from_state(
                    merged_state, updated_at=resolved_updated_at, recovered_from="backup"
                )
                rewritten_backup_payload = self._payload_from_state(merged_state, updated_at=resolved_updated_at)
                self._write_payload(rewritten_primary_payload)
                self._write_backup_payload(rewritten_backup_payload)
                _sync_source_payload(primary_source_payload, rewritten_primary_payload, preserve_equivalent_raw_wrapper=True)
                _clear_staged_session_artifacts()
                return merged_state

        primary_basket_is_authoritative_empty = (
            primary_raw_item_ids is not None
            and not _session_basket_item_ids_should_recover_from_backup(primary_raw_item_ids)
            and not list(primary_state.basket_item_ids if primary_state is not None else [])
            # An empty tuple basket collapses to [] like a recoverable empty
            # list, but is non-canonical. When the backup represents the same
            # session (same project + document) and has actual items, treat
            # the empty tuple as non-authoritative so the backup basket wins.
            and not (
                primary_state is not None
                and isinstance(primary_raw_item_ids, tuple)
                and not primary_raw_item_ids
                and backup_state is not None
                and list(backup_state.basket_item_ids)
                and primary_state.project_name == backup_state.project_name
                and primary_state.document_path == backup_state.document_path
            )
        )
        # When primary is a legacy sequence the basket items it carries are
        # authoritative (they were the only state the primary file could hold).
        # If the backup has richer metadata (project_name, document_path,
        # updated_at), merge: keep primary's basket, adopt backup's metadata.
        if (
            _session_payload_is_legacy_sequence(primary_source_payload)
            and primary_state is not None
            and backup_state is not None
        ):
            merged_state = SessionState(
                project_name=backup_state.project_name,
                document_path=backup_state.document_path,
                basket_item_ids=list(primary_state.basket_item_ids),
            )
            resolved_updated_at = backup_updated_at or utc_now_iso()
            rewritten_payload = self._payload_from_state(merged_state, updated_at=resolved_updated_at)
            self._write_payload(rewritten_payload)
            _sync_source_payload(primary_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
            _sync_source_payload(backup_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
            _clear_staged_session_artifacts()
            return merged_state

        if (
            primary_state is not None
            and backup_state is not None
            and backup_updated_at is not None
            and (primary_updated_at is None or backup_updated_at > primary_updated_at)
            and not primary_basket_is_authoritative_empty
        ):
            # When the primary had a non-canonical empty-tuple basket that was
            # treated as non-authoritative (same-session, backup has items),
            # quarantine the primary and stamp the rewrite as recovered.
            primary_had_empty_tuple = (
                isinstance(primary_raw_item_ids, tuple) and not primary_raw_item_ids
            )
            if primary_had_empty_tuple:
                _quarantine_path(self.primary_path)
                rewritten_primary_payload = self._payload_from_state(
                    backup_state, updated_at=backup_updated_at, recovered_from="backup"
                )
                rewritten_backup_payload = self._payload_from_state(backup_state, updated_at=backup_updated_at)
                self._write_payload(rewritten_primary_payload)
                self._write_backup_payload(rewritten_backup_payload)
                _sync_source_payload(primary_source_payload, rewritten_primary_payload, preserve_equivalent_raw_wrapper=True)
                _sync_source_payload(backup_source_payload, rewritten_backup_payload, preserve_equivalent_raw_wrapper=True)
                _clear_staged_session_artifacts()
                return backup_state
            rewritten_payload = self._payload_from_state(backup_state, updated_at=backup_updated_at)
            self._write_payload(rewritten_payload)
            _sync_source_payload(primary_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
            _sync_source_payload(backup_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
            _clear_staged_session_artifacts()
            return backup_state

        if (
            primary_state is not None
            and backup_state is None
            and backup_recovered_state is not None
            and backup_updated_at is not None
            and (primary_updated_at is None or backup_updated_at > primary_updated_at)
            and not primary_basket_is_authoritative_empty
        ):
            _quarantine_path(self.primary_path)
            rewritten_primary_payload = self._payload_from_state(
                backup_recovered_state,
                updated_at=backup_updated_at,
                recovered_from="backup",
            )
            rewritten_backup_payload = self._payload_from_state(
                backup_recovered_state,
                updated_at=backup_updated_at,
            )
            self._write_payload(rewritten_primary_payload)
            self._write_backup_payload(rewritten_backup_payload)
            _sync_source_payload(primary_source_payload, rewritten_primary_payload, preserve_equivalent_raw_wrapper=True)
            _sync_source_payload(backup_source_payload, rewritten_backup_payload, preserve_equivalent_raw_wrapper=True)
            _clear_staged_session_artifacts()
            return backup_recovered_state

        if primary_payload is not None and not (isinstance(primary_source_payload, tuple) and not primary_source_payload) and (
            _session_payload_needs_audit_quarantine(primary_payload, primary_raw_item_ids)
            or _session_updated_at_needs_audit_quarantine(primary_payload)
            or (
                # A dict payload whose basket_item_ids arrived as an empty
                # Python tuple is non-canonical (JSON never produces tuples).
                # Quarantine it so the rewrite path normalizes to a canonical
                # list. Only applies when no backup is available to confirm
                # the empty basket; a non-empty tuple has recoverable items
                # and must not be quarantined.
                # primary_state may be None here when the empty tuple was
                # snapshotted from an exhausted generator (_payload_to_state
                # returns None for that shape), so guard on isinstance instead.
                isinstance(primary_payload, dict)
                and backup_state is None
                and backup_recovered_state is None
                and primary_raw_item_ids == ()
            )
        ):
            _quarantine_path(self.primary_path)
        if backup_payload is not None and not (isinstance(backup_source_payload, tuple) and not backup_source_payload) and (
            # When the backup has a mapping-shaped basket and the primary also
            # has a mapping-shaped basket (neither side has recoverable basket
            # content), preserve the backup when it can still donate a useful
            # timestamp. Quarantine when _metadata_only_backup_updated_at
            # returns None (primary has a non-blank string timestamp that
            # supersedes the backup) or when the primary has a valid
            # non-mapping basket that is the authoritative basket source.
            (
                _session_payload_needs_audit_quarantine(backup_payload, backup_raw_item_ids)
                and not (
                    isinstance(backup_raw_item_ids, AbstractMapping)
                    and isinstance(primary_raw_item_ids, AbstractMapping)
                    and _metadata_only_backup_updated_at() is not None
                )
            )
            or _session_updated_at_needs_audit_quarantine(backup_payload)
            or (
                # An empty one-shot iterator as basket_item_ids is not a
                # canonical empty basket. _payload_to_state already returns
                # None for this shape (so backup_state is None), but the
                # backup file still holds the malformed payload and must be
                # quarantined so the rewrite path produces a clean artifact.
                backup_raw_item_ids == ()
                and isinstance(backup_payload, dict)
                and ContextBasket._is_one_shot_iterator(backup_payload.get("basket_item_ids"))
            )
        ):
            _quarantine_path(self.backup_path)

        if (
            primary_state is None
            and backup_state is None
            and _session_recovered_backup_is_last_resort_recoverable(backup_payload, backup_raw_item_ids)
        ):
            recovered_state = backup_recovered_state
            if recovered_state is None:
                recovered_state = SessionState()
            if _session_primary_metadata_can_donate(primary_payload) or _session_recovered_primary_metadata_can_donate(
                primary_payload,
            ):
                primary_project_name, primary_document_path = _session_recoverable_metadata_fields(
                    primary_payload,
                    allow_recovered_from=True,
                )
                if primary_project_name is not None or primary_document_path is not None:
                    recovered_state = SessionState(
                        project_name=primary_project_name if primary_project_name is not None else recovered_state.project_name,
                        document_path=primary_document_path if primary_document_path is not None else recovered_state.document_path,
                        basket_item_ids=list(recovered_state.basket_item_ids),
                    )
            backup_recovery_updated_at = backup_updated_at
            recovered_updated_at = _prefer_session_timestamp(
                primary_updated_at,
                backup_recovery_updated_at,
            )
            resolved_updated_at = recovered_updated_at or utc_now_iso()
            # Recovered payloads are audit artefacts, not sources of basket
            # data. Clean primary fields may still donate document/project
            # values into the rewritten state, and a recovered primary can
            # contribute those same fields during last-resort recovery.
            rewritten_primary_payload = self._payload_from_state(
                recovered_state,
                updated_at=resolved_updated_at,
                recovered_from="backup",
            )
            rewritten_backup_payload = self._payload_from_state(recovered_state, updated_at=resolved_updated_at)
            self._write_payload(rewritten_primary_payload)
            self._write_backup_payload(rewritten_backup_payload)
            _sync_source_payload(
                primary_source_payload,
                rewritten_primary_payload,
                preserve_equivalent_raw_wrapper=True,
            )
            _sync_source_payload(
                backup_source_payload,
                rewritten_backup_payload,
                preserve_equivalent_raw_wrapper=True,
            )
            _clear_staged_session_artifacts()
            return recovered_state

        if (
            primary_state is None
            and backup_state is None
            and backup_recovered_state is None
            and isinstance(backup_payload, dict)
            and _session_recovered_from_source(backup_payload.get("recovered_from")) is not None
        ):
            backup_project_name, backup_document_path = _session_recoverable_metadata_fields(
                backup_payload,
                allow_recovered_from=True,
            )
            if backup_project_name is not None or backup_document_path is not None:
                recovered_state = SessionState(
                    project_name=backup_project_name,
                    document_path=backup_document_path,
                    basket_item_ids=[],
                )
                backup_recovery_updated_at = _normalize_updated_at(backup_payload.get("updated_at"))
                resolved_updated_at = backup_recovery_updated_at or utc_now_iso()
                rewritten_primary_payload = self._payload_from_state(
                    recovered_state,
                    updated_at=resolved_updated_at,
                    recovered_from="backup",
                )
                rewritten_backup_payload = self._payload_from_state(recovered_state, updated_at=resolved_updated_at)
                self._write_payload(rewritten_primary_payload)
                self._write_backup_payload(rewritten_backup_payload)
                _sync_source_payload(
                    primary_source_payload,
                    rewritten_primary_payload,
                    preserve_equivalent_raw_wrapper=True,
                )
                _sync_source_payload(
                    backup_source_payload,
                    rewritten_backup_payload,
                    preserve_equivalent_raw_wrapper=True,
                )
                _clear_staged_session_artifacts()
                return recovered_state

        if primary_state is None and backup_state is None and primary_recovered_state is not None:
            if _session_primary_metadata_can_donate(backup_payload):
                backup_project_name, backup_document_path = _session_recoverable_metadata_fields(backup_payload)
                if backup_project_name is not None or backup_document_path is not None:
                    primary_recovered_state = SessionState(
                        project_name=primary_recovered_state.project_name
                        if primary_recovered_state.project_name is not None
                        else backup_project_name,
                        document_path=primary_recovered_state.document_path
                        if primary_recovered_state.document_path is not None
                        else backup_document_path,
                        basket_item_ids=list(primary_recovered_state.basket_item_ids),
                    )
            backup_recovery_updated_at = (
                _normalize_updated_at(backup_payload.get("updated_at"))
                if isinstance(backup_payload, dict)
                else None
            )
            resolved_updated_at = primary_updated_at or backup_recovery_updated_at or utc_now_iso()
            rewritten_payload = self._payload_from_state(primary_recovered_state, updated_at=resolved_updated_at)
            self._write_payload(rewritten_payload)
            _sync_source_payload(primary_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
            _sync_source_payload(backup_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
            _clear_staged_session_artifacts()
            return primary_recovered_state

        if primary_state is None and backup_state is None and _session_payload_can_preserve_metadata_with_empty_basket(
            primary_payload,
            primary_raw_item_ids,
        ):
            primary_project_name, primary_document_path = _session_recoverable_metadata_fields(primary_payload)
            if primary_project_name is not None or primary_document_path is not None:
                recovered_state = SessionState(
                    project_name=primary_project_name,
                    document_path=primary_document_path,
                    basket_item_ids=[],
                )
                backup_recovery_updated_at = _metadata_only_backup_updated_at()
                resolved_updated_at = _prefer_session_timestamp(primary_updated_at, backup_recovery_updated_at)
                resolved_updated_at = resolved_updated_at or utc_now_iso()
                rewritten_payload = self._payload_from_state(recovered_state, updated_at=resolved_updated_at)
                self._write_payload(rewritten_payload)
                _sync_source_payload(primary_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
                _sync_source_payload(backup_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
                _clear_staged_session_artifacts()
                return recovered_state

        if primary_state is None and backup_state is None and _session_payload_can_preserve_metadata_with_empty_basket(
            backup_payload,
            backup_raw_item_ids,
        ):
            backup_project_name, backup_document_path = _session_recoverable_metadata_fields(backup_payload)
            primary_project_name, primary_document_path = _session_recoverable_metadata_fields(primary_payload)
            recovered_state = SessionState(
                # Preserve primary metadata when both payloads can donate it.
                # The backup can still fill in fields that the primary lacks,
                # but it should not override recoverable primary values in a
                # last-resort empty-basket recovery.
                project_name=primary_project_name if primary_project_name is not None else backup_project_name,
                document_path=primary_document_path if primary_document_path is not None else backup_document_path,
                basket_item_ids=[],
            )
            backup_recovery_updated_at = _metadata_only_backup_updated_at()
            resolved_updated_at = _prefer_session_timestamp(primary_updated_at, backup_recovery_updated_at)
            resolved_updated_at = resolved_updated_at or utc_now_iso()
            # This path only rewrites metadata around an intentionally empty
            # basket, so keep the rewritten state canonical instead of
            # stamping recovery provenance that would force a future
            # quarantine.
            rewritten_payload = self._payload_from_state(recovered_state, updated_at=resolved_updated_at)
            self._write_payload(rewritten_payload)
            _sync_source_payload(
                primary_source_payload,
                rewritten_payload,
                preserve_equivalent_raw_wrapper=True,
            )
            _sync_source_payload(
                backup_source_payload,
                rewritten_payload,
                preserve_equivalent_raw_wrapper=True,
            )
            _clear_staged_session_artifacts()
            return recovered_state

        if (
            primary_state is None
            and backup_state is None
            and _session_primary_metadata_can_donate(primary_payload)
            and (
                _session_basket_item_ids_are_empty_non_list_iterable(primary_raw_item_ids)
                or _session_basket_item_ids_can_preserve_metadata_without_backup(primary_raw_item_ids)
            )
        ):
            primary_project_name, primary_document_path = _session_recoverable_metadata_fields(primary_payload)
            if primary_project_name is not None or primary_document_path is not None:
                recovered_state = SessionState(
                    project_name=primary_project_name,
                    document_path=primary_document_path,
                    basket_item_ids=[],
                )
                backup_recovery_updated_at = _metadata_only_backup_updated_at()
                resolved_updated_at = _prefer_session_timestamp(primary_updated_at, backup_recovery_updated_at)
                resolved_updated_at = resolved_updated_at or utc_now_iso()
                # Preserve the recoverable metadata even though the basket
                # shape itself still needs quarantine.
                rewritten_payload = self._payload_from_state(recovered_state, updated_at=resolved_updated_at)
                self._write_payload(rewritten_payload)
                _sync_source_payload(primary_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
                _sync_source_payload(backup_source_payload, rewritten_payload, preserve_equivalent_raw_wrapper=True)
                _clear_staged_session_artifacts()
                return recovered_state

        if primary_state is None and backup_state is None:
            state = SessionState()
            payload = self._payload_from_state(state)
            self._write_payload(payload)
            _sync_source_payload(primary_source_payload, payload, preserve_equivalent_raw_wrapper=True)
            _sync_source_payload(backup_source_payload, payload, preserve_equivalent_raw_wrapper=True)
            _clear_staged_session_artifacts()
            return state

        primary_needs_audit = isinstance(primary_payload, (dict, list)) and (
            _session_payload_needs_audit_quarantine(primary_payload, primary_raw_item_ids)
            or _session_updated_at_needs_audit_quarantine(primary_payload)
        )
        if primary_state is None and backup_state is not None:
            state = backup_state
            if _session_primary_metadata_can_donate(primary_payload):
                primary_project_name, primary_document_path = _session_recoverable_metadata_fields(primary_payload)
                if primary_project_name is not None or primary_document_path is not None:
                    # Preserve any recoverable primary metadata even when the
                    # backup contributes an intentionally empty basket.
                    state = SessionState(
                        project_name=primary_project_name if primary_project_name is not None else state.project_name,
                        document_path=primary_document_path if primary_document_path is not None else state.document_path,
                        basket_item_ids=list(state.basket_item_ids),
                    )
            elif _session_recovered_primary_metadata_can_donate(primary_payload) and (
                state.project_name is None or state.document_path is None
            ):
                primary_project_name, primary_document_path = _session_recoverable_metadata_fields(
                    primary_payload,
                    allow_recovered_from=True,
                )
                if primary_project_name is not None or primary_document_path is not None:
                    state = SessionState(
                        project_name=primary_project_name if primary_project_name is not None else state.project_name,
                        document_path=primary_document_path if primary_document_path is not None else state.document_path,
                        basket_item_ids=list(state.basket_item_ids),
                    )
            recovered_updated_at = None
            primary_recovery_updated_at = primary_updated_at
            if isinstance(backup_payload, dict):
                backup_recovery_updated_at = _normalize_updated_at(backup_payload.get("updated_at"))
                recovered_updated_at = _prefer_session_timestamp(primary_recovery_updated_at, backup_recovery_updated_at)
            else:
                recovered_updated_at = primary_recovery_updated_at
            resolved_updated_at = recovered_updated_at or utc_now_iso()
            normalized_payload = self._payload_from_state(state, updated_at=resolved_updated_at)
            # Stamp recovered_from when primary was loaded but failed validation
            # (corrupt/quarantined). If primary was never readable due to a probe
            # failure (RuntimeError), the file may still be intact — don't stamp
            # so a transient error doesn't permanently mark the session.
            # Detect quarantine by checking whether the primary path is absent
            # after load; probe failures leave the file in place but raise.
            try:
                primary_was_quarantined = not self.primary_path.is_symlink() and not self.primary_path.exists()
            except (OSError, RuntimeError):
                primary_was_quarantined = False
            if primary_was_quarantined and (
                state.basket_item_ids
                # Also stamp when the primary had parseable JSON with non-empty
                # but malformed basket content that forced quarantine, even if
                # the recovered basket is now empty. An unreadable primary (bad
                # JSON, directory at path) or one with an empty basket in the
                # wrong shape only stamps when backup salvaged a non-empty basket.
                or (primary_source_payload is not None and primary_raw_item_ids)
            ):
                # Stamp recovered_from when the primary was quarantined and the
                # session was rebuilt from backup state.
                primary_write_payload = self._payload_from_state(
                    state,
                    updated_at=resolved_updated_at,
                    recovered_from="backup",
                )
            else:
                primary_write_payload = normalized_payload
            self._write_payload(
                primary_write_payload
            )
            # Keep the backup copy canonical after recovery. A recovered backup
            # should not keep the recovery marker because the next load would
            # treat it as quarantinable local state.
            self._write_backup_payload(normalized_payload)
            _sync_source_payload(
                primary_source_payload,
                primary_write_payload,
                preserve_equivalent_raw_wrapper=True,
            )
            _sync_source_payload(
                backup_source_payload,
                normalized_payload,
                preserve_equivalent_raw_wrapper=True,
            )
            _clear_staged_session_artifacts()
            return state

        state = primary_state or SessionState()
        effective_backup_state = backup_state or backup_recovered_state
        recovered_from_backup = False
        if primary_state is not None and effective_backup_state is not None:
            merged_state = _merge_session_state(primary_state, effective_backup_state)
            if backup_state is None and backup_recovered_state is not None and merged_state != primary_state:
                recovered_from_backup = True
            state = merged_state
            if _session_basket_item_ids_should_recover_from_backup(primary_raw_item_ids):
                recovered_basket_state = SessionState(
                    project_name=state.project_name,
                    document_path=state.document_path,
                    basket_item_ids=list(effective_backup_state.basket_item_ids),
                )
                if backup_state is None and backup_recovered_state is not None and recovered_basket_state != state:
                    recovered_from_backup = True
                state = recovered_basket_state
            elif (
                backup_state is not None
                and isinstance(primary_source_payload, AbstractMapping)
                and type(primary_source_payload) is not dict
                and list(state.basket_item_ids) != list(backup_state.basket_item_ids)
                and sorted(state.basket_item_ids) == sorted(backup_state.basket_item_ids)
            ):
                # Primary is a UserDict-shaped wrapper whose basket_item_ids are a
                # permutation of the backup's canonical list. Canonicalize to the
                # backup's order so the on-disk payload and returned state agree.
                state = SessionState(
                    project_name=state.project_name,
                    document_path=state.document_path,
                    basket_item_ids=list(backup_state.basket_item_ids),
                )
        rewrite_updated_at = _prefer_session_timestamp(
            primary_updated_at,
            backup_updated_at if effective_backup_state is not None else None,
        )
        resolved_updated_at = rewrite_updated_at or utc_now_iso()
        normalized_payload = self._payload_from_state(state, updated_at=resolved_updated_at)
        recovered_primary_payload = self._payload_from_state(
            state,
            updated_at=resolved_updated_at,
            recovered_from="backup",
        )
        current_primary_payload = self._peek_json_payload(self.primary_path)
        current_backup_payload = self._peek_json_payload(self.backup_path)
        if recovered_from_backup:
            self._write_payload(recovered_primary_payload)
            self._write_backup_payload(normalized_payload)
            _sync_source_payload(
                primary_source_payload,
                recovered_primary_payload,
                preserve_equivalent_raw_wrapper=True,
            )
            _sync_source_payload(
                backup_source_payload,
                normalized_payload,
                preserve_equivalent_raw_wrapper=True,
            )
        else:
            if current_primary_payload != normalized_payload:
                self._write_payload(normalized_payload)
            if current_backup_payload != normalized_payload:
                self._write_backup_payload(normalized_payload)
            if isinstance(primary_payload, dict):
                _sync_source_payload(
                    primary_source_payload,
                    normalized_payload,
                    preserve_equivalent_raw_wrapper=True,
                    preserve_raw_basket_ids=True,
                )
            if isinstance(backup_payload, dict):
                _sync_source_payload(
                    backup_source_payload,
                    normalized_payload,
                    preserve_equivalent_raw_wrapper=True,
                    preserve_raw_basket_ids=True,
                )
            _sync_staged_source_payloads(normalized_payload)
        _clear_staged_session_artifacts()
        return state

    def save(self, state: SessionState) -> None:
        state.normalize()
        self._write_payload(self._payload_from_state(state))

    def clear(self) -> None:
        """Remove all persisted session artifacts including quarantine state.

        This method provides a deterministic reset so the engine workflow loop
        can transition between documents or projects without leaving stale
        session state on disk.  It mirrors the contract of
        :meth:`ContextBasketStore.clear`.
        """

        _reject_session_state_root_alias(self.state_root)
        # Remove primary and backup payloads.
        for path in (self.primary_path, self.backup_path):
            _remove_session_temp_path_and_fsync(path)
        # Remove staged temp artifacts for both primary and backup.
        for path in (self.primary_path, self.backup_path):
            for temp_path in _session_staged_temp_paths(path):
                _remove_session_temp_path_and_fsync(temp_path)
        # Remove quarantine artifacts.  The quarantine path generator appends
        # numeric suffixes, so we sweep the state root for any file whose name
        # contains the quarantine marker.
        for path in (self.primary_path, self.backup_path):
            _remove_session_corrupt_artifacts(self.state_root, path)
            for temp_path in _session_staged_temp_paths(path):
                _remove_session_corrupt_artifacts(self.state_root, temp_path)
        # Legacy/undotted staged temps are stale-quarantined under their full
        # name (``{temp}.stale.corrupt.json``) on save, so the family stem is the
        # temp name itself -- not the ``.suffix``-collapsed stem that
        # _remove_session_corrupt_artifacts derives. Sweep each family under the
        # full temp name so those stale quarantines (and numbered collisions) are
        # cleared instead of stranded for a later run to trip over.
        for path in (self.primary_path, self.backup_path):
            for temp_path in _session_noncanonical_staged_temp_paths(path):
                _clear_corrupt_artifact_family(temp_path.with_name(f"{temp_path.name}.corrupt.json"))
        # Remove audit log.
        audit_path = self.state_root / f"{self.__class__.__name__}_audit.jsonl"
        if _remove_session_clear_artifact(audit_path):
            _fsync_session_parent(audit_path)
        # A blocking alias on the audit-log path is quarantined to the sibling
        # ``{audit}.corrupt.jsonl`` family by ``audit._quarantine_blocking_audit_artifact``.
        # Removing only the live ``.jsonl`` would strand that quarantine, so
        # ``is_clean_state`` stays false after a reset that promises to remove
        # all persisted artifacts. Sweep the family from the producer's spelling.
        _clear_corrupt_artifact_family(_audit_corrupt_path(audit_path))
