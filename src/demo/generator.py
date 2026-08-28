"""生成匿名化且可复现的广告业务样例数据。"""

from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.config import PROJECT_ROOT, load_app_config

SAMPLE_SEED = 20260827

FIFA_COLUMNS = [
    "No.", "Country", "Date", "Stage", "Media", "Platform",
    "Marketing Funnel", "Objective", "Media Buy Type", "Media Ad Type",
    "Audience Name", "Creative Theme", "Creative Name", "Creative Type",
    "Landing Page Domain", "Spend", "Impression", "Engagement", "Video View",
    "Follower", "Link Click", "Add to Cart", "Purchase", "Purchase Value",
    "All Clicks", "Video Views P25", "Video Views P50", "Video Views P75",
    "Video Views P100",
]


def _funnel_for(objective: str) -> str:
    return {
        "Reach": "Awareness",
        "Awareness": "Awareness",
        "Video Views": "Engagement",
        "Engagement": "Engagement",
        "Traffic": "Traffic",
        "Conversion": "Conversion",
    }[objective]


def generate_gtm_frames(seed: int = SAMPLE_SEED) -> dict[str, pd.DataFrame]:
    """返回 FB、TT、两个 GG Sheet；第二个 GG 用于验证选择规则。"""

    rng = random.Random(seed)
    config = load_app_config()
    platforms = ["FB", "TT", "GG"]
    objectives = ["Reach", "Video Views", "Engagement", "Traffic", "Conversion"]
    audiences = ["Young Tech Fans", "Gaming Enthusiasts", "Value Seekers", "Remarketing 30D"]
    creatives = ["Hero Video", "Camera Story", "Battery Demo", "Lifestyle Cut", "Offer Card"]
    start = date(2026, 7, 28)
    rows_by_platform: dict[str, list[dict[str, Any]]] = {key: [] for key in platforms}

    for day_index in range(30):
        current_date = start + timedelta(days=day_index)
        for project in config.projects:
            for platform in platforms:
                for item_index in range(12):
                    objective = objectives[(day_index + item_index) % len(objectives)]
                    impression = rng.randint(1200, 18000)
                    spend = round(impression / 1000 * rng.uniform(1.5, 5.5), 2)
                    if day_index == 18 and project.country == "UG" and platform == "GG":
                        spend = round(spend * 1.65, 2)
                    ctr = rng.uniform(0.003, 0.025)
                    link_click = int(impression * ctr)
                    engagement = int(impression * rng.uniform(0.006, 0.08))
                    video_view = int(impression * rng.uniform(0.15, 0.75)) if objective == "Video Views" else 0
                    purchase = int(link_click * rng.uniform(0.01, 0.08)) if objective == "Conversion" else 0
                    purchase_value = round(purchase * rng.uniform(25, 80), 2)
                    funnel: str | None = _funnel_for(objective)
                    if item_index == 0 and day_index % 6 == 0:
                        funnel = None
                    elif item_index == 1 and day_index % 7 == 0:
                        funnel = "Traffic" if funnel != "Traffic" else "Awareness"
                    row = {
                        "Country": f" {project.country.lower()} " if item_index == 2 else project.country,
                        "Project Name": project.project_name,
                        "Date": current_date.strftime("%Y/%m/%d") if item_index == 3 else current_date,
                        "Stage": " Launch " if item_index == 4 else "Launch",
                        "Media": " Paid Social " if platform != "GG" else "Paid Search",
                        "Platform": platform.lower() if item_index == 5 else platform,
                        "Marketing Funnel": funnel,
                        "Objective": f" {objective.lower()} " if item_index == 6 else objective,
                        "Media Buy Type": "Auction",
                        "Audience Name": audiences[item_index % len(audiences)],
                        "Creative Theme": "Product Story",
                        "Creative Name": creatives[(day_index + item_index) % len(creatives)],
                        "Creative Type": "video" if item_index % 2 else "Image",
                        "Campaign Name": f"{project.country}_GG_{objective.replace(' ', '')}_{project.project_name}",
                        "Ad Group Name": f"INT_{audiences[item_index % len(audiences)]}",
                        "URL": "https://example.com/product?utm_source=workspace",
                        "Spend": str(spend) if item_index == 7 else spend,
                        "Impression": 0 if item_index == 8 and day_index % 10 == 0 else impression,
                        "Reach": int(impression * rng.uniform(0.65, 0.95)),
                        "Engagement": engagement,
                        "Video View": video_view,
                        "Follower": rng.randint(0, 35) if objective == "Engagement" else 0,
                        "Link Click": link_click,
                        "Add to Cart": max(0, int(link_click * 0.08)),
                        "Purchase": purchase,
                        "Purchase Value": purchase_value,
                        "All Clicks": link_click + rng.randint(0, 30),
                    }
                    rows_by_platform[platform].append(row)

    frames: dict[str, pd.DataFrame] = {}
    for platform, rows in rows_by_platform.items():
        frame = pd.DataFrame(rows)
        duplicate = frame.iloc[[10]].copy()
        total = {column: None for column in frame.columns}
        total["Country"] = "TOTAL"
        total["Spend"] = frame["Spend"].map(lambda value: float(value)).sum()
        total["Impression"] = pd.to_numeric(frame["Impression"]).sum()
        total_frame = pd.DataFrame([total]).dropna(axis=1, how="all").reindex(columns=frame.columns)
        frame = pd.concat([frame, duplicate, total_frame], ignore_index=True)
        frames[platform] = frame
    frames["GG Archive"] = frames["GG"].head(20).copy()
    return frames


def generate_fifa_frame(target_date: date, seed: int = SAMPLE_SEED) -> pd.DataFrame:
    rng = random.Random(seed + target_date.toordinal())
    rows: list[dict[str, Any]] = []
    for index in range(36):
        objective = ["Reach", "Video Views", "Traffic", "Conversion"][index % 4]
        impression = rng.randint(900, 15000)
        spend = round(rng.uniform(8, 240), 2)
        rows.append({
            "No.": index + 1,
            "Country": " ug " if index % 11 == 0 else ["UG", "SN", "PK"][index % 3],
            "Date": target_date.strftime("%Y/%m/%d") if index % 7 == 0 else target_date,
            "Stage": "Launch",
            "Media": "Paid Social",
            "Platform": ["FB", "TT", "GG"][index % 3],
            "Marketing Funnel": None if index % 9 == 0 else ("Traffic" if index % 13 == 0 else _funnel_for(objective)),
            "Objective": objective.lower() if index % 8 == 0 else objective,
            "Media Buy Type": "Auction",
            "Media Ad Type": ["Feed", "Video", "GDN"][index % 3],
            "Audience Name": ["Young Tech Fans", "Value Seekers", "Remarketing 30D"][index % 3],
            "Creative Theme": "Product Story",
            "Creative Name": f"FIFA Creative {index % 6 + 1}",
            "Creative Type": "Video" if index % 2 else "Image",
            "Landing Page Domain": "example.com",
            "Spend": str(spend) if index % 6 == 0 else spend,
            "Impression": 0 if index == 5 else impression,
            "Engagement": int(impression * 0.03),
            "Video View": int(impression * 0.45),
            "Follower": index % 10,
            "Link Click": int(impression * 0.012),
            "Add to Cart": index % 8,
            "Purchase": index % 5,
            "Purchase Value": round((index % 5) * 45.0, 2),
            "All Clicks": int(impression * 0.015),
            "Video Views P25": int(impression * 0.35),
            "Video Views P50": int(impression * 0.28),
            "Video Views P75": int(impression * 0.20),
            "Video Views P100": int(impression * 0.12),
            "未命名": "drop me",
        })
    rows.append(dict(rows[3]))
    return pd.DataFrame(rows)


def generate_qc_records(seed: int = SAMPLE_SEED) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """生成 Media Plan Canonical rows 与 Google Ads rows。"""

    rng = random.Random(seed)
    plans: list[dict[str, Any]] = []
    ads: list[dict[str, Any]] = []
    projects = load_app_config().projects
    ad_types = ["GDN", "VRC", "VVC"]
    for project_index, project in enumerate(projects):
        for ad_index, ad_type in enumerate(ad_types):
            objective = {"GDN": "Traffic", "VRC": "Reach", "VVC": "Video Views"}[ad_type]
            budget = round(4200 + project_index * 700 + ad_index * 500, 2)
            campaign_name = (
                f"{project.country}_GG_{objective.replace(' ', '')}_{ad_type}_CAMON50_"
                f"0728-0826_{project.project_name.replace(' ', '')}_Launch_example.com"
            )
            plan = {
                "country": project.country,
                "channel": "GG",
                "objective": objective,
                "ad_type": ad_type,
                "product": "CAMON50",
                "start_date": "2026-07-28",
                "end_date": "2026-08-26",
                "project_name": project.project_name,
                "stage": "Launch",
                "landing_page_domain": "example.com",
                "creative_name": f"Hero {ad_type}",
                "total_budget": budget,
                "budget_type": "TOTAL",
                "bid_strategy": "Maximize Conversions" if ad_type == "GDN" else "Target CPM",
                "language": "English",
                "status": "PAUSED",
                "campaign_name": campaign_name,
                "ad_group_name": "INT_Young Tech Fans",
                "targeting_strategy": "INT",
                "audience_name": "Young Tech Fans",
                "bid": 2.5,
                "ad_name": f"Product Story_Hero {ad_type}_15s_Video",
                "creative_theme": "Product Story",
                "creative_format": "Video",
                "duration_or_size": "15s",
                "final_url": "https://example.com/product?utm_source=google",
                "headline": "Capture Every Moment",
                "long_headline": "Capture Every Moment with CAMON 50",
                "description": "Discover the new CAMON experience.",
                "cta": "Learn More",
            }
            actual = dict(plan)
            actual["resource_id"] = f"customers/sandbox/campaigns/{project_index}{ad_index}{rng.randint(1000,9999)}"
            plans.append(plan)
            ads.append(actual)

    # 固定制造有业务价值的错误；其余字段保持一致，整体字段级通过率约 85%。
    ads[0]["total_budget"] += 500
    ads[1]["country"] = "KE"
    ads[2]["start_date"] = "2026-07-29"
    ads[3]["audience_name"] = "Broad Tech Audience"
    ads[4]["final_url"] = "https://example.com/other?utm_source=google"
    ads[5]["creative_name"] = "Wrong Creative"
    ads[6]["cta"] = "Shop Now"
    ads[7]["campaign_name"] = ads[7]["campaign_name"].replace("_", "-")
    ads[8]["status"] = "ENABLED"
    return plans, ads


def seed_all(output_root: str | Path | None = None, seed: int = SAMPLE_SEED) -> dict[str, Path]:
    root = Path(output_root) if output_root else PROJECT_ROOT / "data" / "sample"
    gtm_dir = root / "gtm"
    fifa_dir = root / "fifa_shared_drive"
    media_dir = root / "media_plan"
    ads_dir = root / "google_ads"
    for directory in (gtm_dir, fifa_dir, media_dir, ads_dir):
        directory.mkdir(parents=True, exist_ok=True)

    gtm_path = gtm_dir / "TECNO_GTM_sample.xlsx"
    frames = generate_gtm_frames(seed)
    with pd.ExcelWriter(gtm_path, engine="openpyxl") as writer:
        pd.DataFrame({"Note": ["Anonymized sample advertising dataset. No customer records."]}).to_excel(
            writer, sheet_name="README", index=False
        )
        for sheet_name in ("FB", "TT", "GG", "GG Archive"):
            frames[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)

    fifa_paths: list[Path] = []
    for target_date in (date(2026, 8, 24), date(2026, 8, 25), date(2026, 8, 26)):
        path = fifa_dir / f"FIFA_{target_date.isoformat()}.xlsx"
        generate_fifa_frame(target_date, seed).to_excel(path, index=False)
        fifa_paths.append(path)

    plans, ads = generate_qc_records(seed)
    media_path = media_dir / "Sample_Google_Media_Plan.xlsx"
    with pd.ExcelWriter(media_path, engine="openpyxl") as writer:
        pd.DataFrame({"Campaign": ["Anonymized Sample Campaign Plan"]}).to_excel(
            writer, sheet_name="Brief", index=False
        )
        pd.DataFrame(plans).rename(columns={
            "country": "Country", "objective": "Objective", "ad_type": "Ad Type",
            "total_budget": "Ad Type Budget", "start_date": "Start Date",
            "end_date": "End Date", "campaign_name": "Campaign Name",
            "project_name": "Project Name", "bid_strategy": "Bid Strategy",
            "language": "Language", "status": "Status",
        }).to_excel(writer, sheet_name="Media Plan", index=False, startrow=3)
        pd.DataFrame(plans)[[
            "creative_name", "final_url", "headline", "long_headline", "description", "cta"
        ]].to_excel(writer, sheet_name="GG Timeline", index=False)
        pd.DataFrame(plans)[[
            "ad_group_name", "targeting_strategy", "audience_name", "bid"
        ]].to_excel(writer, sheet_name="Audience", index=False)

    ads_path = ads_dir / "google_ads_sample.json"
    ads_path.write_text(json.dumps(ads, ensure_ascii=False, indent=2), encoding="utf-8")
    plan_json_path = media_dir / "media_plan_canonical.json"
    plan_json_path.write_text(json.dumps(plans, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "gtm": gtm_path,
        "fifa_latest": fifa_paths[-1],
        "media_plan": media_path,
        "google_ads": ads_path,
        "media_plan_json": plan_json_path,
    }
