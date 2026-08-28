"""安全数值处理。"""

from __future__ import annotations

import math
from typing import Any


def safe_divide(numerator: float | int | None, denominator: float | int | None) -> float | None:
    """分母为零或输入非法时返回 None，杜绝 NaN/Infinity。"""

    try:
        if numerator is None or denominator in (None, 0):
            return None
        value = float(numerator) / float(denominator)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def parse_number(value: Any) -> float | None:
    """解析带货币符号、千分位或百分号的数值。"""

    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None
    text = str(value).strip()
    if not text:
        return None
    is_percent = text.endswith("%")
    cleaned = text.replace(",", "").replace("$", "").replace("%", "").strip()
    try:
        parsed = float(cleaned)
    except ValueError:
        return None
    parsed = parsed / 100 if is_percent else parsed
    return parsed if math.isfinite(parsed) else None

