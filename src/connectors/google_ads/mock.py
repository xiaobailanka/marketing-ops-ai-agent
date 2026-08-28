"""读取固定 Seed Google Ads JSON。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.utils.config import PROJECT_ROOT


class MockGoogleAdsConnector:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else PROJECT_ROOT / "data/sample/google_ads/google_ads_sample.json"

    def list_qc_objects(self) -> list[dict[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8"))
