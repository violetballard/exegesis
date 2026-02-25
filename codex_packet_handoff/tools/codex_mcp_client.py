#!/usr/bin/env python3
"""
Bare JSON-RPC stdio client for `codex mcp-server`, speaking MCP "tools" protocol.

Important: Codex MCP server exposes tools (not ad-hoc methods):
- tools/list  -> lists tools (expect: "codex" and "codex-reply")
- tools/call  -> call a tool

We keep a long-lived session by storing threadId returned by codex()/codex-reply().
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

Json = Dict[str, Any]


@dataclass
class ApprovalPolicy:
    # allow-all (as requested)
    allow_exec: bool = True
    allow_apply_patch: bool = True

    def approve_exec(self, command: str) -> bool:
        return self.allow_exec

    def approve_patch(self) -> bool:
        return self.allow_apply_patch


class CodexMcpClient:
    def __init__(
        self,
        approval: Optional[ApprovalPolicy] = None,
        on_notification: Optional[Callable[[Json], None]] = None,
        codex_cmd: str = "codex",
    ):
        self.proc = subprocess.Popen(
            [codex_cmd, "mcp-server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=os.environ.copy(),
        )
        assert self.proc.stdin and self.proc.stdout

        self._approval = approval or ApprovalPolicy()
        self._on_notification = on_notification

        self._next_id = 1
        self._pending: Dict[int, "queue.Queue[Json]"] = {}
        self._lock = threading.Lock()

        threading.Thread(target=self._read_loop, daemon=True).start()

        # MCP initialize handshake (best-effort). Some servers require this before tools/list/call.
        try:
            self.initialize()
        except Exception:
            # If the server doesn't require or doesn't implement initialize, we'll proceed anyway.
            pass

    def close(self) -> None:
        try:
            self.proc.terminate()
        except Exception:
            pass

    def call(self, method: str, params: Optional[Json] = None, timeout: float = 180.0) -> Json:
        import queue

        with self._lock:
            req_id = self._next_id
            self._next_id += 1
            q: "queue.Queue[Json]" = queue.Queue(maxsize=1)
            self._pending[req_id] = q

        self._send({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}})

        try:
            resp = q.get(timeout=timeout)
        finally:
            with self._lock:
                self._pending.pop(req_id, None)

        if "error" in resp:
            raise RuntimeError(resp["error"])
        return resp["result"]

    # ---- MCP core ----

    def initialize(self) -> Json:
        # Minimal initialize payload; spec allows capability negotiation.
        return self.call(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "codex_packet_handoff", "version": "0.1"},
            },
            timeout=30.0,
        )

    def tools_list(self) -> Json:
        return self.call("tools/list", {}, timeout=30.0)

    def tools_call(self, name: str, arguments: Json, timeout: float = 180.0) -> Json:
        return self.call("tools/call", {"name": name, "arguments": arguments}, timeout=timeout)

    # ---- Codex tools ----

    def codex(self, prompt: str, cwd: Optional[str], sandbox: str, approval_policy: str, model: str) -> str:
        """
        Start a conversation. Returns threadId.
        """
        args: Json = {"prompt": prompt, "sandbox": sandbox, "approvalPolicy": approval_policy, "model": model}
        if cwd:
            args["cwd"] = cwd
        result = self.tools_call("codex", args, timeout=600.0)
        return _extract_thread_id(result)

    def codex_reply(self, thread_id: str, prompt: str) -> str:
        """
        Continue a conversation. Returns threadId (same or updated).
        """
        result = self.tools_call("codex-reply", {"threadId": thread_id, "prompt": prompt}, timeout=600.0)
        return _extract_thread_id(result)

    # ---- internal plumbing ----

    def _send(self, msg: Json) -> None:
        self.proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()

    def _read_loop(self) -> None:
        while True:
            line = self.proc.stdout.readline()
            if not line:
                return
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except Exception:
                continue

            # response
            if "id" in msg and ("result" in msg or "error" in msg) and "method" not in msg:
                req_id = msg["id"]
                with self._lock:
                    q = self._pending.get(req_id)
                if q:
                    q.put(msg)
                continue

            # notification
            if "method" in msg and "id" not in msg:
                if self._on_notification:
                    self._on_notification(msg)
                continue

            # server->client request: approvals
            if "method" in msg and "id" in msg:
                self._handle_server_request(msg)

    def _handle_server_request(self, msg: Json) -> None:
        method = msg.get("method")
        req_id = msg.get("id")
        params = msg.get("params", {}) or {}

        decision = "deny"
        if method == "execCommandApproval":
            decision = "allow" if self._approval.approve_exec(str(params.get("command", ""))) else "deny"
        elif method == "applyPatchApproval":
            decision = "allow" if self._approval.approve_patch() else "deny"

        self._send({"jsonrpc": "2.0", "id": req_id, "result": {"decision": decision}})


def _extract_thread_id(result: Json) -> str:
    """
    Tool result shape can vary; we try common places:
    - result["threadId"]
    - result["content"][0]["json"]["threadId"]
    - result["content"][0]["text"] containing threadId JSON
    """
    if isinstance(result, dict) and isinstance(result.get("threadId"), str):
        return result["threadId"]

    content = result.get("content") if isinstance(result, dict) else None
    if isinstance(content, list) and content:
        first = content[0]
        if isinstance(first, dict):
            j = first.get("json")
            if isinstance(j, dict) and isinstance(j.get("threadId"), str):
                return j["threadId"]
            # Sometimes tool returns text that includes a JSON object
            t = first.get("text")
            if isinstance(t, str):
                # naive parse: look for "threadId":"..."
                m = __import__("re").search(r'"threadId"\s*:\s*"([^"]+)"', t)
                if m:
                    return m.group(1)

    raise RuntimeError(f"Could not extract threadId from tool result: {result}")
