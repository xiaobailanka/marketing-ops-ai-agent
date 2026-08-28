"""Shared Drive 文件扫描。"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

FILE_PATTERN = re.compile(r"FIFA_(\d{4}-\d{2}-\d{2})\.xlsx$", re.IGNORECASE)


def scan_fifa_files(directory: str | Path) -> dict[date, Path]:
    result: dict[date, Path] = {}
    for path in Path(directory).glob("FIFA_*.xlsx"):
        match = FILE_PATTERN.match(path.name)
        if match:
            result[date.fromisoformat(match.group(1))] = path
    return dict(sorted(result.items()))


def find_target_file(directory: str | Path, target_date: date) -> Path:
    files = scan_fifa_files(directory)
    if target_date not in files:
        raise FileNotFoundError(f"未找到 {target_date.isoformat()} 的 FIFA 文件")
    return files[target_date]

