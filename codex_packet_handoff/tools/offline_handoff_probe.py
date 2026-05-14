#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any, Dict

try:
    from router import _run_cli_integrator, _run_cli_reviewer, load_cfg
except ImportError:  # pragma: no cover - package execution fallback
    from .router import _run_cli_integrator, _run_cli_reviewer, load_cfg


def _read_packet(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _scratch_workspace() -> tempfile.TemporaryDirectory[str]:
    tmp = tempfile.TemporaryDirectory(prefix="offline-handoff-probe-")
    root = Path(tmp.name)
    (root / "README.md").write_text("offline handoff probe scratch workspace\n", encoding="utf-8")
    return tmp


def run_probe(kind: str, packet_path: Path) -> Dict[str, Any]:
    cfg = load_cfg()
    packet = _read_packet(packet_path)
    with _scratch_workspace() as tmp:
        scratch = Path(tmp)
        if kind == "reviewer":
            output = _run_cli_reviewer(
                cfg,
                str(scratch),
                packet,
                "offline handoff probe",
                local=True,
            )
        else:
            output = _run_cli_integrator(
                cfg,
                str(scratch),
                packet,
                local=True,
            )
        return {
            "kind": kind,
            "fixture": str(packet_path),
            "scratch_workspace": str(scratch),
            "ok": bool((output or "").strip()),
            "output": output or "",
        }


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run local reviewer/integrator handoff without touching the live queue.")
    ap.add_argument("kind", choices=["reviewer", "integrator"])
    ap.add_argument("fixture", help="Path to a sample packet file")
    args = ap.parse_args()

    result = run_probe(args.kind, Path(args.fixture))
    payload = dict(result)
    output = str(payload.pop("output"))
    print(json.dumps(payload, indent=2))
    if output:
        print("\n--- OUTPUT ---\n")
        print(output)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
