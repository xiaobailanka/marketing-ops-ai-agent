"""FIFA 文件扫描、清洗和 Upsert 编排。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from src.connectors.feishu.base import FeishuBitableConnector, UpsertResult
from src.fifa.business_key import build_business_key
from src.fifa.cleaner import clean_fifa_frame
from src.fifa.file_scanner import find_target_file
from src.models.cleaning import CleaningResult


@dataclass(slots=True)
class FIFASyncResult:
    source_file: Path
    cleaning: CleaningResult
    upsert: UpsertResult


class FIFASyncService:
    def __init__(self, connector: FeishuBitableConnector) -> None:
        self.connector = connector

    def preview(self, source_file: str | Path) -> CleaningResult:
        return clean_fifa_frame(pd.read_excel(source_file))

    def run(self, directory: str | Path, target_date: date) -> FIFASyncResult:
        source_file = find_target_file(directory, target_date)
        cleaning = self.preview(source_file)
        records = cleaning.after.astype(object).where(pd.notnull(cleaning.after), None).to_dict(orient="records")
        for record in records:
            record["_business_key"] = build_business_key(record)
        upsert = self.connector.upsert(records)
        return FIFASyncResult(source_file, cleaning, upsert)

