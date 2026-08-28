"""统一任务状态生命周期。"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, TypeVar

from src.models.task import TaskRecord, TaskStatus, TaskType
from src.storage.base import TaskRepository

T = TypeVar("T")


class TaskRunner:
    def __init__(self, repository: TaskRepository, mode: str = "demo") -> None:
        self.repository = repository
        self.mode = mode

    def run(
        self,
        task_type: TaskType,
        project: str,
        operation: Callable[[], T],
        input_rows: int = 0,
        summarize: Callable[[T], tuple[int, int, int, str]] | None = None,
    ) -> T:
        task = TaskRecord(task_type=task_type, project=project, mode=self.mode, input_rows=input_rows)
        self.repository.save_task(task)
        try:
            result = operation()
            output_rows, warning_count, error_count, summary = summarize(result) if summarize else (0, 0, 0, "Completed")
            task.output_rows = output_rows
            task.warnings = warning_count
            task.errors = error_count
            task.summary = summary
            task.status = TaskStatus.WARNING if warning_count or error_count else TaskStatus.SUCCESS
            return result
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.errors = 1
            task.summary = str(exc)
            raise
        finally:
            task.finished_at = datetime.now(timezone.utc)
            self.repository.save_task(task)

