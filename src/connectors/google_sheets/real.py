"""真实 Google Sheets 写入；仅在 Service Account 配置完整时启用。"""

from __future__ import annotations

import json
import os
from datetime import date

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

from src.connectors.google_sheets.base import SheetWriteResult


class RealGoogleSheetsConnector:
    def __init__(self, credentials_json: str | None = None) -> None:
        raw = credentials_json or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
        if not raw:
            raise RuntimeError("Real Google Sheets credentials are not configured.")
        info = json.loads(raw)
        credentials = service_account.Credentials.from_service_account_info(
            info,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        self.service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

    def write_daily_report(self, sheet_id: str, report_date: date, frame: pd.DataFrame) -> SheetWriteResult:
        if not sheet_id:
            raise ValueError("Production mode requires google_sheet_id")
        worksheet = report_date.isoformat()
        metadata = self.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        existing = {item["properties"]["title"] for item in metadata.get("sheets", [])}
        action = "REPLACED" if worksheet in existing else "CREATED"
        if worksheet not in existing:
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={"requests": [{"addSheet": {"properties": {"title": worksheet}}}]},
            ).execute()
        else:
            self.service.spreadsheets().values().clear(
                spreadsheetId=sheet_id,
                range=f"'{worksheet}'",
                body={},
            ).execute()
        safe_frame = frame.astype(object).where(pd.notnull(frame), None)
        values = [list(safe_frame.columns)] + safe_frame.values.tolist()
        self.service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"'{worksheet}'!A1",
            valueInputOption="RAW",
            body={"values": values},
        ).execute()
        return SheetWriteResult(worksheet, action, len(frame), "Google Sheet updated")

