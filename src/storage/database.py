"""SQLAlchemy 数据库初始化。"""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.utils.config import PROJECT_ROOT


class Base(DeclarativeBase):
    pass


def database_url(path: str | None = None) -> str:
    configured = path or os.getenv("DATABASE_PATH", "data/app.db")
    db_path = Path(configured)
    if not db_path.is_absolute():
        db_path = PROJECT_ROOT / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"


def build_session_factory(path: str | None = None):
    engine = create_engine(database_url(path), future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)

