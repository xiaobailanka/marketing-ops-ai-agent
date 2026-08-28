"""配置驱动的数据清洗引擎。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from src.models.cleaning import CleaningAuditEntry, CleaningResult, CleaningSummary
from src.utils.config import load_cleaning_rules
from src.utils.numbers import parse_number

OBJECTIVE_CANONICAL = {
    "reach": "Reach",
    "awareness": "Awareness",
    "video views": "Video Views",
    "follower": "Follower",
    "post engagement": "Post Engagement",
    "engagement": "Engagement",
    "traffic": "Traffic",
    "conversion": "Conversion",
}


def _normalized_text(value: Any) -> str:
    return " ".join(str(value).strip().split()) if value is not None and not pd.isna(value) else ""


class CleaningEngine:
    """执行可审计、可配置且不触碰禁止字段的清洗规则。"""

    def __init__(self, rules: dict[str, Any] | None = None) -> None:
        self.rules = rules or load_cleaning_rules()

    def _audit(
        self,
        row_number: int,
        field: str,
        original: Any,
        new: Any,
        rule: str,
    ) -> CleaningAuditEntry:
        return CleaningAuditEntry(
            row_number=row_number,
            field=field,
            original_value=original,
            new_value=new,
            rule=rule,
            timestamp=datetime.now(timezone.utc),
        )

    def _canonical_category(self, field: str, value: Any) -> Any:
        text = _normalized_text(value)
        if not text:
            return None
        lowered = text.casefold()
        if field == "Objective":
            return OBJECTIVE_CANONICAL.get(lowered, text)
        mappings = self.rules.get("category_mappings", {}).get(field, {})
        if lowered in mappings:
            return mappings[lowered]
        if field in {"Marketing Funnel", "Media Buy Type", "Stage", "Media", "Creative Type"}:
            return text.title()
        return text

    def clean(self, frame: pd.DataFrame) -> CleaningResult:
        before = frame.copy()
        work = frame.copy()
        summary = CleaningSummary(input_rows=len(work), filtered_rows=len(work))
        audit_log: list[CleaningAuditEntry] = []
        warnings: list[str] = []

        if work.empty:
            return CleaningResult(before, work, summary, audit_log, warnings)

        # 删除汇总行时只检查常见业务维度，避免误删名为 Total Story 的素材。
        tokens = {str(token).strip().casefold() for token in self.rules.get("total_row_tokens", [])}
        total_mask = pd.Series(False, index=work.index)
        for column in ("Country", "Project Name", "Objective"):
            if column in work.columns:
                total_mask |= work[column].map(lambda value: _normalized_text(value).casefold() in tokens)
        summary.removed_total_rows = int(total_mask.sum())
        work = work.loc[~total_mask].copy()

        if "Impression" in work.columns:
            impression_numeric = work["Impression"].map(parse_number)
            zero_mask = impression_numeric.eq(0)
            summary.removed_zero_impression_rows = int(zero_mask.sum())
            work = work.loc[~zero_mask].copy()

        # 只允许配置列执行 Category 标准化，禁止修改名称、URL 和 ID。
        for field in self.rules.get("category_fields", []):
            if field not in work.columns:
                continue
            for index, original in work[field].items():
                canonical = self._canonical_category(field, original)
                if (pd.isna(original) and canonical is None) or original == canonical:
                    continue
                work.at[index, field] = canonical
                audit_log.append(self._audit(int(index) + 2, field, original, canonical, "category_normalization"))

        funnel_map = self.rules.get("objective_funnel_mapping", {})
        if "Objective" in work.columns and "Marketing Funnel" in work.columns:
            for index, row in work[["Objective", "Marketing Funnel"]].iterrows():
                objective = _normalized_text(row["Objective"]).casefold()
                expected = funnel_map.get(objective)
                if not expected:
                    continue
                original = row["Marketing Funnel"]
                current = _normalized_text(original)
                if not current:
                    work.at[index, "Marketing Funnel"] = expected
                    summary.funnel_filled += 1
                    audit_log.append(self._audit(int(index) + 2, "Marketing Funnel", original, expected, "funnel_missing_fill"))
                elif current.casefold() != expected.casefold():
                    work.at[index, "Marketing Funnel"] = expected
                    summary.funnel_corrected += 1
                    audit_log.append(self._audit(int(index) + 2, "Marketing Funnel", original, expected, "funnel_wrong_value_correction"))

        if "Date" in work.columns:
            parsed_dates = pd.to_datetime(work["Date"], errors="coerce")
            invalid_count = int(parsed_dates.isna().sum())
            if invalid_count:
                warnings.append(f"{invalid_count} 行 Date 无法解析")
            work["Date"] = parsed_dates.dt.date

        for field in self.rules.get("numeric_fields", []):
            if field not in work.columns:
                continue
            parsed = work[field].map(parse_number)
            invalid = parsed.isna() & work[field].notna() & work[field].astype(str).str.strip().ne("")
            invalid_count = int(invalid.sum())
            if invalid_count:
                warnings.append(f"{invalid_count} 行 {field} 不是有效数值")
            work[field] = parsed

        duplicate_mask = work.duplicated(keep="first")
        summary.duplicates_found = int(duplicate_mask.sum())
        work = work.loc[~duplicate_mask].copy()

        missing_required_mask = pd.Series(False, index=work.index)
        for field in self.rules.get("required_fields", []):
            if field not in work.columns:
                warnings.append(f"缺少必填字段 {field}")
                missing_required_mask |= True
                continue
            missing = work[field].isna() | work[field].astype(str).str.strip().eq("")
            count = int(missing.sum())
            if count:
                warnings.append(f"{count} 行缺少必填字段 {field}")
            missing_required_mask |= missing
        if missing_required_mask.any():
            work = work.loc[~missing_required_mask].copy()

        summary.validation_warnings = len(warnings)
        summary.final_clean_rows = len(work)
        work.reset_index(drop=True, inplace=True)
        return CleaningResult(before, work, summary, audit_log, warnings)

