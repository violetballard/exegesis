from __future__ import annotations

from collections import OrderedDict, UserString
from collections.abc import Iterable as AbstractIterable
from collections.abc import Mapping as AbstractMapping
from collections.abc import Set as AbstractSet
from collections.abc import ItemsView as AbstractItemsView
from collections.abc import KeysView as AbstractKeysView
from collections.abc import ValuesView as AbstractValuesView
import json
import os
import math
import unicodedata
from dataclasses import dataclass, field
import weakref


def _safe_repr(value: object) -> str:
    """Return ``repr(value)`` without letting a bad ``__repr__`` break recovery."""

    try:
        rendered = repr(value)
    except Exception:
        return f"<{type(value).__name__}>"
    return rendered if isinstance(rendered, str) else f"<{type(value).__name__}>"


def _safe_json_key(value: object) -> str:
    """Return a stable string key for JSON object snapshots."""

    if isinstance(value, str):
        return value
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(value) if math.isfinite(value) else _safe_repr(value)
    return _safe_repr(value)


def _has_unsafe_item_id_codepoint(value: str) -> bool:
    return any(unicodedata.category(char) in {"Cc", "Cf", "Cs", "Zl", "Zp"} for char in value)


def _safe_json_mapping_key(value: object, seen_keys: dict[str, int], used_keys: set[str]) -> str:
    """Return a JSON key without collapsing distinct malformed payload keys."""

    key = _safe_json_key(value)
    duplicate_count = seen_keys.get(key, 0)
    seen_keys[key] = duplicate_count + 1
    safe_key = key if duplicate_count == 0 else f"{key}#duplicate-{duplicate_count + 1}"
    while safe_key in used_keys:
        duplicate_count += 1
        safe_key = f"{key}#duplicate-{duplicate_count + 1}"
    used_keys.add(safe_key)
    return safe_key


def _safe_json_value(
    value: object,
    _seen: set[int] | None = None,
    _one_shot_snapshots: OrderedDict[int, tuple[object, list[object]]] | None = None,
) -> object:
    """Return a JSON-serializable snapshot of *value*.

    Corrupt-artifact writers should never drop an artifact just because the
    malformed payload contains a value that the standard JSON encoder cannot
    handle. Preserve the shape as much as possible and fall back to stable
    string markers for unsupported objects.
    """

    if _seen is None:
        _seen = set()
    if _one_shot_snapshots is None:
        _one_shot_snapshots = OrderedDict()

    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, UserString):
        return str(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else _safe_repr(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        try:
            raw_bytes = bytes(value)
        except Exception:
            return _safe_repr(value)
        return {"type": type(value).__name__, "hex": raw_bytes.hex()}
    if isinstance(value, os.PathLike):
        try:
            value = os.fspath(value)
        except Exception:
            return _safe_repr(value)
        if isinstance(value, str):
            return value
        return _safe_repr(value)
    if isinstance(value, AbstractMapping):
        value_id = id(value)
        if value_id in _seen:
            return _safe_repr(value)
        _seen.add(value_id)
        try:
            items = value.items() if isinstance(value, dict) else dict(value).items()
        except Exception:
            _seen.discard(value_id)
            return _safe_repr(value)
        try:
            safe_mapping: dict[object, object] = {}
            seen_keys: dict[str, int] = {}
            used_keys: set[str] = set()
            try:
                for key, item in items:
                    safe_key = _safe_json_mapping_key(key, seen_keys, used_keys)
                    safe_mapping[safe_key] = _safe_json_value(item, _seen, _one_shot_snapshots)
                return safe_mapping
            except Exception:
                return _safe_repr(value)
        finally:
            _seen.discard(value_id)
    if isinstance(value, AbstractSet):
        value_id = id(value)
        if value_id in _seen:
            return _safe_repr(value)
        _seen.add(value_id)
        try:
            ordered_values = sorted(value, key=lambda item: (type(item).__name__, _safe_repr(item)))
        except Exception:
            try:
                ordered_values = list(value)
                ordered_values.sort(key=lambda item: (type(item).__name__, _safe_repr(item)))
            except Exception:
                _seen.discard(value_id)
                return _safe_repr(value)
        try:
            return [_safe_json_value(item, _seen, _one_shot_snapshots) for item in ordered_values]
        finally:
            _seen.discard(value_id)
    if isinstance(value, AbstractIterable) and not isinstance(value, (bytes, bytearray, memoryview)):
        value_id = id(value)
        if value_id in _seen:
            return _safe_repr(value)
        _seen.add(value_id)
        try:
            if ContextBasket._is_one_shot_iterator(value):
                cached_entry = _one_shot_snapshots.get(value_id)
                if cached_entry is not None:
                    cached_value, cached_items = cached_entry
                    if cached_value is value:
                        _one_shot_snapshots.move_to_end(value_id)
                        return [
                            _safe_json_value(item, _seen, _one_shot_snapshots)
                            for item in cached_items
                        ]
                cached_items = list(value)
                _one_shot_snapshots[value_id] = (value, cached_items)
                _one_shot_snapshots.move_to_end(value_id)
                if len(_one_shot_snapshots) > _BASKET_ITEM_ID_CACHE_LIMIT:
                    _one_shot_snapshots.popitem(last=False)
            else:
                cached_items = list(value)
            return [
                _safe_json_value(item, _seen, _one_shot_snapshots)
                for item in cached_items
            ]
        except Exception:
            _seen.discard(value_id)
            return _safe_repr(value)
        finally:
            _seen.discard(value_id)
    return _safe_repr(value)


def _canonical_json_dumps(payload: object) -> str:
    """Serialize state through the recovery-safe JSON normalizer."""

    return json.dumps(_safe_json_value(payload), allow_nan=False, indent=2, sort_keys=True) + "\n"


def _has_non_finite_float(value: object, _seen: set[int] | None = None) -> bool:
    """Return ``True`` when a payload contains a JSON-unsafe float value."""

    if isinstance(value, float):
        return not math.isfinite(value)
    if value is None or isinstance(value, (str, bool, int, bytes, bytearray, memoryview)):
        return False
    if _seen is None:
        _seen = set()
    if isinstance(value, AbstractMapping):
        value_id = id(value)
        if value_id in _seen:
            return False
        _seen.add(value_id)
        try:
            items = value.items() if isinstance(value, dict) else dict(value).items()
            return any(_has_non_finite_float(key, _seen) or _has_non_finite_float(item, _seen) for key, item in items)
        except Exception:
            return False
        finally:
            _seen.discard(value_id)
    if isinstance(value, AbstractIterable):
        value_id = id(value)
        if value_id in _seen:
            return False
        if ContextBasket._is_one_shot_iterator(value):
            return True
        _seen.add(value_id)
        try:
            return any(_has_non_finite_float(item, _seen) for item in value)
        except Exception:
            return False
        finally:
            _seen.discard(value_id)
    return False


def _payload_has_non_plain_json_shapes(value: object, _seen: set[int] | None = None) -> bool:
    """Return ``True`` when *value* still contains non-plain JSON container shapes.

    This is the single source of truth shared by the vault, basket, session, and
    context-set stores. Each store exposes a thin prefixed wrapper that delegates
    here so the "vault parity" classification cannot drift between modules.

    Recursion into containers is guarded by ``_seen`` (mirroring
    :func:`_has_non_finite_float`) so a self-referential dict/list in malformed
    in-memory state is classified safely instead of raising ``RecursionError``.
    """

    if isinstance(value, float):
        # A ``float`` subclass round-trips through canonical JSON as a plain
        # ``float``, leaving the in-memory wrapper divergent from disk; flag it
        # alongside the non-finite floats that JSON cannot represent at all.
        if type(value) is not float:
            return True
        return not math.isfinite(value)
    if value is None or isinstance(value, bool):
        return False
    if isinstance(value, (str, int)):
        # ``str``/``int`` subclasses (e.g. an ``IntEnum``) serialize as their
        # plain base type, so a wrapper retaining the subclass diverges from
        # disk -- the same divergence tuples and container subclasses trigger.
        return type(value) not in (str, int)
    if isinstance(value, dict):
        if type(value) is not dict:
            return True
        value_id = id(value)
        if _seen is None:
            _seen = set()
        if value_id in _seen:
            # A self-referential container is itself a plain ``dict``/``list``;
            # the cycle adds no new non-plain shape, so stop the descent here.
            return False
        _seen.add(value_id)
        try:
            return any(
                # A ``str`` subclass key serializes as its plain ``str`` base, so a
                # wrapper retaining the subclass key diverges from disk -- flag it the
                # same way ``str`` subclass *values* are flagged above.
                type(key) is not str or _payload_has_non_plain_json_shapes(item, _seen)
                for key, item in value.items()
            )
        finally:
            _seen.discard(value_id)
    if isinstance(value, list):
        if type(value) is not list:
            return True
        value_id = id(value)
        if _seen is None:
            _seen = set()
        if value_id in _seen:
            return False
        _seen.add(value_id)
        try:
            return any(_payload_has_non_plain_json_shapes(item, _seen) for item in value)
        finally:
            _seen.discard(value_id)
    if isinstance(value, tuple):
        # A tuple is never a plain ``json.loads`` result: it round-trips through
        # canonical JSON as a list, leaving the in-memory wrapper divergent from
        # disk. Flag it as a non-plain shape so marker reconciliation normalizes it.
        return True
    if isinstance(value, os.PathLike):
        # ``_safe_json_value`` normalizes an ``os.PathLike`` (e.g. a
        # ``pathlib.Path``) to its ``os.fspath`` string, so the canonical JSON
        # form on disk is a plain ``str`` while the in-memory wrapper keeps the
        # path object. Flag it the same way ``str`` subclasses and tuples are
        # flagged above so marker reconciliation normalizes it. ``str``/``bytes``
        # are not ``os.PathLike``, so the earlier scalar branches still win.
        return True
    # Anything reaching here is neither a JSON-plain scalar (``None``/``bool``/
    # plain ``str``/plain ``int``/finite plain ``float``) nor a plain ``dict``/
    # ``list``. ``_safe_json_value`` normalizes every such object before it hits
    # disk -- mappings become plain ``dict``s, sets/iterables become ``list``s,
    # and any other opaque object (e.g. ``complex``, ``datetime``, a custom
    # instance) is stringified via ``_safe_repr``. In all cases the in-memory
    # wrapper diverges from the canonical JSON form, so flag it. Returning ``True``
    # closes the gap where opaque non-iterable objects were previously treated as
    # plain and skipped recovery-marker reconciliation.
    return True


def _payload_as_plain_dict(payload: object) -> dict[str, object] | None:
    """Return *payload* as a plain ``dict`` when it is mapping-like.

    This is the single source of truth shared by the vault, basket, session, and
    context-set stores. Each store imports it so the snapshot-vs-canonical
    comparison cannot drift between modules. A genuine ``dict`` is returned by
    identity so callers can detect "already plain" via ``is``; any other mapping
    is materialized into a plain ``dict`` (returning ``None`` if that conversion
    raises), and non-mappings yield ``None``.
    """

    if type(payload) is dict:
        return payload
    if isinstance(payload, AbstractMapping):
        try:
            return dict(payload)
        except Exception:
            return None
    return None


def _mapping_wrapper_exposes_non_plain_json_shape(original_payload: object) -> bool:
    """Return ``True`` when a live mapping wrapper exposes a non-plain JSON shape.

    The vault, basket, session, and context-set ``_sync_*_payload_mapping_wrapper``
    paths share this guard to decide whether a wrapper whose plain-dict snapshot
    already equals the canonical payload may still skip reconciliation. It iterates
    *original_payload* directly -- the live wrapper view rather than a materialized
    snapshot -- so a wrapper hiding a non-plain shape behind a divergent
    ``__iter__``/``values`` view is normalized, not skipped. The two clauses mirror
    the dict branch of :func:`_payload_has_non_plain_json_shapes` (non-``str`` keys
    serialize as their plain ``str`` base; values are classified recursively), so
    the guard cannot drift from the shared classifier between modules.

    Exceptions raised while iterating the wrapper are intentionally left to
    propagate: every caller evaluates this inside a ``try``/``except`` that falls
    through to an authoritative ``clear()``/``update()`` sync, so a wrapper that
    cannot be iterated is reconciled rather than silently preserved.
    """

    return any(type(key) is not str for key in original_payload) or any(  # type: ignore[union-attr]
        _payload_has_non_plain_json_shapes(item)
        for item in original_payload.values()  # type: ignore[union-attr]
    )


class _BasketSnapshotList(list):  # type: ignore[type-arg]
    """Marker list subclass for snapshots materialized from one-shot iterators.

    Instances are identified by ``_is_one_shot_basket_id_snapshot`` without
    relying on WeakKeyDictionary identity checks that break when the source
    generator is garbage-collected after materialization.
    """


_BASKET_ITEM_ID_SNAPSHOTS: weakref.WeakKeyDictionary[object, list[object]] = weakref.WeakKeyDictionary()
_BASKET_ITEM_ID_SNAPSHOT_IDS: OrderedDict[int, tuple[object, list[object]]] = OrderedDict()
_BASKET_ITEM_ID_CACHE_LIMIT = 1024


def _snapshot_one_shot_item_id_values(raw_item_ids: object) -> list[object] | None:
    """Return a stable snapshot for one-shot basket iterables."""

    if not ContextBasket._is_one_shot_iterator(raw_item_ids):
        return None
    try:
        cached_values = _BASKET_ITEM_ID_SNAPSHOTS[raw_item_ids]
    except (KeyError, TypeError):
        payload_id = id(raw_item_ids)
        cached_entry = _BASKET_ITEM_ID_SNAPSHOT_IDS.get(payload_id)
        if cached_entry is not None:
            cached_payload, cached_values = cached_entry
            if cached_payload is raw_item_ids:
                _BASKET_ITEM_ID_SNAPSHOT_IDS.move_to_end(payload_id)
                return cached_values
        try:
            cached_values = _BasketSnapshotList(raw_item_ids)
        except Exception:
            return None
        try:
            _BASKET_ITEM_ID_SNAPSHOTS[raw_item_ids] = cached_values
        except TypeError:
            _BASKET_ITEM_ID_SNAPSHOT_IDS[payload_id] = (raw_item_ids, cached_values)
            _BASKET_ITEM_ID_SNAPSHOT_IDS.move_to_end(payload_id)
            if len(_BASKET_ITEM_ID_SNAPSHOT_IDS) > _BASKET_ITEM_ID_CACHE_LIMIT:
                _BASKET_ITEM_ID_SNAPSHOT_IDS.popitem(last=False)
    return cached_values


def _is_one_shot_basket_id_snapshot(value: object) -> bool:
    """Return ``True`` when *value* is a cached snapshot list from a one-shot iterator.

    Uses the ``_BasketSnapshotList`` marker subclass for GC-safe detection: the
    WeakKeyDictionary entry for the source generator is evicted when the generator
    is garbage-collected after materialization, but the subclass identity survives.
    """
    if isinstance(value, _BasketSnapshotList):
        return True
    if not isinstance(value, list):
        return False
    # Legacy fallback for snapshots created before this subclass was introduced.
    try:
        for cached_snapshot in _BASKET_ITEM_ID_SNAPSHOTS.values():
            if cached_snapshot is value:
                return True
    except Exception:
        pass
    for _, (_, cached_list) in _BASKET_ITEM_ID_SNAPSHOT_IDS.items():
        if cached_list is value:
            return True
    return False


@dataclass
class ContextBasket:
    item_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.normalize()

    @staticmethod
    def _is_one_shot_iterator(raw_values: object) -> bool:
        """Return ``True`` when *raw_values* is a one-shot iterator."""

        if not hasattr(raw_values, "__next__"):
            return False
        try:
            return iter(raw_values) is raw_values
        except TypeError:
            return False

    @staticmethod
    def _ordered_item_id_values(raw_item_ids: object) -> list[object] | None:
        if isinstance(raw_item_ids, (AbstractKeysView, AbstractItemsView, AbstractValuesView)):
            # Mapping views expose dictionary structure, not an ordered basket
            # payload. Treat them as malformed so we never persist raw keys as
            # recoverable item ids.
            return None
        if isinstance(raw_item_ids, AbstractSet):
            try:
                return sorted(
                    raw_item_ids,
                    key=lambda value: (ContextBasket._normalize_item_id(value), type(value).__name__, _safe_repr(value)),
                )
            except Exception:
                # Malformed iterables should fail closed so callers can
                # quarantine them instead of crashing during materialization.
                return None
        if ContextBasket._is_one_shot_iterator(raw_item_ids):
            return _snapshot_one_shot_item_id_values(raw_item_ids)
        if isinstance(raw_item_ids, AbstractIterable) and not isinstance(
            raw_item_ids,
            # Byte-buffer inputs should behave like scalar garbage, not like
            # iterable baskets whose integer byte values would normalize into
            # bogus item ids.
            (str, bytes, bytearray, memoryview, AbstractMapping),
        ):
            # Deterministic iterable inputs such as ``range`` should normalize
            # the same way as lists and tuples, but mappings and string-like
            # payloads still need to stay scalar.
            try:
                return list(raw_item_ids)
            except Exception:
                return None
        return None

    @staticmethod
    def _normalize_item_id(item_id: object) -> str:
        if not isinstance(item_id, str):
            if isinstance(item_id, os.PathLike):
                try:
                    item_id = os.fspath(item_id)
                except Exception:
                    return ""
                if not isinstance(item_id, str):
                    return ""
                candidate = item_id.strip()
                if _has_unsafe_item_id_codepoint(candidate):
                    return ""
                return candidate
            if isinstance(item_id, bool):
                return ""
            if isinstance(item_id, int):
                return str(item_id).strip()
            if isinstance(item_id, float):
                if not math.isfinite(item_id):
                    return ""
                return str(item_id).strip()
            return ""
        candidate = item_id.strip()
        if _has_unsafe_item_id_codepoint(candidate):
            return ""
        return candidate

    def add(self, item_id: object) -> None:
        self.normalize()
        normalized = self._normalize_item_id(item_id)
        if not normalized:
            return
        if normalized not in self.item_ids:
            self.item_ids.append(normalized)

    def remove(self, item_id: object) -> None:
        self.normalize()
        normalized = self._normalize_item_id(item_id)
        if not normalized:
            return
        self.item_ids = [x for x in self.item_ids if x != normalized]

    def normalize(self) -> None:
        raw_item_ids = self.item_ids
        raw_values = self._ordered_item_id_values(raw_item_ids)
        if raw_values is None:
            # Unsupported shapes should be treated as a single scalar rather
            # than iterated, so mappings do not leak their keys into basket
            # state.
            raw_values = [raw_item_ids]
        deduped: list[str] = []
        seen: set[str] = set()
        for raw in raw_values:
            item = self._normalize_item_id(raw)
            if not item or item in seen:
                continue
            deduped.append(item)
            seen.add(item)
        self.item_ids = deduped

    def __repr__(self) -> str:  # pragma: no cover - trivial helper
        """Return a concise representation for debugging.

        The default dataclass ``repr`` is verbose and includes the full list of
        item ids. For logs during engine runs we prefer a shorter form that
        shows only the count and first few items.
        """
        preview = ", ".join(self.item_ids[:3])
        if len(self.item_ids) > 3:
            preview += ", …"
        return f"ContextBasket(count={len(self.item_ids)}, ids=[{preview}])"
