# 数据字典

## 1. Project Configuration

| 字段 | 类型 | 说明 |
|---|---|---|
| country | string | 国家简称，如 UG |
| project_name | string | 项目业务名称，不自动改写 |
| campaign_start_date | date | Campaign 开始日期 |
| campaign_end_date | date | Campaign 结束日期 |
| total_budget | number | Total/Lifetime Budget |
| google_sheet_id | string | 项目日报 Sheet ID |
| anomaly_threshold | ratio | 异常阈值，默认 20% |

## 2. Canonical Performance Record

### 维度

| 字段 | 说明 |
|---|---|
| Country | 国家简称 |
| Project Name | 项目名 |
| Date | 数据日期 |
| Stage | 推广阶段 |
| Media | 媒体类型 |
| Platform | FB / TT / GG |
| Marketing Funnel | Awareness / Engagement / Traffic / Conversion |
| Objective | 投放目标 |
| Media Buy Type | 采买类型 |
| Audience Name | 受众名称 |
| Creative Theme | 素材主题 |
| Creative Name | 素材名 |
| Creative Type | Image / Video 等 |

### 原始指标

| 字段 | 类型 | 说明 |
|---|---|---|
| Spend | number | 消耗 |
| Impression | number | 曝光 |
| Reach | number | 触达人数 |
| Engagement | number | 互动 |
| Video View | number | 视频观看 |
| Follower | number | 新增粉丝 |
| Link Click | number | 链接点击 |
| Add to Cart | number | 加购 |
| Purchase | number | 购买 |
| Purchase Value | number | 购买价值 |
| All Clicks | number | 所有点击 |

## 3. KPI 公式

| KPI | 公式 | 分母为零 |
|---|---|---|
| CPM | Spend / Impression × 1000 | N/A |
| CTR | Link Click / Impression | N/A |
| CPC | Spend / Link Click | N/A |
| CPE | Spend / Engagement | N/A |
| ER | Engagement / Impression | N/A |
| CPV | Spend / Video View | N/A |
| VTR | Video View / Impression | N/A |
| CVR | Purchase / Link Click | N/A |
| CPA | Spend / Purchase | N/A |
| ROAS | Purchase Value / Spend | N/A |

## 4. FIFA Target Schema

```text
No., Country, Date, Stage, Media, Platform, Marketing Funnel, Objective,
Media Buy Type, Media Ad Type, Audience Name, Creative Theme, Creative Name,
Creative Type, Landing Page Domain, Spend, Impression, Engagement, Video View,
Follower, Link Click, Add to Cart, Purchase, Purchase Value, All Clicks,
Video Views P25, Video Views P50, Video Views P75, Video Views P100
```

业务键：

- No. 存在：`Country + Date + No.`
- No. 缺失：指定维度组合的 SHA-256 确定性哈希

## 5. QC Campaign Model

| 字段 | 是否关键 | 说明 |
|---|---|---|
| country | 是 | 国家 |
| channel | 是 | GG |
| objective | 是 | 广告目标 |
| ad_type | 是 | GDN / VRC / VVC |
| product | 是 | 产品型号 |
| start_date / end_date | 是 | 上线周期 |
| project_name | 是 | 项目 |
| stage | 是 | 阶段 |
| landing_page_domain | 是 | 落地页域名 |
| total_budget | 是 | Total Budget |
| budget_type | 是 | 固定为 TOTAL |
| bid_strategy | 是 | 出价策略 |
| language | 是 | 语言 |
| status | 是 | Pre-launch 应为 PAUSED |
| campaign_name | 是 | 完整命名 |

## 6. QC Ad Group Model

`targeting_strategy`、`audience_name`、`keyword_type`、`keyword_theme`、`match_type`、`keywords`、`placement`、`bid`。

## 7. QC Ad Model

`creative_theme`、`creative_name`、`duration_or_size`、`creative_format`、`youtube_url`、`final_url`、`headline`、`long_headline`、`description`、`cta`。

## 8. QC 等级

- PASS：Canonical Values 完全一致。
- WARNING：外观命名问题、Fuzzy Potential Match、非关键字段缺失、低置信度 Mapping。
- ERROR：关键业务字段不同、命名无法解析或 Campaign 在 QC 前已 ENABLED。

URL 只允许 trim，不允许删除或改写路径和 Query Parameter 后再认定相同。

## 9. Task Record

| 字段 | 说明 |
|---|---|
| task_id | 唯一任务 ID |
| task_type | DATA_CLEANING / DAILY_REPORT / FIFA_SYNC / ADS_QC |
| project | 项目 |
| mode | demo（Public Sandbox）/ production（持久化环境） |
| started_at / finished_at | 起止时间 |
| status | RUNNING / SUCCESS / WARNING / FAILED |
| input_rows / output_rows | 输入输出行数 |
| warnings / errors | 警告错误计数 |
| summary | 简要结果 |
