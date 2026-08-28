"""Canonical Value 不同即 ERROR 的严格比较器。"""

from __future__ import annotations

from typing import Any

from src.models.qc import QCLevel, QCResult
from src.qc.normalization import canonicalize


def compare_field(
    object_level: str,
    object_name: str,
    field: str,
    plan_value: Any,
    ads_value: Any,
    required: bool = True,
) -> QCResult:
    canonical_plan = canonicalize(field, plan_value)
    canonical_ads = canonicalize(field, ads_value)
    if canonical_plan == canonical_ads:
        if field == "campaign_name" and plan_value != ads_value:
            return QCResult(
                level=QCLevel.WARNING,
                object_level=object_level,
                object_name=object_name,
                field=field,
                plan_value=plan_value,
                ads_value=ads_value,
                canonical_plan_value=canonical_plan,
                canonical_ads_value=canonical_ads,
                explanation="Naming cosmetic issue; canonical name matches.",
                suggested_action="Review separator/case formatting before launch.",
                rule="naming_cosmetic_warning",
            )
        return QCResult(
            level=QCLevel.PASS,
            object_level=object_level,
            object_name=object_name,
            field=field,
            plan_value=plan_value,
            ads_value=ads_value,
            canonical_plan_value=canonical_plan,
            canonical_ads_value=canonical_ads,
            explanation="Canonical values match.",
            rule="strict_canonical_equality",
        )
    missing = canonical_plan is None or canonical_ads is None
    level = QCLevel.ERROR if required or not missing else QCLevel.WARNING
    return QCResult(
        level=level,
        object_level=object_level,
        object_name=object_name,
        field=field,
        plan_value=plan_value,
        ads_value=ads_value,
        canonical_plan_value=canonical_plan,
        canonical_ads_value=canonical_ads,
        difference=f"{canonical_plan!r} != {canonical_ads!r}",
        explanation="Required business values differ." if level == QCLevel.ERROR else "Optional field is missing.",
        suggested_action="Correct Google Ads or confirm the Media Plan source value.",
        rule="strict_canonical_equality",
    )

