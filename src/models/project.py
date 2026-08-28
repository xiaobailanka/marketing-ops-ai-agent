"""项目与应用配置模型。"""

from __future__ import annotations

from datetime import date
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, field_validator, model_validator


class ProjectConfig(BaseModel):
    """单个广告项目的可编辑配置。"""

    country: str = Field(min_length=2, max_length=8)
    project_name: str = Field(min_length=2)
    campaign_start_date: date
    campaign_end_date: date
    total_budget: float = Field(gt=0)
    google_sheet_id: str = ""
    anomaly_threshold: float = Field(default=0.2, gt=0, lt=1)

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("project_name")
    @classmethod
    def preserve_project_name(cls, value: str) -> str:
        # 仅去除首尾空格，不改变业务名称本身。
        return value.strip()

    @model_validator(mode="after")
    def validate_campaign_dates(self) -> "ProjectConfig":
        if self.campaign_end_date < self.campaign_start_date:
            raise ValueError("campaign_end_date must not precede campaign_start_date")
        return self


class AppConfig(BaseModel):
    """应用级配置。"""

    mode: str = "demo"
    timezone: str = "Asia/Shanghai"
    projects: list[ProjectConfig]

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"demo", "production"}:
            raise ValueError("mode must be demo or production")
        return normalized

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        ZoneInfo(value)
        return value

