"""只读 Google Ads Connector 协议；故意不定义任何 write method。"""

from __future__ import annotations

from typing import Any, Protocol


class GoogleAdsConnector(Protocol):
    def list_qc_objects(self) -> list[dict[str, Any]]: ...

