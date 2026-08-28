from datetime import date

from src.connectors.feishu.mock import MockFeishuConnector
from src.demo.generator import generate_fifa_frame
from src.fifa.business_key import build_business_key
from src.fifa.cleaner import clean_fifa_frame


def test_business_key_and_upsert_are_idempotent() -> None:
    clean = clean_fifa_frame(generate_fifa_frame(date(2026, 8, 26))).after
    records = clean.astype(object).where(clean.notna(), None).to_dict(orient="records")
    for record in records:
        record["_business_key"] = build_business_key(record)
    connector = MockFeishuConnector({})
    first = connector.upsert(records)
    second = connector.upsert(records)
    assert first.inserted == len(records)
    assert second.skipped == len(records)
    assert second.inserted == 0
    changed = [dict(record) for record in records]
    changed[0]["Spend"] = float(changed[0]["Spend"] or 0) + 30
    third = connector.upsert(changed)
    assert third.updated == 1


def test_hash_key_is_stable_without_number() -> None:
    record = {"Country": "UG", "Date": "2026-08-26", "No.": None, "Creative Name": "Hero"}
    assert build_business_key(record) == build_business_key(dict(record))

