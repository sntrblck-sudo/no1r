#!/usr/bin/env python3
"""patterns_mirror.py

Internal "Pattern Mirror" for no1r.

Reads a few local state files and writes a short summary of observed patterns
into patterns.md. This is **internal-facing only** and does not take any
external actions.

Current inputs:
- attention_items.jsonl
- ops_state.json (if present)
- inclawbate_state.json (if present)

Outputs:
- patterns.md (overwritten each run)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from no1r_core import WORKSPACE, log, iter_jsonl, load_json

ATTENTION_FILE = WORKSPACE / "attention_items.jsonl"
OPS_STATE_FILE = WORKSPACE / "ops_state.json"
INCL_STATE_FILE = WORKSPACE / "inclawbate_state.json"
PATTERNS_FILE = WORKSPACE / "patterns.md"


def load_attention_patterns() -> list[str]:
    patterns: list[str] = []
    if not ATTENTION_FILE.exists():
        return patterns

    items: list[dict[str, Any]] = list(iter_jsonl(ATTENTION_FILE))
    if not items:
        return patterns

    # Assume file is already tension-sorted (highest first)
    top = items[:5]
    labels = ", ".join(f"{obj.get('id')}" for obj in top)
    patterns.append(f"Top attention items (by tension ordering): {labels or 'none'}.")

    # Note items that are low bucket but still present
    low = [obj for obj in items if obj.get("bucket") == "low"]
    if low:
        low_ids = ", ".join(obj.get("id", "?") for obj in low)
        patterns.append(f"Items explicitly in 'low' bucket: {low_ids}.")

    return patterns


def load_ops_patterns() -> list[str]:
    patterns: list[str] = []
    if not OPS_STATE_FILE.exists():
        return patterns

    state = load_json(OPS_STATE_FILE, default={}) or {}
    gateway = state.get("gateway")
    sentinel = state.get("sentinel")
    cron = state.get("cron")
    incl = state.get("inclawbate")

    if gateway and sentinel:
        if gateway == "ok" and sentinel == "ok":
            patterns.append("Core ops (gateway + sentinel) currently OK.")
        else:
            patterns.append(
                f"Core ops show issues: gateway={gateway}, sentinel={sentinel}."
            )

    if cron:
        if cron == "ok":
            patterns.append("Cron list accessible; status reported as OK in last snapshot.")
        else:
            patterns.append(f"Cron reported non-OK status in last snapshot: {cron}.")

    if incl:
        patterns.append(f"Inclawbate status flag in ops_state: {incl}.")

    return patterns


def load_inclawbate_patterns() -> list[str]:
    patterns: list[str] = []
    if not INCL_STATE_FILE.exists():
        return patterns

    try:
        raw = load_json(INCL_STATE_FILE, default={}) or {}
        data = raw.get("data", {})
        staking = data.get("staking", {})
        tvl = staking.get("tvl_usd", 0)
        stakers = staking.get("total_stakers", 0)
        token = data.get("token", {})
        price = token.get("price_usd")
    except Exception:
        return patterns

    patterns.append(
        f"Inclawbate staking snapshot: tvl_usd={tvl}, total_stakers={stakers}."
    )
    if tvl == 0 and stakers == 0:
        patterns.append("Inclawbate staking currently empty (TVL=0, no stakers).")

    if price is not None:
        patterns.append(f"Inclawbate token price (last snapshot): {price} USD.")

    return patterns


def main() -> None:
    log("Running Pattern Mirror (internal)", scope="patterns")

    lines: list[str] = []
    lines.append("# Pattern Mirror\n")

    attn = load_attention_patterns()
    if attn:
        lines.append("## Attention\n")
        for p in attn:
            lines.append(f"- {p}")
        lines.append("")

    ops = load_ops_patterns()
    if ops:
        lines.append("## Ops\n")
        for p in ops:
            lines.append(f"- {p}")
        lines.append("")

    incl = load_inclawbate_patterns()
    if incl:
        lines.append("## Inclawbate\n")
        for p in incl:
            lines.append(f"- {p}")
        lines.append("")

    if len(lines) == 1:
        lines.append("(No patterns detected; input state files missing or empty.)\n")

    PATTERNS_FILE.write_text("\n".join(lines), encoding="utf-8")
    log("Pattern Mirror wrote patterns.md", scope="patterns")


if __name__ == "__main__":
    main()
