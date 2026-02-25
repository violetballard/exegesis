#!/usr/bin/env python3
"""
Event accumulator for Codex MCP notifications.

Captures `codex/event` notifications and extracts text-like fields recursively.
Treats "idle for idle_seconds" as end of a turn.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict

Json = Dict[str, Any]

class EventAccumulator:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_event_ts: Dict[str, float] = {}
        self._text_buf: Dict[str, str] = {}

    def on_notification(self, msg: Json) -> None:
        if msg.get("method") != "codex/event":
            return
        params = msg.get("params", {}) or {}
        cid = params.get("conversationId") or params.get("threadId") or "unknown"
        extracted = self._extract_any_text(params)
        with self._lock:
            self._last_event_ts[str(cid)] = time.time()
            if extracted:
                self._text_buf[str(cid)] = self._text_buf.get(str(cid), "") + extracted

    def clear(self, conversation_id: str) -> None:
        with self._lock:
            self._text_buf[str(conversation_id)] = ""

    def wait_for_idle_text(self, conversation_id: str, idle_seconds: float, timeout: float) -> str:
        start = time.time()
        cid = str(conversation_id)
        while time.time() - start < timeout:
            with self._lock:
                last = self._last_event_ts.get(cid, 0.0)
            if last and (time.time() - last) >= idle_seconds:
                break
            time.sleep(0.05)
        with self._lock:
            return (self._text_buf.get(cid, "") or "").strip()

    def _extract_any_text(self, obj: Any) -> str:
        texts = []
        def walk(x: Any) -> None:
            if isinstance(x, dict):
                for k,v in x.items():
                    if k in ("text","delta","content") and isinstance(v,str) and v.strip():
                        texts.append(v)
                    walk(v)
            elif isinstance(x, list):
                for v in x: walk(v)
        walk(obj)
        return ("\n".join(texts) + "\n") if texts else ""
