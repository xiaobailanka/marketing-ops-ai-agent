"""规则优先的 Schema Mapping；LLM 仅作为未来低置信度辅助。"""

from __future__ import annotations

import re

from src.models.mapping import MappingEntry

ALIASES = {
    "country": ["country", "market"],
    "channel": ["channel", "media"],
    "objective": ["objective", "obj."],
    "ad_type": ["ad type", "campaign type", "media ad type"],
    "product": ["product", "product name", "model"],
    "start_date": ["start date", "start"],
    "end_date": ["end date", "end"],
    "project_name": ["project name", "campaign project"],
    "stage": ["stage", "campaign stage"],
    "landing_page_domain": ["landing page domain", "domain"],
    "creative_name": ["creative name", "creative"],
    "total_budget": ["ad type budget", "campaign budget", "budget usd", "total budget", "planned budget"],
    "bid_strategy": ["bid strategy", "bidding"],
    "language": ["language"],
    "status": ["status"],
    "campaign_name": ["campaign name"],
    "ad_group_name": ["ad group name"],
    "targeting_strategy": ["targeting strategy"],
    "audience_name": ["audience name", "audience"],
    "bid": ["bid"],
    "ad_name": ["ad name"],
    "creative_theme": ["creative theme"],
    "creative_format": ["creative format"],
    "duration_or_size": ["duration", "image size", "duration or size"],
    "final_url": ["final url", "landing page url"],
    "headline": ["headline"],
    "long_headline": ["long headline"],
    "description": ["description"],
    "cta": ["cta", "call to action"],
}


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def map_headers(headers: list[str], source_sheet: str = "") -> list[MappingEntry]:
    mappings: list[MappingEntry] = []
    for header in headers:
        normalized = _normalize(header)
        best: tuple[str, float] | None = None
        for canonical, aliases in ALIASES.items():
            for alias in aliases:
                normalized_alias = _normalize(alias)
                if normalized == normalized_alias:
                    candidate = (canonical, 0.99)
                elif normalized_alias in normalized or normalized in normalized_alias:
                    candidate = (canonical, 0.88)
                else:
                    continue
                if best is None or candidate[1] > best[1]:
                    best = candidate
        if best:
            mappings.append(MappingEntry(
                source_column=header,
                canonical_field=best[0],
                confidence=best[1],
                source_sheet=source_sheet,
            ))
    return mappings

