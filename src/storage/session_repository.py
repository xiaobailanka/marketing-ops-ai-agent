"""Demo Session Repository。"""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

from src.models.task import TaskRecord, TaskStatus


class SessionRepository:
    def __init__(self, state: MutableMapping[str, Any]) -> None:
        self.state = state
        self.state.setdefault("task_records", [])

    def save_task(self, task: TaskRecord) -> TaskRecord:
        records: list[dict[str, Any]] = self.state["task_records"]
        payload = task.model_dump(mode="json")
        for index, existing in enumerate(records):
            if existing["task_id"] == task.task_id:
                records[index] = payload
                break
        else:
            records.append(payload)
        return task

    def list_tasks(self, failed_only: bool = False) -> list[TaskRecord]:
        tasks = [TaskRecord.model_validate(item) for item in self.state["task_records"]]
        if failed_only:
            tasks = [task for task in tasks if task.status == TaskStatus.FAILED]
        return sorted(tasks, key=lambda item: item.started_at, reverse=True)

    def get_task(self, task_id: str) -> TaskRecord | None:
        return next((task for task in self.list_tasks() if task.task_id == task_id), None)

    def reset(self) -> None:
        self.state["task_records"] = []

