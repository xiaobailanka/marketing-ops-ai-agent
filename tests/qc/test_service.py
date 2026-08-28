from src.demo.generator import generate_qc_records
from src.qc.service import GoogleAdsQCService


def test_demo_qc_has_pass_warning_and_error() -> None:
    plans, ads = generate_qc_records()
    summary = GoogleAdsQCService().run(plans, ads)
    assert summary.passed > 0
    assert summary.warnings > 0
    assert summary.errors > 0

