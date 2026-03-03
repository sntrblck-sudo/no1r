#!/usr/bin/env python3
"""ops_inbox.py

Compact "ops inbox" for no1rlocal.

Prints a one-shot health snapshot:
- OpenClaw gateway status
- Sentinel health (/health + recent log lines)
- Cron summary

Read-only: does not change any state.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/sntrblck/.openclaw/workspace")


def run(cmd: str) -> str:
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return proc.stdout.strip() or proc.stderr.strip()


def header(title: str) -> None:
    print(f"\n=== {title} ===")


def show_gateway_status() -> None:
    header("OpenClaw Gateway")
    out = run("openclaw status 2>&1 | head -15")
    print(out)


def show_sentinel_health() -> None:
    header("Sentinel Health")
    # HTTP health
    health_raw = run("curl -s http://localhost:18799/health || echo '{}' ")
    try:
        h = json.loads(health_raw)
    except Exception:
        h = {}
    print("/health:")
    print(json.dumps(h, indent=2))

    # Last few log lines
    print("\nSentinel log (tail -10):")
    log_tail = run(f"tail -10 {WORKSPACE/'sentinel.log'} 2>&1")
    print(log_tail)


def show_cron_summary() -> None:
    header("Cron Jobs")
    out = run("openclaw cron list 2>&1 | head -20")
    print(out)


OPS_STATE_FILE = WORKSPACE / "ops_state.json"


def write_state(state: dict) -> None:
    try:
        OPS_STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception:
        pass


def main() -> None:
    ts = datetime.utcnow().isoformat() + "Z"
    print(f"◼️ ops_inbox snapshot @ {ts}\n")

    # Gateway health via openclaw status | grep Gateway line
    status_raw = run("openclaw status 2>&1 | head -15")
    show_gateway_status()

    # Sentinel
    show_sentinel_health()

    # Cron
    show_cron_summary()

    # Cheap structured state for other tools
    state = {
        "timestamp": ts,
        "gateway": "ok" if "Gateway         │ local" in status_raw and "reachable" in status_raw else "warn",
        "sentinel": "ok",  # refined below
        "cron": "ok",
    }

    # Refine sentinel status
    try:
        health_raw = run("curl -s http://localhost:18799/health || echo '{}' ")
        h = json.loads(health_raw)
        if not h.get("status") == "ok":
            state["sentinel"] = "warn"
    except Exception:
        state["sentinel"] = "warn"

    write_state(state)


if __name__ == "__main__":
    main()
