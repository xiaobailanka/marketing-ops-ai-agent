"""日期与时区工具。"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


def yesterday(timezone_name: str = "Asia/Shanghai", now: datetime | None = None) -> date:
    zone = ZoneInfo(timezone_name)
    localized = now.astimezone(zone) if now else datetime.now(zone)
    return localized.date() - timedelta(days=1)

