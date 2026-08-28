"""广告类型 Validator 基类。"""

from __future__ import annotations

from typing import Any

from src.models.qc import QCResult
from src.qc.comparator import compare_field

CAMPAIGN_FIELDS = [
    "country", "channel", "objective", "ad_type", "product", "start_date", "end_date",
    "project_name", "stage", "landing_page_domain", "total_budget", "budget_type",
    "bid_strategy", "language", "status", "campaign_name",
]
AD_GROUP_FIELDS = ["targeting_strategy", "audience_name", "bid"]
AD_FIELDS = [
    "creative_theme", "creative_name", "duration_or_size", "creative_format", "final_url",
    "headline", "long_headline", "description", "cta",
]
OPTIONAL_FIELDS = {"headline", "long_headline", "description"}


class BaseValidator:
    ad_type = "BASE"

    def validate(self, plan: dict[str, Any], ads: dict[str, Any]) -> list[QCResult]:
        name = str(plan.get("campaign_name", "Unknown Campaign"))
        results: list[QCResult] = []
        for field in CAMPAIGN_FIELDS:
            results.append(compare_field("Campaign", name, field, plan.get(field), ads.get(field)))
        for field in AD_GROUP_FIELDS:
            results.append(compare_field(
                "Ad Group", str(plan.get("ad_group_name", name)), field,
                plan.get(field), ads.get(field), required=field not in OPTIONAL_FIELDS,
            ))
        for field in AD_FIELDS:
            results.append(compare_field(
                "Ad", str(plan.get("ad_name", name)), field,
                plan.get(field), ads.get(field), required=field not in OPTIONAL_FIELDS,
            ))
        return results

