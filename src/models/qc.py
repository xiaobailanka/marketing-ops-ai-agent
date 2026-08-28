"""Google Ads QC Canonical Models。"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class QCLevel(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    ERROR = "ERROR"


class CampaignQCModel(BaseModel):
    country: str
    channel: str = "GG"
    objective: str
    ad_type: str
    product: str
    start_date: date
    end_date: date
    project_name: str
    stage: str
    landing_page_domain: str
    creative_name: str | None = None
    total_budget: float = Field(gt=0)
    budget_type: str = "TOTAL"
    bid_strategy: str
    language: str
    status: str
    campaign_name: str


class AdGroupQCModel(BaseModel):
    ad_group_name: str
    targeting_strategy: str
    audience_name: str | None = None
    keyword_type: str | None = None
    keyword_theme: str | None = None
    match_type: str | None = None
    keywords: list[str] = Field(default_factory=list)
    placement: list[str] = Field(default_factory=list)
    bid: float | None = Field(default=None, ge=0)


class AdQCModel(BaseModel):
    ad_name: str
    creative_theme: str
    creative_name: str
    duration_or_size: str
    creative_format: str
    youtube_url: str | None = None
    final_url: str
    headline: str | None = None
    long_headline: str | None = None
    description: str | None = None
    cta: str | None = None


class QCResult(BaseModel):
    level: QCLevel
    object_level: str
    object_name: str
    field: str
    plan_value: Any = None
    ads_value: Any = None
    canonical_plan_value: Any = None
    canonical_ads_value: Any = None
    difference: str = ""
    explanation: str = ""
    suggested_action: str = ""
    rule: str = ""

