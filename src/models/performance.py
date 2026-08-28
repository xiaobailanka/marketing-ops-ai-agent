"""广告表现 Canonical Data Model。"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CanonicalPerformanceRecord(BaseModel):
    """清洗后跨平台统一的一行广告表现数据。"""

    model_config = ConfigDict(extra="allow")

    country: str
    project_name: str
    date: date
    platform: str
    objective: str
    marketing_funnel: str
    stage: str | None = None
    media: str | None = None
    media_buy_type: str | None = None
    audience_name: str | None = None
    creative_theme: str | None = None
    creative_name: str | None = None
    creative_type: str | None = None
    campaign_name: str | None = None
    ad_group_name: str | None = None
    url: str | None = None
    spend: float = Field(default=0, ge=0)
    impression: float = Field(default=0, ge=0)
    reach: float | None = Field(default=None, ge=0)
    engagement: float = Field(default=0, ge=0)
    video_view: float = Field(default=0, ge=0)
    follower: float = Field(default=0, ge=0)
    link_click: float = Field(default=0, ge=0)
    add_to_cart: float = Field(default=0, ge=0)
    purchase: float = Field(default=0, ge=0)
    purchase_value: float = Field(default=0, ge=0)
    all_clicks: float = Field(default=0, ge=0)
    source_file: str | None = None
    source_sheet: str | None = None
    source_row: int | None = Field(default=None, ge=1)

