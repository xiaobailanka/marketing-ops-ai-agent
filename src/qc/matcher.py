"""对象匹配；RapidFuzz 仅用于 Potential Match。"""

from __future__ import annotations

from typing import Any

from rapidfuzz import fuzz, process

from src.qc.naming_parser import normalize_cosmetic_name


def match_campaign(plan: dict[str, Any], candidates: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str, float]:
    target = str(plan.get("campaign_name", ""))
    normalized = normalize_cosmetic_name(target)
    for candidate in candidates:
        if normalize_cosmetic_name(str(candidate.get("campaign_name", ""))) == normalized:
            return candidate, "CANONICAL", 100.0
    names = [str(item.get("campaign_name", "")) for item in candidates]
    match = process.extractOne(target, names, scorer=fuzz.ratio)
    if not match:
        return None, "NONE", 0.0
    name, score, index = match
    return candidates[index], "POTENTIAL", float(score)

