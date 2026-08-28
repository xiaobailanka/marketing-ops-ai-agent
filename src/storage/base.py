"""任务历史 Repository 接口。"""

from __future__ import annotations

from typing import Protocol

from src.models.task import TaskRecord


class TaskRepository(Protocol):
    def save_task(self, task: TaskRecord) -> TaskRecord: ...

    def list_tasks(self, failed_only: bool = False) -> list[TaskRecord]: ...

    def get_task(self, task_id: str) -> TaskRecord | None: ...

    def reset(self) -> None: ...

