"""YAML 配置加载。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.models.project import AppConfig

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str | Path) -> dict[str, Any]:
    """读取 YAML；空文件返回空字典。"""

    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = PROJECT_ROOT / resolved
    with resolved.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_app_config(path: str | Path = "config/projects.yaml") -> AppConfig:
    return AppConfig.model_validate(load_yaml(path))


def load_cleaning_rules(path: str | Path = "config/cleaning_rules.yaml") -> dict[str, Any]:
    return load_yaml(path)


def load_qc_rules(path: str | Path = "config/qc_rules.yaml") -> dict[str, Any]:
    return load_yaml(path)


def load_anomaly_thresholds(
    path: str | Path = "config/anomaly_thresholds.yaml",
) -> dict[str, Any]:
    return load_yaml(path)

