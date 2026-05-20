#!/usr/bin/env python3
"""
codex_mcp_client.py

Bare JSON-RPC over stdio client for `codex mcp-server`, using MCP tools protocol:
- initialize
- tools/list
- tools/call

We expect Codex to expose tools:
- codex
- codex-reply

We return (threadId, content) from tool calls; content is pulled from structuredContent.content when present.
"""

from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

Json = Dict[str, Any]


@dataclass
class ApprovalPolicy:
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
        codex_args: Optional[List[str]] = None,
    ):
        launch_cmd = [codex_cmd, *(codex_args or []), "mcp-server"]
        self.proc = subprocess.Popen(
            launch_cmd,
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
        self._stderr_tail: deque[str] = deque(maxlen=20)

        threading.Thread(target=self._read_loop, daemon=True).start()
        threading.Thread(target=self._read_stderr_loop, daemon=True).start()

        # Best-effort initialize (some servers require it)
        try:
            self.initialize()
        except Exception:
            pass

    def close(self) -> None:
        try:
            self.proc.terminate()
        except Exception:
            pass

    def call(self, method: str, params: Optional[Json] = None, timeout: float = 180.0) -> Json:
        with self._lock:
            req_id = self._next_id
            self._next_id += 1
            q: "queue.Queue[Json]" = queue.Queue(maxsize=1)
            self._pending[req_id] = q

        self._send({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}}, method=method)

        try:
            resp = q.get(timeout=timeout)
        except queue.Empty as exc:
            raise TimeoutError(self._format_process_error(f"{method} timed out after {timeout:.0f}s")) from exc
        finally:
            with self._lock:
                self._pending.pop(req_id, None)

        if "error" in resp:
            raise RuntimeError(self._format_process_error(f"{method} returned error: {resp['error']}"))
        return resp["result"]

    # MCP core
    def initialize(self) -> Json:
        return self.call(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "packet_garden", "version": "0.2"},
            },
            timeout=30.0,
        )

    def tools_call(self, name: str, arguments: Json, timeout: float = 600.0) -> Json:
        return self.call("tools/call", {"name": name, "arguments": arguments}, timeout=timeout)

    # Codex tools
    def codex(
        self,
        prompt: str,
        cwd: Optional[str],
        sandbox: str,
        approval_policy: str,
        model: str,
        timeout: float = 600.0,
    ) -> Tuple[str, str]:
        args: Json = {"prompt": prompt, "sandbox": sandbox, "approvalPolicy": approval_policy}
        if model:
            args["model"] = model
        if cwd:
            args["cwd"] = cwd
        result = self.tools_call("codex", args, timeout=timeout)
        return _extract_thread_id(result), _extract_content(result)

    def codex_reply(self, thread_id: str, prompt: str, timeout: float = 600.0) -> Tuple[str, str]:
        result = self.tools_call("codex-reply", {"threadId": thread_id, "prompt": prompt}, timeout=timeout)
        return _extract_thread_id(result), _extract_content(result)

    # internal plumbing
    def _send(self, msg: Json, *, method: str = "request") -> None:
        try:
            self.proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n")
            self.proc.stdin.flush()
        except Exception as exc:
            raise RuntimeError(self._format_process_error(f"failed to send {method}: {exc}")) from exc

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

            # server->client request (approvals)
            if "method" in msg and "id" in msg:
                self._handle_server_request(msg)

    def _read_stderr_loop(self) -> None:
        if not self.proc.stderr:
            return
        while True:
            line = self.proc.stderr.readline()
            if not line:
                return
            text = line.strip()
            if text:
                self._stderr_tail.append(text)

    def _handle_server_request(self, msg: Json) -> None:
        method = msg.get("method")
        req_id = msg.get("id")
        params = msg.get("params", {}) or {}

        decision = "denied"
        if method == "execCommandApproval":
            decision = "approved" if self._approval.approve_exec(str(params.get("command", ""))) else "denied"
        elif method == "applyPatchApproval":
            decision = "approved" if self._approval.approve_patch() else "denied"

        self._send({"jsonrpc": "2.0", "id": req_id, "result": {"decision": decision}})

    def _format_process_error(self, message: str) -> str:
        stderr_tail = " | ".join(self._stderr_tail)
        if self.proc.poll() is not None:
            detail = f"process exited rc={self.proc.returncode}"
            if stderr_tail:
                detail += f"; stderr_tail={stderr_tail}"
            return f"{message}; {detail}"
        if stderr_tail:
            return f"{message}; stderr_tail={stderr_tail}"
        return message


def _extract_thread_id(result: Json) -> str:
    if isinstance(result, dict):
        sc = result.get("structuredContent")
        if isinstance(sc, dict) and isinstance(sc.get("threadId"), str):
            return sc["threadId"]
        if isinstance(result.get("threadId"), str):
            return result["threadId"]
    raise RuntimeError(f"Could not extract threadId from tool result: {result}")


def _extract_content(result: Json) -> str:
    if isinstance(result, dict):
        sc = result.get("structuredContent")
        if isinstance(sc, dict) and isinstance(sc.get("content"), str):
            return sc["content"]
        content = result.get("content")
        if isinstance(content, list) and content:
            first = content[0]
            if isinstance(first, dict) and isinstance(first.get("text"), str):
                return first["text"]
    return ""
