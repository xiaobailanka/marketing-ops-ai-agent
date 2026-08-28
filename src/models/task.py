"""任务历史模型。"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskType(StrEnum):
    DATA_CLEANING = "DATA_CLEANING"
    DAILY_REPORT = "DAILY_REPORT"
    FIFA_SYNC = "FIFA_SYNC"
    ADS_QC = "ADS_QC"


class TaskStatus(StrEnum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    FAILED = "FAILED"


class TaskRecord(BaseModel):
    task_id: str = Field(default_factory=lambda: uuid4().hex)
    task_type: TaskType
    project: str = ""
    mode: str = "demo"
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    status: TaskStatus = TaskStatus.RUNNING
    input_rows: int = 0
    output_rows: int = 0
    warnings: int = 0
    errors: int = 0
    summary: str = ""

