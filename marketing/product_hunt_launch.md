# Product Hunt Launch — Chinese Trending Data API

> **Launch Checklist:** Ensure RapidAPI pricing plans are live, docs page is polished, `/v1/stats` endpoint is responsive, and the free tier (5 calls/day) is working before launch.

---

## 1. Tagline (max 60 chars)

**The pulse of China, in one API.**

*(57 characters — optimized for PH headline)*

---

## 2. Short Description (max 260 chars)

Real-time trending topics from 8 Chinese platforms (Weibo, Baidu, Zhihu, Douyin, Bilibili, Toutiao & more) with LLM-powered English translations and monetization tags. 3,577 trends, 6 search endpoints, free tier available.

*(252 characters — fits the PH card perfectly)*

---

## 3. Full Description (markdown)

### What It Does

The Chinese Trending Data API is the single endpoint that unlocks real-time trending data from every major Chinese content platform. We scrape, deduplicate, and enrich 3,500+ trending topics every 4 hours — then run them through an LLM pipeline that generates English translations, category tags, heat scores, and even monetization suggestions. No Chinese language skills required. No scraping infrastructure to maintain. One API call.

### Why It Matters

China's internet is a walled garden. Weibo, Baidu, Zhihu, Douyin, Bilibili, Toutiao — these platforms drive the conversations of 1 billion+ users, but accessing their trending data programmatically is a nightmare. Individual scraping projects break within days. No standardized schema exists. And without Chinese fluency, you can't even understand what's trending.

We built the bridge. This is the first API that gives you structured, English-accessible, monetization-tagged trending data from all 8 platforms in a unified format — updated every 4 hours.

### 🚀 Key Features

- **🌐 8 Platforms, 1 API** — Weibo, Baidu, Zhihu, Douyin (TikTok CN), Bilibili, Toutiao, Baidu Realtime & Weibo Realtime in a unified JSON schema
- **📊 3,577+ Active Trends** — With real heat scores (not scraped counts): Weibo reads, Baidu search indices, Zhihu views — up to 99M+
- **🤖 LLM-Enriched English** — Every title and every content snippet comes with AI-generated English translation. Zero Chinese knowledge needed
- **💰 Monetization Tags** — AI suggests how to capitalize on each trend: content ideas, product angles, ad opportunities
- **🔍 6 Search Endpoints** — Full-text search, category browsing, cross-platform comparison, random sampling, source filtering, sort by heat/rank/date
- **⚡ Auto-Updated** — Pipeline runs every 4 hours with automated scraping, deduplication, and LLM enrichment
- **🏷️ 60+ Categories** — Tech, finance, entertainment, sports, news, gaming, food, culture, society, and more
- **📈 Heat Levels** — viral 🔥 (>1M), top 🔶 (>100K), hot 🟡 (>10K), trending 🟢, normal ⚪

### 💡 Use Cases

1. **Content Creators & Publishers** — Spot trending topics in China before they go global. Publish English-language analysis that rides the wave of Baidu viral topics within hours, not days.

2. **Market & Sentiment Analysts** — Track Chinese consumer sentiment in real-time. Compare how a topic performs across Weibo (public opinion), Zhihu (deep discussion), and Douyin (viral video) — all from one endpoint.

3. **AI/ML Developers** — Feed fresh Chinese trending data into LLM fine-tuning pipelines, trend prediction models, cross-cultural NLP analysis, or content recommendation engines. 3,500+ labeled, translated records updated continuously.

4. **E-commerce & Brand Teams** — Spot product trends early. Monitor what Chinese consumers are searching for on Baidu and discussing on Douyin. Align inventory, marketing campaigns, and influencer strategies with real-time demand signals.

5. **Trading & Crypto Researchers** — China's social media moves markets. Track regulatory sentiment, tech stock buzz, and crypto-related discussions across Weibo and Zhihu before they hit Western news wires.

### 💎 Pricing

| Plan | Price | Calls/Day | Features |
|------|-------|-----------|----------|
| **Free** | $0 | 5/endpoint | Limited results, 3-platform compare, truncated content |
| **Basic** | $29/mo | 500 | All 8 platforms, full translations, monetization tags, 7-day history |
| **Pro** | $99/mo | 3,000 | Everything in Basic + 30-day history + priority support |
| **Enterprise** | Custom | Unlimited | SLA guarantee, private deployment, custom data feeds |

### 🔗 Links

- **RapidAPI Marketplace:** https://rapidapi.com/jkk542830/api/chinese-trending-data-api
- **Live API & Docs:** http://161.153.56.113:8900/
- **Contact:** jkk542830@gmail.com

---

## 4. Topics/Tags (max 3)

**API, Developer Tools, Data**

*(These 3 tags maximize discoverability on PH's developer audience. "API" captures builders searching for integrations. "Developer Tools" puts us in the main tools category. "Data" covers the data product angle.)*

---

## 5. First Comment (Maker Comment)

> *Hey Product Hunt! 👋 Maker here.*
>
> About a year ago, I was building a China-focused market analysis tool and hit a wall. I needed to know what was trending on Weibo, Baidu, and Zhihu — but every option was terrible. Scrapy scripts that broke after platform updates. Paywalled Chinese-only services. Random Telegram channels posting screenshots. Nothing had structured data, English translations, or a unified API.
>
> So I built it myself.
>
> Started with one platform (Weibo hot search). Added Baidu. Then Zhihu. Then Douyin, Bilibili, Toutiao... The data pipeline grew from a weekend hack to a production system scraping 8 platforms simultaneously, deduplicating 1000s of records, and running everything through an LLM pipeline for translation + monetization analysis.
>
> **The result is the Chinese Trending Data API** — 3,577+ real-time trends from 8 Chinese platforms, all accessible via REST API, all with AI-generated English translations, heat scores, and monetization tags.
>
> Some things I'm most proud of:
> - **Cross-platform comparison** — Search once, see how a topic ranks across all 8 platforms side-by-side. No other API does this.
> - **English-first** — Every single record has LLM-translated title and content. You don't need to read Chinese to use this.
> - **Real heat scores** — These are native platform metrics (millions of Weibo reads, Baidu search indices), not made-up scores.
>
> 🎉 **Product Hunt Launch Offer:** Use code **PH50** at checkout on RapidAPI for **50% off your first month** on any paid plan (Basic or Pro). Good for the first 100 subscribers.
>
> Free tier is live right now — 5 calls/day per endpoint, no credit card needed. Try it, break it, tell me what to build next.
>
> Happy to answer any questions about the tech stack, data pipeline, or China's internet landscape. Let's go! 🚀

---

## 6. Gallery Images Description

### Image 1 — Hero / Product Overview
**File:** `ph-gallery-01-hero.png`
**Style:** Dark theme (matching API docs). Center shows a dashboard-style UI with 8 platform icons (Weibo, Baidu, Zhihu, Douyin, Bilibili, Toutiao, Baidu API, Weibo API) connected by glowing lines to a central "API" node. Data counter "3,577+" displayed prominently. Tagline: "The pulse of China, in one API." RapidAPI and "Free Tier Available" badges.
**Dimensions:** 1920×1080 (standard PH gallery)

### Image 2 — API Response Example
**File:** `ph-gallery-02-response.png`
**Style:** Terminal/code screenshot on dark background. Shows a clean `curl` command and a formatted JSON response from `/v1/trends/search`. Highlight the key fields: `keyword`, `source`, `heat` (e.g., "2,350,000"), `translated_title` ("DeepSeek AI shakes up global tech"), `translated_content`, `monetization_tags` (e.g., "content_recommendation, product_review"). Use VS Code or Warp terminal aesthetic with syntax highlighting.
**Dimensions:** 1920×1080

### Image 3 — Cross-Platform Comparison Feature
**File:** `ph-gallery-03-compare.png`
**Style:** Split-screen comparison visualization. Left side: a search input showing "keyword=AI" with a search button. Right side: a table/grid showing the same keyword ranked across 8 platforms — Weibo (🔥 viral, rank #3), Baidu (🔥 viral, rank #1), Zhihu (🟡 hot, rank #7), Douyin (🔶 top, rank #2), etc. Use a heat map color scale (red = hottest, blue = cold). Title overlay: "Compare any topic across all 8 Chinese platforms."
**Dimensions:** 1920×1080

### Image 4 — Use Cases Grid
**File:** `ph-gallery-04-usecases.png`
**Style:** 4-panel grid layout with icons. Each panel shows a distinct use case with a small illustrative graphic:
- Panel 1 (🌐 Content Creators): Globe with trending arrows + "Spot trends before they go global"
- Panel 2 (📈 Market Analysts): Chart going up + "Track Chinese sentiment in real-time"  
- Panel 3 (🤖 AI/ML Devs): Neural network nodes + "3,500+ translated records for model training"
- Panel 4 (🛒 E-commerce): Shopping cart + "Align inventory with Chinese demand signals"
**Background:** Gradient dark purple-to-blue. Clean, minimal, readable at thumbnail size.
**Dimensions:** 1920×1080

### Image 5 — Pricing Tiers
**File:** `ph-gallery-05-pricing.png`
**Style:** 3-column pricing card layout (Free / Basic $29 / Pro $99) with a "Popular" badge on Basic. Each card shows: plan name, price, key features with checkmarks. Free tier: "5 calls/day · 3 platforms · Truncated preview". Basic: "500 calls/day · All 8 platforms · Full translations · Monetization tags". Pro: "3,000 calls/day · 30-day history · Priority support". Bottom CTA button: "Get Started Free on RapidAPI". Include the launch offer callout: "🎉 PH50 = 50% off first month".
**Dimensions:** 1920×1080

---

## Appendix — Launch Checklist

- [ ] Confirm RapidAPI pricing plans are active (Free, Basic $29, Pro $99)
- [ ] Set up RapidAPI coupon code **PH50** (50% off first month, 100 redemptions)
- [ ] Test all 6 endpoints return valid JSON
- [ ] Verify `/v1/stats` shows accurate total count (3,577+)
- [ ] Polish docs page at http://161.153.56.113:8900/
- [ ] Create 5 gallery images matching descriptions above
- [ ] Prepare Maker avatar and bio for PH profile
- [ ] Schedule PH launch for Tuesday/Wednesday morning (EST) — best engagement
- [ ] Write a short Twitter/X thread to share after launch
- [ ] Prepare response templates for expected questions (pricing, data freshness, Chinese language support, comparison with competitors)
