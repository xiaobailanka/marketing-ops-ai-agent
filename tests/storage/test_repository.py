from datetime import datetime, timezone

import pytest

from src.models.task import TaskRecord, TaskStatus, TaskType
from src.storage.session_repository import SessionRepository
from src.storage.sqlalchemy_repository import SQLAlchemyRepository


def test_session_repository_is_isolated_and_resettable() -> None:
    first_state: dict = {}
    second_state: dict = {}
    first = SessionRepository(first_state)
    second = SessionRepository(second_state)
    first.save_task(TaskRecord(task_type=TaskType.DATA_CLEANING, status=TaskStatus.SUCCESS))
    assert len(first.list_tasks()) == 1
    assert second.list_tasks() == []
    first.reset()
    assert first.list_tasks() == []


def test_sqlalchemy_repository_persists_tasks(tmp_path) -> None:
    path = str(tmp_path / "tasks.db")
    repository = SQLAlchemyRepository(path)
    task = TaskRecord(
        task_type=TaskType.ADS_QC,
        status=TaskStatus.WARNING,
        started_at=datetime.now(timezone.utc),
        warnings=1,
    )
    repository.save_task(task)
    loaded = SQLAlchemyRepository(path).get_task(task.task_id)
    assert loaded is not None and loaded.status == TaskStatus.WARNING
    with pytest.raises(PermissionError):
        repository.reset()

