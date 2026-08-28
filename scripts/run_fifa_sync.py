"""独立 FIFA Sync 命令。"""

from __future__ import annotations

import argparse
import json
from datetime import date

from src.application.facade import MarketingOpsFacade
from src.utils.dates import yesterday


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one FIFA file upsert")
    parser.add_argument("--date", dest="target_date", default=None, help="YYYY-MM-DD; defaults to yesterday")
    parser.add_argument("--demo", action="store_true", help="Explicitly run with Demo connector")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target_date = date.fromisoformat(args.target_date) if args.target_date else yesterday()
    result = MarketingOpsFacade({}).run_fifa_sync(target_date)
    print(json.dumps({
        "status": "SUCCESS" if result.upsert.errors == 0 else "WARNING",
        "source_file": str(result.source_file),
        "target_date": target_date.isoformat(),
        "inserted": result.upsert.inserted,
        "updated": result.upsert.updated,
        "skipped": result.upsert.skipped,
        "errors": result.upsert.errors,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

