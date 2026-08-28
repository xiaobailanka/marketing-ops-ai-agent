from src.qc.naming_parser import GoogleAdGroupNameParser, GoogleAdNameParser, GoogleCampaignNameParser


def test_campaign_ad_group_and_ad_names() -> None:
    campaign = GoogleCampaignNameParser().parse(
        "UG_GG_Traffic_GDN_CAMON50_0728-0826_CAMON50Campaign_Launch_example.com"
    )
    assert not campaign.errors
    assert campaign.values["country"] == "UG"
    assert GoogleAdGroupNameParser().parse("INT_Young Tech Fans").values["targeting_strategy"] == "INT"
    assert GoogleAdNameParser().parse("Product Story_Hero_15s_Video").values["creative_format"] == "Video"


def test_cosmetic_and_critical_naming_levels() -> None:
    cosmetic = GoogleCampaignNameParser().parse(
        "UG - GG - Traffic - GDN - CAMON50 - 0728-0826 - Demo - Launch - example.com"
    )
    assert cosmetic.warnings and not cosmetic.errors
    assert GoogleCampaignNameParser().parse("UG_GG_Broken").errors

