<!--
💡 GitHub SEO Keywords:
chinese trending data api, chinese social media scraper, weibo trending topics api,
baidu hot search api, zhihu trending api, douyin trending api, bilibili trending api,
toutiao news api, chinese trend monitor, weibo scraper, china trending topics,
chinese market intelligence, real-time chinese trends, china social media api,
content arbitrage api, cross-border ecommerce data, china consumer trends api,
chinese viral trends api, china market research api, chinese hot search api,
中文热搜API, 微博热搜API, 百度热搜API, 抖音热搜API, B站热搜API, 知乎热搜API,
今日头条热搜API, 中国趋势监控API, 中文社交媒体API, 跨境电商数据API
-->

<p align="center">
  <a href="https://rapidapi.com/jkk542830/api/chinese-trending-data-api"><img src="https://img.shields.io/badge/RapidAPI-API%20Marketplace-0055FF?style=for-the-badge&logo=rapidapi" alt="Available on RapidAPI"></a>
  <img src="https://img.shields.io/github/stars/donald481/chinese-trending-data-api?style=for-the-badge&color=yellow" alt="GitHub Stars">
  <img src="https://img.shields.io/github/forks/donald481/chinese-trending-data-api?style=for-the-badge" alt="GitHub Forks">
  <img src="https://img.shields.io/github/license/donald481/chinese-trending-data-api?style=for-the-badge&color=green" alt="MIT License">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/LLM-Enhanced-FF6F00?style=for-the-badge&logo=openai" alt="LLM Enhanced">
  <img src="https://img.shields.io/badge/Data%20Points-13%2C784-7B68EE?style=for-the-badge" alt="13,784+ Trending Topics">
  <img src="https://img.shields.io/badge/Sources-8%20Platforms-FF4500?style=for-the-badge" alt="8 Chinese Platforms">
  <img src="https://img.shields.io/badge/Updated-Every%204h-00C853?style=for-the-badge" alt="Updated Every 4 Hours">
</p>

<h1 align="center">🇨🇳 Chinese Trending Data API</h1>
<p align="center"><strong>实时聚合 8 大中文平台热搜数据 — 微博、百度、抖音、B站、知乎、今日头条全覆盖。LLM 智能翻译、分类标注、商业化标签一应俱全。RapidAPI 上排名第一的中文热搜数据接口。</strong></p>

<p align="center">
  <a href="https://rapidapi.com/jkk542830/api/chinese-trending-data-api">🚀 在 RapidAPI 订阅</a> •
  <a href="http://161.153.56.113:8900/docs">📖 API 文档</a> •
  <a href="http://161.153.56.113:8900/v1/stats">📊 实时统计</a> •
  <a href="CASE_STUDIES.md">💡 案例研究</a>
</p>

<p align="center">
  <a href="README.md">English</a> •
  <a href="README_CN.md">中文</a>
</p>

---

## 📋 目录

- [为什么选择这个 API？](#-为什么选择这个-api)
- [核心特性](#-核心特性)
- [数据来源](#-数据来源)
- [API 端点](#-api-端点)
- [数据结构](#-数据结构)
- [快速上手](#-快速上手)
- [免费额度](#-免费额度)
- [应用场景](#-应用场景)
- [系统架构](#-系统架构)
- [数据示例](#-数据示例)
- [常见问题](#-常见问题)
- [许可证](#-许可证)

---

## 🎯 为什么选择这个 API？

中国互联网是全球最具活力的信息场——热点瞬息万变，趋势此起彼伏。但对海外开发者和商业团队而言，语言壁垒、平台碎片化、算法黑箱，让这些数据如同被锁在墙后。**Chinese Trending Data API** 正是为打破这堵墙而生：

- **8 大平台实时爬取**：微博、百度、抖音（TikTok 中国版）、B站、知乎、今日头条等全覆盖
- **LLM 智能英文翻译**：每条热搜标题和摘要均由 DeepSeek 大模型自动翻译为英文
- **商业化变现标签**：AI 分析每条热点的商业价值，标注如"Safety Equipment"、"Celebrity Merchandise"、"Gaming Hardware"等关键词
- **热度评分 & 分类体系**：精准量化每个话题的火爆程度，自动归入 50+ 内容类目

> **13,784+ 条数据**，每 4 小时更新。为开发者、跨境贸易商、市场研究人员和内容运营者量身打造。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| **8 大中文平台** | 微博、百度、抖音、B站、知乎、今日头条、百度 API、微博 API |
| **LLM 英文翻译** | 每条热搜标题及内容由 DeepSeek 大模型翻译 |
| **商业化标签** | AI 自动生成每条热点的商业机会标签 |
| **热度评分** | 原始热度值 + 5 级热度等级：`normal`、`trending`、`hot`、`top`、`viral` |
| **分类体系** | 50+ 类目（科技、娱乐、财经、体育、健康、社会等） |
| **全文检索** | 支持关键词搜索标题、标签和译文 |
| **多维筛选排序** | 支持按来源、类目、热度等级、热度区间、排名筛选与排序 |
| **分页查询** | offset/limit 分页，单次最多返回 100 条 |
| **免费额度** | 无需付费即可体验，无需信用卡 |
| **RapidAPI 上架** | 通过 RapidAPI 市场一键订阅 |
| **FastAPI 驱动** | 极致性能，自动生成 OpenAPI 文档 |
| **速率限制** | 免费版 60 次/分钟·IP（付费版更高速率） |

---

## 📡 数据来源

| 来源 | 平台 | 类型 | 数据量 |
|------|------|------|--------|
| `weibo` | 新浪微博 | 微博社交 | 2,111 |
| `weibo_api` | 微博（API） | 微博社交 | 2,095 |
| `toutiao` | 今日头条 | 新闻聚合 | 1,848 |
| `baidu_api` | 百度（API） | 搜索引擎 | 1,752 |
| `baidu` | 百度 | 搜索引擎 | 1,543 |
| `bilibili` | B站 | 视频/二次元 | 1,386 |
| `zhihu` | 知乎 | 问答社区 | 1,303 |
| `douyin` | 抖音（TikTok 中国版） | 短视频 | 1,011 |
| **合计** | | | **13,049+** |

---

## 📡 API 端点

所有端点返回 JSON 格式数据。Base URL：`http://161.153.56.113:8900`

### 🔍 搜索热搜

```http
GET /v1/trends/search
```

支持 8 个维度的组合筛选，精准定位目标热点。

**查询参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `keyword` | string | — | 模糊搜索标题、标签和译文 |
| `source` | string | — | 按平台筛选：`weibo`、`baidu`、`douyin`、`bilibili`、`zhihu`、`toutiao`、`baidu_api`、`weibo_api` |
| `category` | string | — | 按类目筛选：`technology`、`entertainment`、`finance`、`sports`、`health`、`social` 等 |
| `heat_level` | string | — | 按热度等级：`normal`、`trending`、`hot`、`top`、`viral` |
| `min_heat` | int | — | 最低热度值 |
| `max_heat` | int | — | 最高热度值 |
| `sort_by` | string | `heat_desc` | 排序方式：`heat_desc`、`heat_asc`、`rank_asc`、`newest` |
| `limit` | int | `20` | 每页返回条数（1–100） |
| `offset` | int | `0` | 分页偏移量 |

**认证方式：** `X-API-KEY` 请求头（RapidAPI 用户使用 `X-RapidAPI-Key`）

**cURL 示例：**

```bash
# 搜索 AI 相关热搜
curl -s "http://161.153.56.113:8900/v1/trends/search?keyword=AI&limit=5" \
  -H "X-API-KEY: client_test_key_abc" | jq .

# 按平台和热度等级筛选
curl -s "http://161.153.56.113:8900/v1/trends/search?source=douyin&heat_level=viral&limit=3" \
  -H "X-API-KEY: client_test_key_abc" | jq .

# 按类目筛选并排序
curl -s "http://161.153.56.113:8900/v1/trends/search?category=technology&sort_by=newest&limit=5" \
  -H "X-API-KEY: client_test_key_abc" | jq .

# 获取超高热度爆榜话题
curl -s "http://161.153.56.113:8900/v1/trends/search?heat_level=viral&min_heat=5000000&sort_by=heat_desc&limit=10" \
  -H "X-API-KEY: client_test_key_abc" | jq .
```

**响应示例：**

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

### 🎲 随机抽样

```http
GET /v1/trends/sample
```

获取随机数据样本，快速预览数据质量。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `count` | int | `3` | 随机样本数（1–10） |

**cURL 示例：**

```bash
curl -s "http://161.153.56.113:8900/v1/trends/sample?count=3" \
  -H "X-API-KEY: client_test_key_abc" | jq .
```

### 📊 统计数据

```http
GET /v1/stats
```

获取数据集的聚合统计信息。**无需认证**——可用来展示数据质量。

**cURL 示例：**

```bash
curl -s http://161.153.56.113:8900/v1/stats | jq .
```

**响应示例：**

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

### ❤️ 健康检查

```http
GET /health
```

**cURL 示例：**

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

## 📦 数据结构

每条热搜记录包含以下 16 个字段：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | int | 唯一记录 ID | `1751` |
| `keyword` | string | 原始中文关键词 | `"山西事故煤矿企业对作业人数统计不清"` |
| `source` | string | 来源平台标识 | `"toutiao"` |
| `original_id` | string | 来源平台唯一 ID | `"7ea4d8cc..."` |
| `title` | string | 原始中文标题 | `"山西事故煤矿企业..."` |
| `content_clean` | string | 清洗后的内容摘要 | `"头条热榜第1位..."` |
| `source_url` | string \| null | 热搜原始链接 | `"https://..."` |
| `heat` | int \| null | 原始热度/互动评分 | `99944458` |
| `rank` | int \| null | 榜单位置 | `1` |
| `heat_level` | string \| null | 热度等级：`normal`、`trending`、`hot`、`top`、`viral` | `"viral"` |
| `category` | string \| null | 优化后的内容分类 | `"finance"` |
| `tags` | string \| null | 英文主题标签（逗号分隔） | `"Mining,Industrial Safety,Workplace Safety"` |
| `translated_title` | string \| null | LLM 翻译的英文标题 | `"Shanxi Accident Mine Company..."` |
| `translated_content` | string \| null | LLM 翻译的英文内容 | `"A coal mine in Shanxi..."` |
| `monetization_tags` | string \| null | AI 生成的商业化机会标签 | `"Safety Equipment,Mining Gear,PPE"` |
| `updated_at` | string | 最后更新时间戳 | `"2026-05-24 04:59:27.265804"` |

---

## 🚀 快速上手

### 1. 获取 API Key

**方式 A：通过 RapidAPI（推荐）**
1. 访问 [RapidAPI Marketplace](https://rapidapi.com/jkk542830/api/chinese-trending-data-api)
2. 点击"Subscribe"并选择套餐
3. 使用你的 RapidAPI Key 作为 `X-RapidAPI-Key` 请求头

**方式 B：直接访问**
1. 使用测试 Key `client_test_key_abc` 进行评估
2. 如需更高速率限制的专用 Key，请联系我们

### 2. 发起第一次请求

```bash
# 查看统计数据（无需 Key）
curl -s http://161.153.56.113:8900/v1/stats | python3 -m json.tool

# 获取 2 条随机样本
curl -s "http://161.153.56.113:8900/v1/trends/sample?count=2" \
  -H "X-API-KEY: client_test_key_abc" | python3 -m json.tool

# 搜索娱乐类热搜
curl -s "http://161.153.56.113:8900/v1/trends/search?category=entertainment&limit=3" \
  -H "X-API-KEY: client_test_key_abc" | python3 -m json.tool
```

### 3. Python 调用示例

```python
import requests
import json

API_URL = "http://161.153.56.113:8900"
API_KEY = "client_test_key_abc"
headers = {"X-API-KEY": API_KEY}

# 获取科技类爆款话题
resp = requests.get(
    f"{API_URL}/v1/trends/search",
    params={"category": "technology", "limit": 5, "heat_level": "viral"},
    headers=headers
)
trends = resp.json()

for t in trends:
    print(f"[{t['heat_level'].upper()}] {t['translated_title']}")
    print(f"  来源: {t['source']} | 热度: {t['heat']:,}")
    print(f"  商业化标签: {t['monetization_tags']}")
    print()
```

### 4. JavaScript / Node.js 调用示例

```javascript
const API_URL = 'http://161.153.56.113:8900';
const API_KEY = 'client_test_key_abc';

const response = await fetch(`${API_URL}/v1/trends/search?category=entertainment&limit=5`, {
  headers: { 'X-API-KEY': API_KEY }
});
const trends = await response.json();
trends.forEach(t => {
  console.log(`[${t.heat_level}] ${t.translated_title}`);
  console.log(`  热度: ${t.heat.toLocaleString()} | ${t.monetization_tags}`);
});
```

---

## 🆓 免费额度

你可以**无需付费或注册**即可评估 API：

| 端点 | 每日免费额度 |
|------|:----------:|
| `GET /v1/trends/search` | **3 次/天** |
| `GET /v1/trends/sample` | **2 次/天** |
| `GET /v1/stats` | **不限** |
| `GET /health` | **不限** |

免费版用户将获得截断的商业化标签和翻译内容作为预览。

### 🔐 各套餐权益对比

| 功能 | 免费 | Basic（$29/月） | Pro（$99/月） | 企业版 |
|------|:----:|:--------------:|:------------:|:------:|
| 每日调用次数 | 3+2 | 500 次/天 | 3,000 次/天 | 定制 |
| 完整商业化标签 | ❌ | ✅ | ✅ | ✅ |
| 完整翻译内容 | ❌ | ✅ | ✅ | ✅ |
| 全部搜索筛选 | ✅ | ✅ | ✅ | ✅ |
| 速率限制 | 60 次/分 | 500 次/分 | 2,000 次/分 | 定制 |
| 优先技术支持 | ❌ | ❌ | ✅ | ✅ |
| 定制数据管道 | ❌ | ❌ | ❌ | ✅ |

**[👉 立即在 RapidAPI 订阅](https://rapidapi.com/jkk542830/api/chinese-trending-data-api)**

---

## 💡 应用场景

> 📖 **[查看详细案例研究 →](CASE_STUDIES.md)** 内含实战示例、完整代码和 ROI 测算。

### 📈 内容跨境搬运 & 媒体套利
发现中文爆款热点，**抢在它们登上全球社交媒体之前**——通常领先 48-72 小时。翻译、改编、发布英文内容，在话题还未内卷时抢占先机。商业化标签如"Celebrity Merchandise"或"Gaming Hardware"直接告诉你钱在哪里。**[→ 阅读完整案例](CASE_STUDIES.md#-case-study-1-content-arbitrage----turn-chinese-viral-trends-into-english-traffic)**

### 📊 市场调研 & 竞品情报
实时追踪 8 大中文平台的热门话题，跨平台对比告诉你应该在哪里发布——抖音偏重 = 做视频，B站偏重 = 做深度，微博偏重 = 做观点。Pro 套餐 $99/月，比传统季度报告**节省 95% 以上**。**[→ 阅读完整案例](CASE_STUDIES.md#-case-study-2-market-research----multi-platform-trend-intelligence)**

### 🔍 SEO & 内容策略
识别高热度中文热搜中尚未有英文内容覆盖的蓝海话题。LLM 翻译直接提供内容切入角度，抢在关键词变得竞争激烈之前布局。

### 🤖 AI 训练数据
每条记录包含原始中文、LLM 英文翻译、分类标签、热度评分和商业化标签——一套丰富的多模态数据集，可用于训练或微调中国互联网文化及趋势分析模型。

### 📊 金融分析 & 舆情监控
跨平台追踪财经、房地产、经济话题的舆情走势。热度评分提供量化指标，精准衡量公众对特定股票、行业或经济议题的关注度。

### 🛒 跨境电商 & 选品
商业化标签直接指出产品机会。"健身器材"或"护肤流程"等爆梗话题明确告诉你该推什么商品。通过追踪中国消费趋势跑在需求曲线前面——将滞销库存从 70-80% 降至 30-40%。**[→ 阅读完整案例](CASE_STUDIES.md#-case-study-3-e-commerce-product-selection----monetization-tags-that-sell)**

---

## 🏗 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Chinese Trending Data API                      │
│                                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐             │
│  │  爬虫    │  │  爬虫    │  │  爬虫    │  │  爬虫    │  ... 8个  │
│  │  微博    │  │  百度    │  │  抖音    │  │  知乎    │  爬虫    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │              │              │              │              │
│       └──────────────┴──────┬───────┴──────────────┘              │
│                             │                                     │
│                    ┌────────▼────────┐                            │
│                    │  数据管道         │                            │
│                    │  ─────────────   │                            │
│                    │  • 清洗 &        │                            │
│                    │    去重          │                            │
│                    │  • 分类优化      │                            │
│                    │  • 热度等级       │                            │
│                    │    计算          │                            │
│                    └────────┬────────┘                            │
│                             │                                     │
│                    ┌────────▼────────┐                            │
│                    │  LLM 增强        │                            │
│                    │  ─────────────   │                            │
│                    │  • 标题/内容     │                            │
│                    │    翻译          │                            │
│                    │  • 英文标签      │                            │
│                    │  • 商业化价值     │                            │
│                    │    分析          │                            │
│                    └────────┬────────┘                            │
│                             │                                     │
│                    ┌────────▼────────┐                            │
│                    │   SQLite 数据库   │                            │
│                    │  clean_data.db  │                            │
│                    │  13,049+ 条记录  │                            │
│                    └────────┬────────┘                            │
│                             │                                     │
│                    ┌────────▼────────┐                            │
│                    │   FastAPI 服务   │                            │
│                    │   Uvicorn 8900  │                            │
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

### 技术栈

| 组件 | 技术 |
|------|------|
| **框架** | FastAPI (Python 3.10+) |
| **服务器** | Uvicorn (端口 8900) |
| **数据库** | SQLite (clean_data.db) |
| **LLM** | DeepSeek API（翻译与增强） |
| **速率限制** | SlowAPI (60 次/分钟·IP) |
| **部署** | Linux 服务器，systemd 服务 |
| **API 市场** | RapidAPI |
| **认证** | API Key + RapidAPI Proxy Secret |

---

## 📋 数据示例

以下为数据库中的真实记录，展示数据的丰富度：

**来自微博：**
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

**来自 B站：**
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

**来自知乎：**
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

## ❓ 常见问题

**Q：数据多久更新一次？**
A：爬虫定时运行，持续更新。可通过 `/v1/stats` 查看最新的 `last_updated` 时间戳。

**Q：可以获取历史数据吗？**
A：数据库包含各平台的最新热搜。如需历史趋势数据，请联系我们了解企业版方案。

**Q：支持哪些语言？**
A：API 同时返回原始中文和 LLM 翻译的英文。英文翻译覆盖标题、内容和标签。

**Q：并发请求有限制吗？**
A：免费版限制为 60 次/分钟·IP。付费版享有更高速率限制。

**Q：分类准确度如何？**
A：分类经过专门优化——`general` 类别占比已从 41% 降至 1.5%，目前覆盖 50+ 个具体类目。

---

## 📄 许可证

本项目仅授权 **API 访问**。源码结构公开仅供透明度参考。商业使用数据需通过 [RapidAPI](https://rapidapi.com/jkk542830/api/chinese-trending-data-api) 付费订阅。

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
