"""Google Campaign、Ad Group 和 Ad 命名解析。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.utils.config import load_yaml


@dataclass(slots=True)
class NamingParseResult:
    values: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _replace_cosmetic_separators(name: str) -> str:
    # 先保护唯一允许的 4位日期-4位日期，再把其余连字符转成命名分隔符。
    protected = re.sub(r"(\d{4})-(\d{4})", r"\1§\2", name.strip())
    normalized = re.sub(r"\s*-\s*", "_", protected).replace("§", "-")
    return re.sub(r"_+", "_", normalized)


def normalize_cosmetic_name(name: str) -> str:
    return _replace_cosmetic_separators(name).casefold()


class GoogleCampaignNameParser:
    FIELDS = [
        "country", "channel", "objective", "ad_type", "product", "date_range",
        "project_name", "stage", "landing_page_domain",
    ]

    def parse(self, name: str) -> NamingParseResult:
        result = NamingParseResult()
        cosmetic = _replace_cosmetic_separators(name)
        if cosmetic != name.strip():
            result.warnings.append("Campaign naming uses cosmetic separator variation")
        parts = [part.strip() for part in cosmetic.split("_") if part.strip()]
        if len(parts) < len(self.FIELDS):
            result.errors.append("Campaign name cannot resolve critical fields")
            return result
        result.values = dict(zip(self.FIELDS, parts[: len(self.FIELDS)], strict=True))
        if not re.fullmatch(r"\d{4}-\d{4}", result.values["date_range"]):
            result.errors.append("Campaign date range is invalid")
        return result


class GoogleAdGroupNameParser:
    def __init__(self) -> None:
        self.rules = load_yaml("config/naming_rules.yaml")

    def parse(self, name: str) -> NamingParseResult:
        parts = [part.strip() for part in name.split("_") if part.strip()]
        result = NamingParseResult()
        if not parts:
            result.errors.append("Ad Group name is empty")
            return result
        strategy = parts[0]
        if strategy.casefold() == "kw":
            if len(parts) < 4:
                result.errors.append("Keyword Ad Group requires KW Type, Theme and Match Type")
            else:
                result.values = {
                    "targeting_strategy": strategy,
                    "keyword_type": parts[1],
                    "keyword_theme": parts[2],
                    "match_type": parts[3],
                }
        elif strategy.casefold() in {item.casefold() for item in self.rules["targeting_strategies"]}:
            if len(parts) < 2:
                result.errors.append("Targeting Ad Group requires audience or theme")
            else:
                result.values = {"targeting_strategy": strategy, "audience_name": parts[1]}
        else:
            result.errors.append("Unknown targeting strategy")
        return result


class GoogleAdNameParser:
    def parse(self, name: str) -> NamingParseResult:
        parts = [part.strip() for part in name.split("_") if part.strip()]
        result = NamingParseResult()
        if len(parts) < 4:
            result.errors.append("Ad name cannot resolve critical creative fields")
            return result
        result.values = dict(zip(
            ["creative_theme", "creative_name", "duration_or_size", "creative_format"],
            parts[:4],
            strict=True,
        ))
        return result
