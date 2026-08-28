"""Google Ads API 只读查询。"""

from __future__ import annotations

import os
from typing import Any

from google.ads.googleads.client import GoogleAdsClient


class RealGoogleAdsConnector:
    """仅暴露 list_qc_objects；V1 不存在 create/update/pause/enable 方法。"""

    def __init__(self, customer_id: str) -> None:
        required = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
            "use_proto_plus": True,
        }
        if not all(required[key] for key in ("developer_token", "client_id", "client_secret", "refresh_token")):
            raise RuntimeError("Real Google Ads credentials are not configured.")
        self.customer_id = customer_id.replace("-", "")
        self.client = GoogleAdsClient.load_from_dict(required)

    def list_qc_objects(self) -> list[dict[str, Any]]:
        service = self.client.get_service("GoogleAdsService")
        query = """
            SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type,
                   campaign.start_date, campaign.end_date, campaign_budget.amount_micros,
                   ad_group.id, ad_group.name, ad_group.status,
                   ad_group_ad.ad.id, ad_group_ad.ad.name, ad_group_ad.status,
                   ad_group_ad.ad.final_urls
            FROM ad_group_ad
            WHERE campaign.status IN ('ENABLED', 'PAUSED')
        """
        rows: list[dict[str, Any]] = []
        for row in service.search(customer_id=self.customer_id, query=query):
            rows.append({
                "resource_id": f"customers/{self.customer_id}/campaigns/{row.campaign.id}",
                "campaign_name": row.campaign.name,
                "status": row.campaign.status.name,
                "ad_type": row.campaign.advertising_channel_type.name,
                "start_date": row.campaign.start_date,
                "end_date": row.campaign.end_date,
                "total_budget": row.campaign_budget.amount_micros / 1_000_000,
                "ad_group_name": row.ad_group.name,
                "ad_name": row.ad_group_ad.ad.name,
                "final_url": row.ad_group_ad.ad.final_urls[0] if row.ad_group_ad.ad.final_urls else None,
            })
        return rows

