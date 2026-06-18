<!--
💡 GitHub SEO Keywords:
chinese trending data api, chinese social media scraper, weibo trending topics api,
baidu hot search api, zhihu trending api, douyin trending api, bilibili trending api,
toutiao news api, chinese trend monitor, weibo scraper, china trending topics,
chinese market intelligence, real-time chinese trends, china social media api,
content arbitrage api, cross-border ecommerce data, china consumer trends api,
chinese viral trends api, china market research api, chinese hot search api
-->

<p align="center">
  <a href="https://rapidapi.com/jkk542830/api/chinese-trending-data-api"><img src="https://img.shields.io/badge/RapidAPI-API%20Marketplace-0055FF?style=for-the-badge&logo=rapidapi" alt="Available on RapidAPI"></a>
  <img src="https://img.shields.io/github/stars/donald481/chinese-trending-data-api?style=for-the-badge&color=yellow" alt="GitHub Stars">
  <img src="https://img.shields.io/github/forks/donald481/chinese-trending-data-api?style=for-the-badge" alt="GitHub Forks">
  <img src="https://img.shields.io/github/license/donald481/chinese-trending-data-api?style=for-the-badge&color=green" alt="MIT License">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/LLM-Enhanced-FF6F00?style=for-the-badge&logo=openai" alt="LLM Enhanced">
  <img src="https://img.shields.io/badge/Data%20Points-8%2C558-7B68EE?style=for-the-badge" alt="13,784+ Trending Topics">
  <img src="https://img.shields.io/badge/Sources-8%20Platforms-FF4500?style=for-the-badge" alt="8 Chinese Platforms">
  <img src="https://img.shields.io/badge/Updated-Every%204h-00C853?style=for-the-badge" alt="Updated Every 4 Hours">
</p>

<h1 align="center">🇨🇳 Chinese Trending Data API</h1>
<p align="center"><strong>Real-time trending topics from 8 Chinese platforms — Weibo, Baidu, Douyin, Bilibili, Zhihu, Toutiao. LLM-translated, categorized, with monetization insights. The #1 Chinese trending data API on RapidAPI.</strong></p>

<p align="center">
  <a href="https://rapidapi.com/jkk542830/api/chinese-trending-data-api">🚀 Subscribe on RapidAPI</a> •
  <a href="http://161.153.56.113:8900/docs">📖 API Docs</a> •
  <a href="http://161.153.56.113:8900/v1/stats">📊 Live Stats</a> •
  <a href="CASE_STUDIES.md">💡 Case Studies</a>
</p>

<p align="center">
  <a href="README.md">English</a> •
  <a href="README_CN.md">中文</a>
</p>

---

## 📋 Table of Contents

- [Why This API?](#-why-this-api)
- [Features](#-features)
- [Data Sources](#-data-sources)
- [API Endpoints](#-api-endpoints)
- [Data Schema](#-data-schema)
- [Quick Start](#-quick-start)
- [Free Tier](#-free-tier)
- [Use Cases](#-use-cases)
- [Architecture](#-architecture)
- [Example Data](#-example-data)
- [FAQ](#-faq)
- [License](#-license)

---

## 🎯 Why This API?

China's internet is a **massive, fast-moving trend engine** — but it's locked behind language barriers, fragmented platforms, and opaque algorithms. The **Chinese Trending Data API** breaks through this wall:

- **8 major platforms** crawled in real-time: Weibo, Baidu, Douyin (TikTok China), Bilibili, Zhihu, Toutiao, and more
- **LLM-powered English translation** — every trend title and description is machine-translated into English
- **Monetization tags** — each trend is analyzed for commercial value (e.g., "Safety Equipment", "Celebrity Merchandise", "Gaming Hardware")
- **Heat scoring & categorization** — know exactly how viral something is and which category it belongs to

> **8,558+ data points** and growing. Updated every 4 hours. Ready for developers, traders, researchers, and content strategists.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **8 Chinese Platforms** | Weibo, Baidu, Douyin, Bilibili, Zhihu, Toutiao, Baidu API, Weibo API |
| **LLM English Translation** | Every trend title & content translated via DeepSeek LLM |
| **Monetization Tags** | AI-generated commercial opportunity tags per trend |
| **Heat Scoring** | Raw heat numbers + 5 heat levels: `normal`, `trending`, `hot`, `top`, `viral` |
| **Category Classification** | 50+ categories (tech, entertainment, finance, sports, health, etc.) |
| **Full-Text Search** | Search by keyword across titles, tags, and translations |
| **Filtering & Sorting** | By source, category, heat level, heat range, rank |
| **Pagination** | Offset/limit with up to 100 results per call |
| **Free Tier** | Try before you buy — limited calls per day, no credit card |
| **RapidAPI Ready** | Subscribe via RapidAPI marketplace |
| **FastAPI Backend** | Blazing fast, auto-generated OpenAPI docs |
| **Rate Limited** | 60 req/min per IP (paid tiers: higher limits) |

---

## 📡 Data Sources

| Source | Platform | Type | Records |
|--------|----------|------|---------|
| `weibo` | Sina Weibo | Microblogging | 1,430 |
| `weibo_api` | Weibo (API) | Microblogging | 1,492 |
| `toutiao` | Toutiao | News Aggregator | 1,242 |
| `baidu_api` | Baidu (API) | Search Engine | 1,158 |
| `baidu` | Baidu | Search Engine | 958 |
| `bilibili` | Bilibili | Video/Anime | 876 |
| `zhihu` | Zhihu | Q&A Community | 804 |
| `douyin` | Douyin (TikTok China) | Short Video | 598 |
| **Total** | | | **8,558+** |

---

## 📡 API Endpoints

All endpoints return JSON. Base URL: `http://161.153.56.113:8900`

### 🔍 Search Trends

```http
GET /v1/trends/search
```

Search and filter trending topics with 8 dimensions of filtering.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | — | Fuzzy search across title, tags, and translations |
| `source` | string | — | Filter by platform: `weibo`, `baidu`, `douyin`, `bilibili`, `zhihu`, `toutiao`, `baidu_api`, `weibo_api` |
| `category` | string | — | Filter by category: `technology`, `entertainment`, `finance`, `sports`, `health`, `social`, etc. |
| `heat_level` | string | — | Filter by heat: `normal`, `trending`, `hot`, `top`, `viral` |
| `min_heat` | int | — | Minimum heat score |
| `max_heat` | int | — | Maximum heat score |
| `sort_by` | string | `heat_desc` | Sort: `heat_desc`, `heat_asc`, `rank_asc`, `newest` |
| `limit` | int | `20` | Results per page (1–100) |
| `offset` | int | `0` | Pagination offset |

**Authentication:** `X-API-KEY` header (or `X-RapidAPI-Key` for RapidAPI)

**cURL Examples:**

```bash
# Search for AI-related trends
curl -s "http://161.153.56.113:8900/v1/trends/search?keyword=AI&limit=5" \
  -H "X-API-KEY: client_test_key_abc" | jq .

# Filter by source and heat level
curl -s "http://161.153.56.113:8900/v1/trends/search?source=douyin&heat_level=viral&limit=3" \
  -H "X-API-KEY: client_test_key_abc" | jq .

# Filter by category with sorting
curl -s "http://161.153.56.113:8900/v1/trends/search?category=technology&sort_by=newest&limit=5" \
  -H "X-API-KEY: client_test_key_abc" | jq .

# Get top viral trends with high heat
curl -s "http://161.153.56.113:8900/v1/trends/search?heat_level=viral&min_heat=5000000&sort_by=heat_desc&limit=10" \
  -H "X-API-KEY: client_test_key_abc" | jq .
```

**Response:**

```json
[
  {
    "id": 1751,
    "keyword": "山西事故煤矿企业对作业人数统计不清",
    "source": "toutiao",
    "title": "山西事故煤矿企业对作业人数统计不清",
    "content_clean": "头条热榜第1位：山西事故煤矿企业对作业人数统计不清（热度99944458）",
    "source_url": "https://www.toutiao.com/trending/...",
    "heat": 99944458,
    "rank": 1,
    "heat_level": "viral",
    "category": "finance",
    "tags": "Mining,Industrial Safety,Workplace Safety",
    "translated_title": "Shanxi Accident Mine Company Unsure of Worker Count",
    "translated_content": "A coal mine in Shanxi, China, involved in an accident failed to provide an accurate count of workers on site, sparking safety concerns.",
    "monetization_tags": "Safety Equipment,Mining Gear,Personal Protective Equipment",
    "updated_at": "2026-05-24 04:59:27.265804"
  }
]
```

### 🎲 Random Sample

```http
GET /v1/trends/sample
```

Get random records to preview data quality.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | int | `3` | Number of random samples (1–10) |

**cURL Example:**

```bash
curl -s "http://161.153.56.113:8900/v1/trends/sample?count=3" \
  -H "X-API-KEY: client_test_key_abc" | jq .
```

### 📊 Statistics

```http
GET /v1/stats
```

Get aggregate statistics about the dataset. **No authentication required** — use this to showcase data quality.

**cURL Example:**

```bash
curl -s http://161.153.56.113:8900/v1/stats | jq .
```

**Response:**

```json
{
  "total_trends": 12798,
  "sources": {
    "weibo": 2066, "weibo_api": 2055, "toutiao": 1813,
    "baidu_api": 1713, "baidu": 1534, "bilibili": 1352,
    "zhihu": 1285, "douyin": 980
  },
  "heat_levels": { "viral": 7024, "hot": 2309, "normal": 1755, "top": 1444, "trending": 266 },
  "avg_heat": 4801917,
  "max_heat": 99944458,
  "last_updated": "2026-06-07 05:29:03"
}
```

### ❤️ Health Check

```http
GET /health
```

**cURL Example:**

```bash
curl -s http://161.153.56.113:8900/health
```

```json
{
  "status": "healthy",
  "version": "2.2.0",
  "database": "clean_data.db",
  "sources": 8
}
```

---

## 📦 Data Schema

Every trend record contains these 16 fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | int | Unique record ID | `1751` |
| `keyword` | string | Native Chinese keyword | `"山西事故煤矿企业对作业人数统计不清"` |
| `source` | string | Source platform slug | `"toutiao"` |
| `original_id` | string | Unique ID from source platform | `"7ea4d8cc..."` |
| `title` | string | Original Chinese title | `"山西事故煤矿企业..."` |
| `content_clean` | string | Cleaned content summary | `"头条热榜第1位..."` |
| `source_url` | string \| null | Direct URL to the trend | `"https://..."` |
| `heat` | int \| null | Raw heat/engagement score | `99944458` |
| `rank` | int \| null | Position on trending board | `1` |
| `heat_level` | string \| null | Categorized heat level: `normal`, `trending`, `hot`, `top`, `viral` | `"viral"` |
| `category` | string \| null | Content category after optimization | `"finance"` |
| `tags` | string \| null | English topic tags (comma-separated) | `"Mining,Industrial Safety,Workplace Safety"` |
| `translated_title` | string \| null | LLM-translated English title | `"Shanxi Accident Mine Company..."` |
| `translated_content` | string \| null | LLM-translated English content | `"A coal mine in Shanxi..."` |
| `monetization_tags` | string \| null | AI-generated monetization opportunities | `"Safety Equipment,Mining Gear,PPE"` |
| `updated_at` | string | Timestamp of last update | `"2026-05-24 04:59:27.265804"` |

---

## 🚀 Quick Start

### 1. Get an API Key

**Option A: RapidAPI (Recommended)**
1. Go to [RapidAPI Marketplace](https://rapidapi.com/jkk542830/api/chinese-trending-data-api)
2. Click "Subscribe" and choose a plan
3. Use your RapidAPI key in the `X-RapidAPI-Key` header

**Option B: Direct Access**
1. Use the test key `client_test_key_abc` for evaluation
2. Contact us for a dedicated key with higher rate limits

### 2. Make Your First Call

```bash
# Check stats (no key needed)
curl -s http://161.153.56.113:8900/v1/stats | python3 -m json.tool

# Get 2 random samples
curl -s "http://161.153.56.113:8900/v1/trends/sample?count=2" \
  -H "X-API-KEY: client_test_key_abc" | python3 -m json.tool

# Search for entertainment trends
curl -s "http://161.153.56.113:8900/v1/trends/search?category=entertainment&limit=3" \
  -H "X-API-KEY: client_test_key_abc" | python3 -m json.tool
```

### 3. Parse in Python

```python
import requests
import json

API_URL = "http://161.153.56.113:8900"
API_KEY = "client_test_key_abc"
headers = {"X-API-KEY": API_KEY}

# Get trending tech topics
resp = requests.get(
    f"{API_URL}/v1/trends/search",
    params={"category": "technology", "limit": 5, "heat_level": "viral"},
    headers=headers
)
trends = resp.json()

for t in trends:
    print(f"[{t['heat_level'].upper()}] {t['translated_title']}")
    print(f"  Source: {t['source']} | Heat: {t['heat']:,}")
    print(f"  Monetization: {t['monetization_tags']}")
    print()
```

### 4. Parse in JavaScript / Node.js

```javascript
const API_URL = 'http://161.153.56.113:8900';
const API_KEY = 'client_test_key_abc';

const response = await fetch(`${API_URL}/v1/trends/search?category=entertainment&limit=5`, {
  headers: { 'X-API-KEY': API_KEY }
});
const trends = await response.json();
trends.forEach(t => {
  console.log(`[${t.heat_level}] ${t.translated_title}`);
  console.log(`  Heat: ${t.heat.toLocaleString()} | ${t.monetization_tags}`);
});
```

---

## 🆓 Free Tier

You can evaluate the API **without any payment or registration**:

| Endpoint | Free Daily Limit |
|----------|:----------------:|
| `GET /v1/trends/search` | **3 calls/day** |
| `GET /v1/trends/sample` | **2 calls/day** |
| `GET /v1/stats` | **Unlimited** |
| `GET /health` | **Unlimited** |

Free tier users get truncated monetization tags and translated content as a preview.

### 🔐 What You Get When You Subscribe

| Feature | Free | Basic ($29/mo) | Pro ($99/mo) | Enterprise |
|---------|:----:|:--------------:|:------------:|:----------:|
| Daily API Calls | 3+2 | 500/day | 3,000/day | Custom |
| Full Monetization Tags | ❌ | ✅ | ✅ | ✅ |
| Full Translated Content | ❌ | ✅ | ✅ | ✅ |
| All Search Filters | ✅ | ✅ | ✅ | ✅ |
| Rate Limit | 60/min | 500/min | 2,000/min | Custom |
| Priority Support | ❌ | ❌ | ✅ | ✅ |
| Custom Data Pipeline | ❌ | ❌ | ❌ | ✅ |

**[👉 Subscribe Now on RapidAPI](https://rapidapi.com/jkk542830/api/chinese-trending-data-api)**

---

## 💡 Use Cases

> 📖 **[See detailed case studies →](CASE_STUDIES.md)** with real examples, code, and ROI projections.

### 📈 Content & Media Arbitrage
Identify viral Chinese trends **before they hit global social media** — often 48-72 hours earlier. Translate, repurpose, and publish English-language content while the trend is still hot. Monetization tags like "Celebrity Merchandise" or "Gaming Hardware" tell you exactly where the commercial value is. **[→ Read full case study](CASE_STUDIES.md#-case-study-1-content-arbitrage----turn-chinese-viral-trends-into-english-traffic)**

### 📊 Market Research & Competitive Intel
Track what's trending across 8 Chinese platforms in real-time. Cross-platform comparison reveals WHERE to publish (Douyin-heavy = video, Bilibili-heavy = deep-dive, Weibo-heavy = opinion posts). At $99/month, it's **95%+ savings** vs. traditional quarterly reports. **[→ Read full case study](CASE_STUDIES.md#-case-study-2-market-research----multi-platform-trend-intelligence)**

### 🔍 SEO & Content Strategy
Find underserved English-language topics by identifying high-heat Chinese trends that have no English coverage. The LLM translations give you ready-made content angles. Target keywords before they become competitive.

### 🤖 AI Training Data
Every record includes raw Chinese text, LLM-translated English, category labels, heat scores, and monetization tags — a rich multi-modal dataset for training or fine-tuning models on Chinese internet culture and trend analysis.

### 📊 Financial Analysis & Sentiment
Track social sentiment on finance, real estate, and economic topics across Chinese platforms. Heat scores provide a quantitative measure of public attention on specific stocks, sectors, or economic issues.

### 🛒 E-commerce & Dropshipping
Monetization tags directly highlight product opportunities. A viral trend about "workout equipment" or "skincare routines" tells you exactly what to promote. Get ahead of demand curves by watching Chinese consumer trends — reduce dead inventory from 70-80% to 30-40%. **[→ Read full case study](CASE_STUDIES.md#-case-study-3-e-commerce-product-selection----monetization-tags-that-sell)**

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Chinese Trending Data API                      │
│                                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐             │
│  │  Scraper │  │  Scraper │  │  Scraper │  │  Scraper │  ... 8   │
│  │  Weibo   │  │  Baidu   │  │  Douyin  │  │  Zhihu   │  scrapers│
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │              │              │              │              │
│       └──────────────┴──────┬───────┴──────────────┘              │
│                             │                                     │
│                    ┌────────▼────────┐                            │
│                    │  Data Pipeline   │                            │
│                    │  ─────────────   │                            │
│                    │  • Clean &       │                            │
│                    │    Deduplicate   │                            │
│                    │  • Category      │                            │
│                    │    Optimization  │                            │
│                    │  • Heat Level    │                            │
│                    │    Calculation   │                            │
│                    └────────┬────────┘                            │
│                             │                                     │
│                    ┌────────▼────────┐                            │
│                    │  LLM Enrichment  │                            │
│                    │  ─────────────   │                            │
│                    │  • Title/Content │                            │
│                    │    Translation   │                            │
│                    │  • English Tags  │                            │
│                    │  • Monetization  │                            │
│                    │    Analysis      │                            │
│                    └────────┬────────┘                            │
│                             │                                     │
│                    ┌────────▼────────┐                            │
│                    │   SQLite DB     │                            │
│                    │  clean_data.db  │                            │
│ │ 8,558+ records │ │
│                    └────────┬────────┘                            │
│                             │                                     │
│                    ┌────────▼────────┐                            │
│                    │   FastAPI App    │                            │
│                    │   Uvicorn 8900   │                            │
│                    │                 │                            │
│                    │  /v1/trends/    │                            │
│                    │   ├─ search     │                            │
│                    │   ├─ sample     │                            │
│                    │   ├─ stats      │                            │
│                    │   └─ health     │                            │
│                    └────────┬────────┘                            │
│                             │                                     │
│                    ┌────────▼────────┐                            │
│                    │   RapidAPI      │                            │
│                    │   Marketplace   │                            │
│                    └─────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | FastAPI (Python 3.10+) |
| **Server** | Uvicorn (port 8900) |
| **Database** | SQLite (clean_data.db) |
| **LLM** | DeepSeek API for translation & enrichment |
| **Rate Limiting** | SlowAPI (60 req/min per IP) |
| **Deployment** | Linux server, systemd service |
| **API Marketplace** | RapidAPI |
| **Auth** | API Key + RapidAPI Proxy Secret |

---

## 📋 Example Data

Here are real records from the database showing the richness of the data:

**From Weibo:**
```json
{
  "keyword": "小米汽车发布",
  "category": "technology",
  "heat": 52000000,
  "heat_level": "viral",
  "translated_title": "Xiaomi Car Launch Event",
  "monetization_tags": "Electric Vehicles,Smart Cars,Consumer Electronics"
}
```

**From Bilibili:**
```json
{
  "keyword": "原神新版本爆料",
  "category": "gaming",
  "heat": 3800000,
  "heat_level": "hot",
  "translated_title": "Genshin Impact New Version Leaks",
  "monetization_tags": "Gaming Merchandise,Game Cards,Anime Collectibles"
}
```

**From Zhihu:**
```json
{
  "keyword": "人工智能就业前景",
  "category": "education",
  "heat": 1200000,
  "heat_level": "trending",
  "translated_title": "AI Career Prospects Discussion",
  "monetization_tags": "Online Courses,AI Tools,Career Services"
}
```

---

## ❓ FAQ

**Q: How often is the data updated?**
A: Scrapers run on schedule, with continuous updates. Check `/v1/stats` for the latest `last_updated` timestamp.

**Q: Can I access historical data?**
A: The database contains the latest trends from each platform. For historical trend data, contact us about enterprise plans.

**Q: What languages do you support?**
A: The API returns both original Chinese and LLM-translated English. The English translations cover titles, content, and tags.

**Q: Is there a limit on concurrent requests?**
A: The free tier is limited to 60 requests/minute/IP. Paid plans have higher limits.

**Q: How accurate are the categories?**
A: Categories have been optimized — `general` was reduced from 41% to 1.5% through a dedicated classification pass. The system now covers 50+ specific categories.

---

## 📄 License

This project is licensed for **API access only**. The source code structure is provided for transparency. Commercial use of the data requires a paid subscription via [RapidAPI](https://rapidapi.com/jkk542830/api/chinese-trending-data-api).

---

<p align="center">
  <a href="https://rapidapi.com/jkk542830/api/chinese-trending-data-api">
    <img src="https://img.shields.io/badge/Subscribe%20on-RapidAPI-0055FF?style=for-the-badge&logo=rapidapi" alt="Subscribe on RapidAPI">
  </a>
  <a href="http://161.153.56.113:8900/docs">
    <img src="https://img.shields.io/badge/API%20Docs-Swagger-85EA2D?style=for-the-badge&logo=swagger" alt="API Docs">
  </a>
  <a href="http://161.153.56.113:8900/v1/stats">
    <img src="https://img.shields.io/badge/Live%20Stats-Explore-FF6F00?style=for-the-badge" alt="Live Stats">
  </a>
</p>
