from src.models.qc import QCLevel
from src.qc.comparator import compare_field


def test_canonical_values_pass_and_business_differences_error() -> None:
    assert compare_field("Campaign", "Demo", "total_budget", "$5,000", 5000.0).level == QCLevel.PASS
    assert compare_field("Campaign", "Demo", "start_date", "2026/08/20", "2026-08-20").level == QCLevel.PASS
    assert compare_field("Campaign", "Demo", "objective", "video views", "VIDEO VIEWS").level == QCLevel.PASS
    assert compare_field(
        "Ad", "Demo", "final_url", "https://x.test/a?x=1", "https://x.test/a?x=2"
    ).level == QCLevel.ERROR


def test_naming_cosmetic_difference_is_warning() -> None:
    result = compare_field(
        "Campaign", "Demo", "campaign_name",
        "UG_GG_Traffic_GDN_CAMON50_0728-0826_Demo_Launch_example.com",
        "UG-GG-Traffic-GDN-CAMON50-0728-0826-Demo-Launch-example.com",
    )
    assert result.level == QCLevel.WARNING

