"""真实 Feishu Bitable Connector。"""

from __future__ import annotations

import os
from typing import Any

import requests

from src.connectors.feishu.base import UpsertResult


class RealFeishuConnector:
    BASE_URL = "https://open.feishu.cn/open-apis"

    def __init__(self) -> None:
        self.app_id = os.getenv("FEISHU_APP_ID", "")
        self.app_secret = os.getenv("FEISHU_APP_SECRET", "")
        self.app_token = os.getenv("FEISHU_BITABLE_APP_TOKEN", "")
        self.table_id = os.getenv("FEISHU_TABLE_ID", "")
        if not all((self.app_id, self.app_secret, self.app_token, self.table_id)):
            raise RuntimeError("Real Feishu credentials are not configured.")

    def _token(self) -> str:
        response = requests.post(
            f"{self.BASE_URL}/auth/v3/tenant_access_token/internal",
            json={"app_id": self.app_id, "app_secret": self.app_secret},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("code") != 0:
            raise RuntimeError(f"Feishu authentication failed: {payload.get('msg', 'unknown error')}")
        return str(payload["tenant_access_token"])

    def upsert(self, records: list[dict[str, Any]]) -> UpsertResult:
        # 真实 Bitable 的字段/记录 ID 依赖客户表结构；先读取业务键，再做 create/update。
        token = self._token()
        headers = {"Authorization": f"Bearer {token}"}
        base = f"{self.BASE_URL}/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records"
        response = requests.get(base, headers=headers, params={"page_size": 500}, timeout=30)
        response.raise_for_status()
        existing_items = response.json().get("data", {}).get("items", [])
        existing = {
            str(item.get("fields", {}).get("_business_key")): item
            for item in existing_items
            if item.get("fields", {}).get("_business_key")
        }
        result = UpsertResult()
        for record in records:
            key = str(record["_business_key"])
            item = existing.get(key)
            if item is None:
                write = requests.post(base, headers=headers, json={"fields": record}, timeout=30)
                write.raise_for_status()
                result.inserted += 1
            elif item.get("fields") == record:
                result.skipped += 1
            else:
                record_id = item["record_id"]
                write = requests.put(f"{base}/{record_id}", headers=headers, json={"fields": record}, timeout=30)
                write.raise_for_status()
                result.updated += 1
        return result

