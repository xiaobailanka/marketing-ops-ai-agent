"""Production Task History Repository。"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, select
from sqlalchemy.orm import Mapped, mapped_column

from src.models.task import TaskRecord, TaskStatus, TaskType
from src.storage.database import Base, build_session_factory


class TaskRow(Base):
    __tablename__ = "tasks"

    task_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_type: Mapped[str] = mapped_column(String(32))
    project: Mapped[str] = mapped_column(String(255), default="")
    mode: Mapped[str] = mapped_column(String(16), default="production")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(16))
    input_rows: Mapped[int] = mapped_column(Integer, default=0)
    output_rows: Mapped[int] = mapped_column(Integer, default=0)
    warnings: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str] = mapped_column(Text, default="")


class SQLAlchemyRepository:
    def __init__(self, path: str | None = None) -> None:
        self.session_factory = build_session_factory(path)

    @staticmethod
    def _to_model(row: TaskRow) -> TaskRecord:
        return TaskRecord(
            task_id=row.task_id,
            task_type=TaskType(row.task_type),
            project=row.project,
            mode=row.mode,
            started_at=row.started_at,
            finished_at=row.finished_at,
            status=TaskStatus(row.status),
            input_rows=row.input_rows,
            output_rows=row.output_rows,
            warnings=row.warnings,
            errors=row.errors,
            summary=row.summary,
        )

    def save_task(self, task: TaskRecord) -> TaskRecord:
        with self.session_factory.begin() as session:
            row = session.get(TaskRow, task.task_id) or TaskRow(task_id=task.task_id)
            for field, value in task.model_dump().items():
                if field in {"task_type", "status"}:
                    value = value.value
                setattr(row, field, value)
            session.add(row)
        return task

    def list_tasks(self, failed_only: bool = False) -> list[TaskRecord]:
        statement = select(TaskRow).order_by(TaskRow.started_at.desc())
        if failed_only:
            statement = statement.where(TaskRow.status == TaskStatus.FAILED.value)
        with self.session_factory() as session:
            return [self._to_model(row) for row in session.scalars(statement).all()]

    def get_task(self, task_id: str) -> TaskRecord | None:
        with self.session_factory() as session:
            row = session.get(TaskRow, task_id)
            return self._to_model(row) if row else None

    def reset(self) -> None:
        # Production 数据不应被公共 Demo Reset 删除。
        raise PermissionError("Production repository cannot be reset from the demo UI")

