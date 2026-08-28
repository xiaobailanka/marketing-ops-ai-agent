from src.utils.config import load_anomaly_thresholds, load_app_config, load_cleaning_rules


def test_default_projects_are_configured() -> None:
    config = load_app_config()
    pairs = {(item.country, item.project_name) for item in config.projects}
    assert pairs == {
        ("UG", "CAMON 50 Campaign"),
        ("SN", "Spark 50 Campaign"),
        ("PK", "PK CAMON 50 Campaign"),
    }
    assert all(project.total_budget > 0 for project in config.projects)


def test_rules_and_thresholds_are_externalized() -> None:
    rules = load_cleaning_rules()
    thresholds = load_anomaly_thresholds()
    assert "objective_funnel_mapping" in rules
    assert thresholds["min_impressions"] == 1000
    assert thresholds["budget_pacing_percentage_points"] == 0.10

