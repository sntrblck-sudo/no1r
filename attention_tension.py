#!/usr/bin/env python3
"""attention_tension.py

Compute tension scores for attention items and reorder attention_items.jsonl.

- Tension = base_priority * age_factor
- age_factor is based on time since last_action_epoch (capped at max_age_seconds)

If last_action_epoch is missing, we treat the item as max age (highest age_factor).

This is a small, read-only-ish tool: it rewrites attention_items.jsonl but does not
change any semantic fields besides ordering. Safe to run manually when priorities
need refreshing.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Literal
import json
import time

Bucket = Literal["active", "watch", "low", "retired"]


@dataclass
class AttentionItem:
    id: str
    kind: str
    label: str
    base_priority: float
    scores: dict[str, float]
    last_action_epoch: int | None
    bucket: Bucket
    raw: dict[str, Any]


@dataclass
class ScoredAttentionItem:
    item: AttentionItem
    tension_score: float


def load_attention_items(path: Path) -> list[AttentionItem]:
    items: list[AttentionItem] = []
    if not path.exists():
        return items

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue

            base_priority = raw.get("base_priority")
            if base_priority is None:
                # Fallback: derive a rough base_priority from importance if present
                scores = raw.get("scores", {})
                base_priority = float(scores.get("importance", 0.5))

            last_action_epoch = raw.get("last_action_epoch")
            if isinstance(last_action_epoch, str):
                try:
                    last_action_epoch = int(last_action_epoch)
                except ValueError:
                    last_action_epoch = None

            item = AttentionItem(
                id=str(raw.get("id")),
                kind=str(raw.get("kind", "topic")),
                label=str(raw.get("label", "")),
                base_priority=float(base_priority),
                scores=dict(raw.get("scores", {})),
                last_action_epoch=last_action_epoch if isinstance(last_action_epoch, int) else None,
                bucket=str(raw.get("bucket", "watch")) or "watch",
                raw=raw,
            )
            items.append(item)

    return items


def compute_tension_scores(
    items: Iterable[AttentionItem],
    now_epoch: int | None = None,
    max_age_seconds: int = 7 * 24 * 3600,
) -> list[ScoredAttentionItem]:
    """Compute tension scores for attention items.

    Tension = base_priority * age_factor

    where age_factor is a normalized function of (now_epoch - last_action_epoch),
    capped by max_age_seconds. Items without last_action_epoch are treated as
    max age (age_factor = 1.0).
    """

    if now_epoch is None:
        now_epoch = int(time.time())

    scored: list[ScoredAttentionItem] = []

    for item in items:
        if item.last_action_epoch is None:
            age_factor = 1.0
        else:
            age = max(0, now_epoch - item.last_action_epoch)
            age_factor = min(age / max_age_seconds, 1.0)

        tension = item.base_priority * age_factor
        scored.append(ScoredAttentionItem(item=item, tension_score=tension))

    # Sort by tension_score descending, then by id for stability
    scored.sort(key=lambda s: (-s.tension_score, s.item.id))
    return scored


def write_attention_items(path: Path, scored_items: list[ScoredAttentionItem]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for scored in scored_items:
            raw = scored.item.raw
            raw["last_action_epoch"] = raw.get("last_action_epoch") or scored.item.last_action_epoch
            f.write(json.dumps(raw, ensure_ascii=False) + "\n")


def main() -> None:
    workspace = Path("/home/sntrblck/.openclaw/workspace")
    path = workspace / "attention_items.jsonl"

    items = load_attention_items(path)
    if not items:
        print("[attention_tension] No attention items found.")
        return

    now_epoch = int(time.time())
    scored_items = compute_tension_scores(items, now_epoch=now_epoch)

    write_attention_items(path, scored_items)

    print("[attention_tension] Rewrote attention_items.jsonl sorted by tension_score.")
    print("Top items:")
    for scored in scored_items[:5]:
        print(f"- {scored.item.id}: tension={scored.tension_score:.3f} (base={scored.item.base_priority}, last_action={scored.item.last_action_epoch})")


if __name__ == "__main__":
    main()
