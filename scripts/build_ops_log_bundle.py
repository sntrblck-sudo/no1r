#!/usr/bin/env python3
"""Collect local ops data into an OpsLogBundle JSON."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
TS = datetime.now(timezone.utc).isoformat()


def read_text_tail(path: Path, lines: int = 200) -> str | None:
    if not path.exists():
        return None
    try:
        data = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(data[-lines:])
    except Exception:
        return None


def load_json_file(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def tail_jsonl(path: Path, lines: int = 20) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
        entries = []
        for line in raw[-lines:]:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return entries
    except Exception:
        return []


def capture(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.stdout.strip():
            return result.stdout.strip()
        return result.stderr.strip()
    except Exception as exc:
        return f"(error running {' '.join(cmd)}: {exc})"


def system_metrics() -> dict[str, Any]:
    disk = shutil.disk_usage(WORKSPACE)
    disk_percent = round(disk.used / disk.total * 100, 2) if disk.total else 0.0

    mem_total = 0
    mem_available = 0
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    mem_total = int(line.split()[1])  # kB
                elif line.startswith("MemAvailable:"):
                    mem_available = int(line.split()[1])
        mem_used = max(mem_total - mem_available, 0)
        mem_percent = round(mem_used / mem_total * 100, 2) if mem_total else 0.0
    except Exception:
        mem_percent = None

    try:
        load_avg = os.getloadavg()
    except OSError:
        load_avg = (0.0, 0.0, 0.0)

    return {
        "disk": {"percent_used": disk_percent, "notes": f"workspace mount {WORKSPACE}"},
        "memory": {"percent_used": mem_percent, "notes": "from /proc/meminfo"},
        "cpu": {"load_avg": list(load_avg), "notes": "os.getloadavg"},
    }


def collect_recent_errors(tail: str | None) -> list[str]:
    if not tail:
        return []
    errors = []
    for line in tail.splitlines():
        if any(token in line.lower() for token in ("error", "failed", "alert")):
            errors.append(line.strip())
    return errors[-10:]


def main() -> None:
    bundle: dict[str, Any] = {
        "ts_collected": TS,
        "sentinel_log_tail": read_text_tail(WORKSPACE / "sentinel.log"),
        "sentinel_state": load_json_file(WORKSPACE / "sentinel_state.json"),
        "events_tail": tail_jsonl(WORKSPACE / "events.jsonl"),
        "ops_state": load_json_file(WORKSPACE / "ops_state.json"),
        "cron_status": capture(["openclaw", "cron", "list"]),
        "system_metrics": system_metrics(),
        "recent_errors": [],
    }

    bundle["recent_errors"] = collect_recent_errors(bundle.get("sentinel_log_tail"))

    print(json.dumps(bundle, indent=2))


if __name__ == "__main__":
    main()
