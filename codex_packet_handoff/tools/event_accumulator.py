#!/usr/bin/env python3
from __future__ import annotations
import threading, time
from typing import Any, Dict
Json = Dict[str, Any]

class EventAccumulator:
    def __init__(self)->None:
        self._lock = threading.Lock()
        self._last: Dict[str,float] = {}
        self._buf: Dict[str,str] = {}

    def on_notification(self, msg: Json)->None:
        if msg.get("method") != "codex/event": return
        p = msg.get("params",{}) or {}
        cid = str(p.get("conversationId") or p.get("threadId") or "unknown")
        txt = self._extract(p)
        with self._lock:
            self._last[cid]=time.time()
            if txt:
                self._buf[cid]=self._buf.get(cid,"")+txt

    def clear(self, cid: str)->None:
        with self._lock:
            self._buf[str(cid)]=""

    def wait_for_idle_text(self, cid: str, idle_seconds: float, timeout: float)->str:
        cid=str(cid); start=time.time()
        while time.time()-start < timeout:
            with self._lock:
                last=self._last.get(cid,0.0)
            if last and (time.time()-last) >= idle_seconds:
                break
            time.sleep(0.05)
        with self._lock:
            return (self._buf.get(cid,"") or "").strip()

    def _extract(self, obj: Any)->str:
        texts=[]
        def walk(x: Any):
            if isinstance(x, dict):
                for k,v in x.items():
                    if k in ("text","delta","content") and isinstance(v,str) and v.strip():
                        texts.append(v)
                    walk(v)
            elif isinstance(x, list):
                for v in x: walk(v)
        walk(obj)
        return ("\n".join(texts)+"\n") if texts else ""
