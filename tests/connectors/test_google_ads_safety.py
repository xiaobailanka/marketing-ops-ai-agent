from src.connectors.google_ads.base import GoogleAdsConnector
from src.connectors.google_ads.real import RealGoogleAdsConnector


def test_google_ads_connector_has_no_write_methods() -> None:
    forbidden = {"create", "update", "pause", "enable", "delete", "set_budget", "set_bid"}
    assert forbidden.isdisjoint(set(dir(GoogleAdsConnector)))
    assert forbidden.isdisjoint(set(dir(RealGoogleAdsConnector)))
