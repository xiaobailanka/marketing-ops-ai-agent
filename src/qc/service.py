"""Google Ads QC 用例编排。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.models.qc import QCLevel, QCResult
from src.qc.matcher import match_campaign
from src.qc.validators import GDNValidator, VRCValidator, VVCValidator


@dataclass(slots=True)
class QCRunSummary:
    objects_checked: int
    passed: int
    warnings: int
    errors: int
    results: list[QCResult]


class GoogleAdsQCService:
    def __init__(self) -> None:
        self.validators = {
            "GDN": GDNValidator(),
            "VRC": VRCValidator(),
            "VVC": VVCValidator(),
        }

    def run(self, plans: list[dict[str, Any]], ads_objects: list[dict[str, Any]]) -> QCRunSummary:
        results: list[QCResult] = []
        for plan in plans:
            ad_type = str(plan.get("ad_type", "")).upper()
            if ad_type not in self.validators:
                results.append(QCResult(
                    level=QCLevel.ERROR,
                    object_level="Campaign",
                    object_name=str(plan.get("campaign_name", "Unknown")),
                    field="ad_type",
                    plan_value=ad_type,
                    explanation="Unsupported ad type for V1.",
                    suggested_action="Use GDN, VRC or VVC.",
                    rule="supported_ad_type",
                ))
                continue
            matched, method, score = match_campaign(plan, ads_objects)
            if matched is None:
                results.append(QCResult(
                    level=QCLevel.ERROR,
                    object_level="Campaign",
                    object_name=str(plan.get("campaign_name", "Unknown")),
                    field="campaign_name",
                    plan_value=plan.get("campaign_name"),
                    explanation="No Google Ads campaign match found.",
                    suggested_action="Confirm account and campaign naming.",
                    rule="campaign_matching",
                ))
                continue
            if method == "POTENTIAL":
                results.append(QCResult(
                    level=QCLevel.WARNING,
                    object_level="Campaign",
                    object_name=str(plan.get("campaign_name", "Unknown")),
                    field="campaign_name",
                    plan_value=plan.get("campaign_name"),
                    ads_value=matched.get("campaign_name"),
                    explanation=f"Fuzzy potential match ({score:.1f}%). Human confirmation required.",
                    suggested_action="Confirm the potential match before relying on QC results.",
                    rule="fuzzy_potential_match",
                ))
                continue
            results.extend(self.validators[ad_type].validate(plan, matched))
        passed = sum(item.level == QCLevel.PASS for item in results)
        warnings = sum(item.level == QCLevel.WARNING for item in results)
        errors = sum(item.level == QCLevel.ERROR for item in results)
        return QCRunSummary(len(plans), passed, warnings, errors, results)

