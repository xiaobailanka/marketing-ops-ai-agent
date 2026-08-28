"""FIFA 幂等业务键。"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

HASH_FIELDS = [
    "Country", "Date", "Stage", "Media", "Platform", "Objective", "Media Ad Type",
    "Audience Name", "Creative Theme", "Creative Name", "Creative Type", "Landing Page Domain",
]


def _canonical(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().casefold().split())


def build_business_key(record: Mapping[str, Any]) -> str:
    number = record.get("No.")
    if number is not None and str(number).strip() and str(number).strip().lower() != "nan":
        return "|".join([
            _canonical(record.get("Country")),
            _canonical(record.get("Date")),
            _canonical(number),
        ])
    payload = "|".join(_canonical(record.get(field)) for field in HASH_FIELDS)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

