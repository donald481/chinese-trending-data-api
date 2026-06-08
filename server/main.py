from fastapi import FastAPI, Depends, HTTPException, Security, status, Query, Request, BackgroundTasks
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3
import os
import json
import uuid
import asyncio
import httpx
from pathlib import Path
from fastapi.responses import HTMLResponse
import sys
from pathlib import Path
from datetime import date, datetime, timedelta

# 添加request_logger模块
sys.path.insert(0, str(Path(__file__).parent))
import request_logger

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Arbitrage High-Value Niche Data API", version="2.4.0",
              description="多平台中文热点数据API — 真实热度 + LLM增强分析 + 变现建议 + Webhook通知")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── 免费层配置 ───
FREE_TIER_LIMITS = {
    "/v1/trends/search": 3,
    "/v1/trends/sample": 2,
    "/v1/trends/by-category": 3,
    "/v1/trends/compare": 3,
}

# ─── 数据库路径 ───
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/clean_data.db")

# ─── Webhook SQLite表 ───
def init_webhooks_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS webhooks (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            categories TEXT,
            min_heat INTEGER,
            source_filter TEXT,
            event_type TEXT DEFAULT 'new_trend',
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            last_delivery_at TEXT,
            delivery_count INTEGER DEFAULT 0,
            tier TEXT DEFAULT 'free'
        )
    """)
    conn.commit()
    conn.close()

# ─── Webhook Pydantic Models ───
class WebhookCreateRequest(BaseModel):
    url: str = Field(..., description="Webhook callback URL")
    categories: Optional[List[str]] = Field(None, description="Filter: only these categories")
    min_heat: Optional[int] = Field(None, description="Filter: minimum heat score")
    source_filter: Optional[List[str]] = Field(None, description="Filter: only these sources")
    event_type: Optional[str] = Field("new_trend", pattern="^(new_trend|viral_alert|daily_digest)$")

class WebhookCreateResponse(BaseModel):
    webhook_id: str
    status: str

class WebhookResponse(BaseModel):
    id: str
    url: str
    categories: Optional[str] = None
    min_heat: Optional[int] = None
    source_filter: Optional[str] = None
    event_type: str
    is_active: bool
    created_at: str
    last_delivery_at: Optional[str] = None
    delivery_count: int
    tier: str

# ─── Startup ───
@app.on_event("startup")
async def startup():
    init_webhooks_db()
    asyncio.create_task(webhook_delivery_loop())

async def get_user_tier(api_key: str) -> str:
    """Determine user tier: 'free' or 'paid'"""
    if api_key == "[free]":
        return "free"
    return "paid"

# ─── API 鉴权 ───
# ─── API 鉴权 (支持直接访问 & RapidAPI代理) ───
ALLOWED_KEYS = ["client_test_key_abc"]
env_keys = os.getenv("ARBITRAGE_API_KEYS", "")
if env_keys:
    ALLOWED_KEYS.extend([k.strip() for k in env_keys.split(",") if k.strip()])

RAPIDAPI_SECRET = os.getenv("RAPIDAPI_PROXY_SECRET", "")

async def verify_api_key(request: Request):
    # 直接访问: X-API-KEY 或 X-RapidAPI-Key
    api_key = request.headers.get("X-API-KEY") or request.headers.get("X-RapidAPI-Key") or ""
    
    # RapidAPI 代理模式: 验证 Proxy-Secret
    proxy_secret = request.headers.get("X-RapidAPI-Proxy-Secret", "")
    if proxy_secret and RAPIDAPI_SECRET and proxy_secret == RAPIDAPI_SECRET:
        request.state.api_key_type = "rapidapi"
        return "[rapidapi_proxy]"
    
    if api_key in ALLOWED_KEYS:
        request.state.api_key_type = "paid"
        return api_key
    
    # 免费层：无Key时允许有限访问
    request.state.api_key_type = "free"
    return "[free]"


# ─── 免费层限额检查 ───
async def check_free_tier_limit(request: Request, api_key: str):
    """对免费用户检查每日调用限额"""
    if api_key != "[free]":
        return  # 付费用户不受限制
    
    ip = get_remote_address(request)
    endpoint = str(request.url.path)
    limit = FREE_TIER_LIMITS.get(endpoint)
    if limit is None:
        return  # 该endpoint不限制免费调用
    
    daily_count = request_logger.get_daily_count(ip, endpoint)
    if daily_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": f"Free tier daily limit reached ({limit} calls/day for {endpoint}). Upgrade for unlimited access.",
                "upgrade_url": "https://rapidapi.com/jkk542830/api/chinese-trending-data-api",
                "plans": {"basic": "$29/mo - 500 calls/day", "pro": "$99/mo - 3000 calls/day", "enterprise": "Custom - unlimited"},
                "remaining_today": 0
            }
        )


# ─── 响应模型（高价值数据维度）───
class TrendResponse(BaseModel):
    id: int
    keyword: str
    source: str
    original_id: str
    title: str
    content_clean: str
    source_url: Optional[str] = None
    heat: Optional[int] = None
    rank: Optional[int] = None
    heat_level: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    translated_title: Optional[str] = None
    translated_content: Optional[str] = None
    monetization_tags: Optional[str] = None
    updated_at: str


# ─── 文档站 ───
@app.get("/", response_class=HTMLResponse)
@app.get("/docs-site", response_class=HTMLResponse)
async def docs_page():
    docs_path = Path(__file__).parent / "docs_page.html"
    if docs_path.exists():
        return HTMLResponse(content=docs_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Arbitrage API</h1><p>Documentation page not found.</p>")


# ─── 健康检查 ───
@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.4.0", "database": "clean_data.db", "sources": 8}


# ─── API调用日志中间件（含RapidAPI subscriber追踪）───
@app.middleware("http")
async def log_api_usage(request: Request, call_next):
    # 提取RapidAPI subscriber信息（RapidAPI代理模式自动注入的headers）
    rapidapi_subscriber = request.headers.get("X-RapidAPI-Subscriber", "")
    rapidapi_plan = request.headers.get("X-RapidAPI-Plan", "")
    user_agent = request.headers.get("User-Agent", "")[:500]  # 截断防止超长
    request_id = request.headers.get("X-RapidAPI-Request-ID", "")

    response = await call_next(request)

    # 获取API Key类型（由verify_api_key设置在request.state中）
    api_key_type = getattr(request.state, "api_key_type", "free")

    # 有选择地记录（排除文档/健康检查等）
    path = request.url.path
    if path not in ("/", "/health", "/docs-site", "/docs", "/openapi.json", "/favicon.ico"):
        request_logger.log_api_call(
            ip=get_remote_address(request),
            endpoint=path,
            api_key_type=api_key_type,
            response_status=response.status_code,
            rapidapi_subscriber=rapidapi_subscriber or None,
            rapidapi_plan=rapidapi_plan or None,
            user_agent=user_agent or None,
            request_id=request_id or None,
        )

    # 为免费用户添加剩余额度响应头
    if api_key_type == "free" and path in FREE_TIER_LIMITS:
        daily_count = request_logger.get_daily_count(get_remote_address(request), path)
        limit = FREE_TIER_LIMITS[path]
        remaining = max(0, limit - daily_count)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        if remaining <= 1:
            response.headers["X-Upgrade-URL"] = "https://rapidapi.com/jkk542830/api/chinese-trending-data-api"

    return response


# ─── 核心数据查询 ───
@app.get("/v1/trends/search", response_model=List[TrendResponse])
@limiter.limit("60/minute")
async def search_trends(
    request: Request,
    q: Optional[str] = Query(None, description="🔍 Full-text search across keyword, title & content"),
    keyword: Optional[str] = Query(None, description="关键词搜索（模糊匹配标题/标签）"),
    source: Optional[str] = Query(None, description="数据来源: weibo / baidu / zhihu / douyin / bilibili / toutiao / baidu_api / weibo_api"),
    category: Optional[str] = Query(None, description="分类筛选: 科技 / 娱乐 / 社会 / 汽车等"),
    heat_level: Optional[str] = Query(None, description="热度级别: trending / hot / top / viral / normal"),
    min_heat: Optional[int] = Query(None, description="最低热度值"),
    max_heat: Optional[int] = Query(None, description="最高热度值"),
    sort_by: Optional[str] = Query("heat_desc", description="排序: heat_desc / heat_asc / rank_asc / newest"),
    limit: int = Query(default=20, ge=1, le=100, description="返回条数(1-100)"),
    offset: int = Query(default=0, ge=0, description="分页偏移"),
    api_key: str = Depends(verify_api_key)
):
    """查询热点数据——真实热度 + LLM增强标签 + 变现建议"""

    # 免费层限额检查
    await check_free_tier_limit(request, api_key)

    is_free = (api_key == "[free]")
    effective_limit = min(limit, 5) if is_free else limit

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/clean_data.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="Clean database not initialized.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT id, keyword, source, original_id, title, content_clean, source_url, heat, rank, heat_level, category, tags, translated_title, translated_content, monetization_tags, updated_at FROM clean_trend WHERE 1=1"
    params = []

    # Full-text search via `q` — across keyword, title, and content_clean
    if q:
        query += " AND (keyword LIKE ? OR title LIKE ? OR content_clean LIKE ?)"
        like = f"%{q}%"
        params.extend([like, like, like])

    # Backward-compatible keyword search (searches keyword, tags, translated_title)
    if keyword:
        query += " AND (keyword LIKE ? OR tags LIKE ? OR translated_title LIKE ?)"
        like = f"%{keyword}%"
        params.extend([like, like, like])

    if source:
        query += " AND source = ?"
        params.append(source)

    if category:
        query += " AND category LIKE ?"
        params.append(f"%{category}%")

    if heat_level:
        query += " AND heat_level = ?"
        params.append(heat_level)

    if min_heat is not None:
        query += " AND heat >= ?"
        params.append(min_heat)

    if max_heat is not None:
        query += " AND heat <= ?"
        params.append(max_heat)

    # 排序
    sort_map = {
        "heat_desc": " ORDER BY heat DESC, updated_at DESC",
        "heat_asc": " ORDER BY heat ASC, updated_at DESC",
        "rank_asc": " ORDER BY rank ASC, updated_at DESC",
        "newest": " ORDER BY updated_at DESC, heat DESC",
    }
    query += sort_map.get(sort_by, " ORDER BY heat DESC, updated_at DESC")
    query += f" LIMIT ? OFFSET ?"
    params.extend([effective_limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    results = [
    TrendResponse(
        id=r[0], keyword=r[1], source=r[2], original_id=r[3],
        title=r[4], content_clean=r[5], source_url=r[6],
        heat=r[7], rank=r[8], heat_level=r[9], category=r[10],
        tags=r[11], translated_title=r[12], translated_content=r[13],
        monetization_tags=r[14], updated_at=str(r[15])
    ) for r in rows
    ]

    # 免费用户截断高价值字段（展示数据存在，引导付费解锁完整内容）
    if is_free:
        for item in results:
            item.monetization_tags = "🔒 Upgrade to unlock"
            item.translated_content = (item.translated_content[:80] + "... 🔒") if item.translated_content and len(item.translated_content) > 80 else item.translated_content
            item.content_clean = (item.content_clean[:120] + "... 🔒") if item.content_clean and len(item.content_clean) > 120 else item.content_clean

    return results


# ─── Feature 2: By-category browsing ───
@app.get("/v1/trends/by-category", response_model=dict)
@limiter.limit("30/minute")
async def trends_by_category(
    request: Request,
    category: Optional[str] = Query(None, description="Filter by specific category name"),
    limit: int = Query(default=20, ge=1, le=100, description="Results per category (1-100)"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    api_key: str = Depends(verify_api_key)
):
    """Browse trends grouped by category — shows available categories with counts"""

    await check_free_tier_limit(request, api_key)
    is_free = (api_key == "[free]")
    effective_limit = min(limit, 5) if is_free else limit

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/clean_data.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="Database not initialized.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all available categories with counts
    if category:
        cursor.execute(
            "SELECT category, COUNT(*) FROM clean_trend WHERE category LIKE ? GROUP BY category ORDER BY COUNT(*) DESC",
            (f"%{category}%",)
        )
    else:
        cursor.execute(
            "SELECT category, COUNT(*) FROM clean_trend WHERE category IS NOT NULL AND category != '' GROUP BY category ORDER BY COUNT(*) DESC"
        )
    categories_raw = cursor.fetchall()

    result = {}
    for cat_name, cat_count in categories_raw:
        if not cat_name:
            continue

        # For free tier, only return up to 5 results per category
        per_category_limit = effective_limit
        cursor.execute(
            "SELECT id, keyword, source, original_id, title, content_clean, source_url, heat, rank, heat_level, category, tags, translated_title, translated_content, monetization_tags, updated_at FROM clean_trend WHERE category LIKE ? ORDER BY heat DESC LIMIT ? OFFSET ?",
            (f"%{cat_name}%", per_category_limit, offset)
        )
        rows = cursor.fetchall()

        trends = [
            TrendResponse(
                id=r[0], keyword=r[1], source=r[2], original_id=r[3],
                title=r[4], content_clean=r[5], source_url=r[6],
                heat=r[7], rank=r[8], heat_level=r[9], category=r[10],
                tags=r[11], translated_title=r[12], translated_content=r[13],
                monetization_tags=r[14], updated_at=str(r[15])
            ) for r in rows
        ]

        # Free tier: truncate sensitive fields
        if is_free:
            for item in trends:
                item.monetization_tags = "🔒 Upgrade to unlock"
                item.translated_content = (item.translated_content[:80] + "... 🔒") if item.translated_content and len(item.translated_content) > 80 else item.translated_content
                item.content_clean = (item.content_clean[:120] + "... 🔒") if item.content_clean and len(item.content_clean) > 120 else item.content_clean

        result[cat_name] = {
            "total_in_category": cat_count,
            "trends": [t.dict() for t in trends]
        }

    conn.close()

    return {
        "categories_count": len(result),
        "categories": result,
        "showing": f"{'free (max 5 per category)' if is_free else 'full'}"
    }


# ─── Feature 3: Cross-platform comparison ───
@app.get("/v1/trends/compare", response_model=dict)
@limiter.limit("30/minute")
async def compare_trends(
    request: Request,
    keyword: str = Query(..., description="Keyword to compare across platforms"),
    api_key: str = Depends(verify_api_key)
):
    """Cross-platform comparison — see how a topic ranks across all 8 Chinese platforms"""

    await check_free_tier_limit(request, api_key)
    is_free = (api_key == "[free]")

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/clean_data.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="Database not initialized.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Search for this keyword across all platforms
    like = f"%{keyword}%"
    cursor.execute(
        "SELECT id, keyword, source, original_id, title, content_clean, source_url, heat, rank, heat_level, category, tags, translated_title, translated_content, monetization_tags, updated_at FROM clean_trend WHERE keyword LIKE ? OR title LIKE ? OR content_clean LIKE ? ORDER BY heat DESC",
        (like, like, like)
    )
    rows = cursor.fetchall()
    conn.close()

    # Group by platform
    platform_order = ["weibo", "baidu", "zhihu", "douyin", "bilibili", "toutiao", "baidu_api", "weibo_api"]
    by_platform = {}

    for r in rows:
        src = r[2]
        if src not in by_platform:
            by_platform[src] = {
                "platform": src,
                "matches_found": 0,
                "top_result": None,
                "max_heat": 0,
                "best_rank": None
            }

        by_platform[src]["matches_found"] += 1
        if r[7] and r[7] > by_platform[src]["max_heat"]:
            by_platform[src]["max_heat"] = r[7]
            by_platform[src]["best_rank"] = r[8]
            by_platform[src]["top_result"] = {
                "keyword": r[1],
                "title": r[4],
                "heat": r[7],
                "rank": r[8],
                "heat_level": r[9],
                "category": r[10]
            }

    # Sort platforms: those with matches first, then by heat desc
    platform_order_sorted = sorted(platform_order, key=lambda p: by_platform[p]["max_heat"] if p in by_platform else -1, reverse=True)

    comparison = []
    limited_platforms = 3 if is_free else 8

    for idx, src in enumerate(platform_order_sorted):
        if idx >= limited_platforms:
            break
        if src in by_platform:
            comparison.append(by_platform[src])
        else:
            comparison.append({
                "platform": src,
                "matches_found": 0,
                "top_result": None,
                "max_heat": 0,
                "best_rank": None
            })

    return {
        "keyword": keyword,
        "total_matches": len(rows),
        "platforms_with_matches": len([p for p in by_platform if by_platform[p]["matches_found"] > 0]),
        "comparison": comparison,
        "tier": "free (3 platforms only)" if is_free else "paid (all 8 platforms)",
        "upgrade_url": "https://rapidapi.com/jkk542830/api/chinese-trending-data-api" if is_free else None
    }


# ─── 数据统计摘要（无需鉴权，用于吸引客户）───
@app.get("/v1/stats")
async def stats():
    """数据概览——数据量、来源分布、热度统计"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/clean_data.db")
    if not os.path.exists(db_path):
        return {"total": 0}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    total = cursor.execute("SELECT COUNT(*) FROM clean_trend").fetchone()[0]
    sources = cursor.execute("SELECT source, COUNT(*) FROM clean_trend GROUP BY source").fetchall()
    heat_levels = cursor.execute("SELECT heat_level, COUNT(*) FROM clean_trend GROUP BY heat_level").fetchall()
    avg_heat = cursor.execute("SELECT AVG(heat) FROM clean_trend WHERE heat > 0").fetchone()[0]
    max_heat = cursor.execute("SELECT MAX(heat) FROM clean_trend").fetchone()[0]
    categories = cursor.execute("SELECT category, COUNT(*) FROM clean_trend GROUP BY category ORDER BY COUNT(*) DESC").fetchall()
    updated = cursor.execute("SELECT MAX(updated_at) FROM clean_trend").fetchone()[0]

    conn.close()
    return {
        "total_trends": total,
        "sources": {s: c for s, c in sources},
        "heat_levels": {h: c for h, c in heat_levels},
        "avg_heat": round(avg_heat) if avg_heat else 0,
        "max_heat": max_heat,
        "categories": {c: n for c, n in categories},
        "last_updated": str(updated) if updated else None
    }


# ─── 随机采样（展示数据质量用）───
@app.get("/v1/trends/sample", response_model=List[TrendResponse])
@limiter.limit("30/minute")
async def sample_trends(
    request: Request,
    count: int = Query(default=3, ge=1, le=10),
    api_key: str = Depends(verify_api_key)
):
    """随机采样——让客户预览数据质量"""

    # 免费层限额检查
    await check_free_tier_limit(request, api_key)

    is_free = (api_key == "[free]")

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/clean_data.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="Database not initialized.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, keyword, source, original_id, title, content_clean, source_url, heat, rank, heat_level, category, tags, translated_title, translated_content, monetization_tags, updated_at FROM clean_trend ORDER BY RANDOM() LIMIT ?",
        (count,)
    )
    rows = cursor.fetchall()
    conn.close()
    results = [
    TrendResponse(
        id=r[0], keyword=r[1], source=r[2], original_id=r[3],
        title=r[4], content_clean=r[5], source_url=r[6],
        heat=r[7], rank=r[8], heat_level=r[9], category=r[10],
        tags=r[11], translated_title=r[12], translated_content=r[13],
        monetization_tags=r[14], updated_at=str(r[15])
    ) for r in rows
    ]

    # 免费用户截断高价值字段
    if is_free:
        for item in results:
            item.monetization_tags = "🔒 Upgrade to unlock"
            item.translated_content = (item.translated_content[:80] + "... 🔒") if item.translated_content and len(item.translated_content) > 80 else item.translated_content
            item.content_clean = (item.content_clean[:120] + "... 🔒") if item.content_clean and len(item.content_clean) > 120 else item.content_clean

    return results


# ─── Webhook: Helper Functions ───
def get_webhook_count_for_tier(api_key: str) -> int:
    """Get current webhook count for this user by IP."""
    if api_key == "[free]":
        return 1  # free tier limit
    return 10  # paid tier limit

async def validate_webhook_url(url: str) -> bool:
    """Validate URL is reachable via HEAD request."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.head(url, follow_redirects=True)
            return resp.status_code < 500
    except Exception:
        return False

async def deliver_webhook(webhook_id: str, url: str, trend_data: dict) -> bool:
    """Send a POST request to a webhook URL with trend data."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=trend_data, headers={
                "Content-Type": "application/json",
                "User-Agent": "ArbitrageAPI-Webhook/2.4.0"
            })
            success = 200 <= resp.status_code < 300
    except Exception:
        success = False
    
    # Update delivery stats
    conn = sqlite3.connect(DB_PATH)
    if success:
        conn.execute(
            "UPDATE webhooks SET delivery_count = delivery_count + 1, last_delivery_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), webhook_id)
        )
    else:
        conn.execute(
            "UPDATE webhooks SET last_delivery_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), webhook_id)
        )
    conn.commit()
    conn.close()
    return success


async def webhook_delivery_loop():
    """Background task: periodically check for new trends and deliver to matching webhooks."""
    await asyncio.sleep(10)  # give startup time
    while True:
        try:
            await process_webhook_deliveries()
        except Exception as e:
            print(f"[Webhook] Delivery loop error: {e}")
        await asyncio.sleep(3600)  # check every hour


async def process_webhook_deliveries():
    """Check webhooks and deliver matching trends."""
    now = datetime.utcnow()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Get all active webhooks
    cursor = conn.execute("SELECT * FROM webhooks WHERE is_active = 1")
    webhooks = [dict(r) for r in cursor.fetchall()]
    
    if not webhooks:
        conn.close()
        return
    
    # Get recent trends (last 1 hour for paid, last 6 hours for free)
    paid_cutoff = (now - timedelta(hours=1)).isoformat()
    free_cutoff = (now - timedelta(hours=6)).isoformat()
    
    for wh in webhooks:
        tier = wh.get("tier", "free")
        cutoff = paid_cutoff if tier == "paid" else free_cutoff
        
        # Build query for matching trends
        query = "SELECT id, keyword, source, title, content_clean, heat, heat_level, category, tags, monetization_tags, updated_at FROM clean_trend WHERE updated_at >= ?"
        params = [cutoff]
        
        if wh.get("categories"):
            cats = json.loads(wh["categories"]) if isinstance(wh["categories"], str) else wh["categories"]
            if cats:
                placeholders = " OR ".join(["category LIKE ?" for _ in cats])
                query += f" AND ({placeholders})"
                params.extend([f"%{c}%" for c in cats])
        
        if wh.get("min_heat"):
            query += " AND heat >= ?"
            params.append(wh["min_heat"])
        
        if wh.get("source_filter"):
            sources = json.loads(wh["source_filter"]) if isinstance(wh["source_filter"], str) else wh["source_filter"]
            if sources:
                placeholders = " OR ".join(["source = ?" for _ in sources])
                query += f" AND ({placeholders})"
                params.extend(sources)
        
        query += " ORDER BY heat DESC LIMIT 20"
        
        try:
            cursor2 = conn.execute(query, params)
            trends = [dict(r) for r in cursor2.fetchall()]
        except Exception as e:
            print(f"[Webhook] Query error for {wh['id']}: {e}")
            continue
        
        if not trends:
            continue
        
        # If daily_digest event type, bundle all trends into one payload
        if wh.get("event_type") == "daily_digest":
            payload = {
                "event": "daily_digest",
                "webhook_id": wh["id"],
                "timestamp": now.isoformat(),
                "trends": trends
            }
            await deliver_webhook(wh["id"], wh["url"], payload)
        else:
            # Send each trend individually
            for trend in trends:
                payload = {
                    "event": wh.get("event_type", "new_trend"),
                    "webhook_id": wh["id"],
                    "timestamp": now.isoformat(),
                    "trend": trend
                }
                await deliver_webhook(wh["id"], wh["url"], payload)
    
    conn.close()


# ─── Webhook API Endpoints ───

@limiter.limit("10/minute")
@app.post("/v1/webhooks", response_model=WebhookCreateResponse)
async def create_webhook(
    request: Request,
    body: WebhookCreateRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a new webhook subscription."""
    tier = await get_user_tier(api_key)
    max_webhooks = get_webhook_count_for_tier(api_key)
    
    # Count existing webhooks for this IP/user
    ip = get_remote_address(request)
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM webhooks WHERE is_active = 1").fetchone()[0]
    
    if count >= max_webhooks:
        conn.close()
        extra_msg = " Upgrade to paid tier for up to 10 webhooks." if tier == "free" else ""
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Webhook limit reached ({max_webhooks}).{extra_msg}"
        )
    
    # Validate URL
    url_valid = await validate_webhook_url(body.url)
    if not url_valid:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook URL is not reachable. Please provide a valid, accessible URL."
        )
    
    webhook_id = str(uuid.uuid4())
    now_iso = datetime.utcnow().isoformat()
    
    conn.execute(
        """INSERT INTO webhooks (id, url, categories, min_heat, source_filter, event_type, created_at, tier)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            webhook_id,
            body.url,
            json.dumps(body.categories) if body.categories else None,
            body.min_heat,
            json.dumps(body.source_filter) if body.source_filter else None,
            body.event_type or "new_trend",
            now_iso,
            tier,
        )
    )
    conn.commit()
    conn.close()
    
    return WebhookCreateResponse(webhook_id=webhook_id, status="active")


@limiter.limit("10/minute")
@app.get("/v1/webhooks", response_model=List[WebhookResponse])
async def list_webhooks(
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """List all webhooks for this account (by IP)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM webhooks ORDER BY created_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    return [
        WebhookResponse(
            id=r["id"],
            url=r["url"],
            categories=r["categories"],
            min_heat=r["min_heat"],
            source_filter=r["source_filter"],
            event_type=r["event_type"],
            is_active=bool(r["is_active"]),
            created_at=r["created_at"],
            last_delivery_at=r["last_delivery_at"],
            delivery_count=r["delivery_count"],
            tier=r["tier"],
        )
        for r in rows
    ]


@limiter.limit("10/minute")
@app.delete("/v1/webhooks/{webhook_id}")
async def delete_webhook(
    request: Request,
    webhook_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete a webhook by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT id FROM webhooks WHERE id = ?", (webhook_id,))
    existing = cursor.fetchone()
    
    if not existing:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found.")
    
    conn.execute("DELETE FROM webhooks WHERE id = ?", (webhook_id,))
    conn.commit()
    conn.close()
    
    return {"status": "deleted", "webhook_id": webhook_id}


@limiter.limit("5/minute")
@app.post("/v1/webhooks/{webhook_id}/test")
async def test_webhook(
    request: Request,
    webhook_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Send a test event to a webhook URL."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM webhooks WHERE id = ?", (webhook_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found.")
    
    wh = dict(row)
    conn.close()
    
    test_payload = {
        "event": "test",
        "webhook_id": webhook_id,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "This is a test event from Chinese Trending Data API webhook system.",
        "trend": {
            "id": 0,
            "keyword": "[test] AI在中国的最新发展",
            "source": "weibo",
            "title": "AI在中国的最新发展",
            "heat": 5000000,
            "heat_level": "viral",
            "category": "科技"
        }
    }
    
    success = await deliver_webhook(webhook_id, wh["url"], test_payload)
    
    if success:
        return {"status": "sent", "webhook_id": webhook_id, "url": wh["url"]}
    else:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to deliver test event to {wh['url']}. Check the URL or make sure your endpoint is accessible."
        )


# ─── 用户追踪统计端点 ───
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "changeme_admin_key")

async def verify_admin(request: Request):
    """管理端点鉴权：Bearer token或query param"""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
    else:
        token = request.query_params.get("admin_key", "")
    if token != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin access required. Provide admin_key param or Bearer token.")
    return True


@app.get("/v1/users/stats")
async def users_stats(
    request: Request,
    day: Optional[str] = Query(None, description="统计日期 (YYYY-MM-DD), 默认今天"),
    _auth: bool = Depends(verify_admin),
):
    """用户追踪统计：按subscriber维度聚合，区分真实用户/Bot/探针"""
    subscriber_stats = request_logger.get_subscriber_stats(day)
    plan_distribution = request_logger.get_plan_distribution(day)
    real_users = request_logger.get_real_users(day, min_calls=2)

    # 汇总指标
    total_unique = len(subscriber_stats)
    total_calls = sum(s["total_calls"] for s in subscriber_stats)
    rapidapi_users = [s for s in subscriber_stats if s.get("rapidapi_subscriber")]
    direct_users = [s for s in subscriber_stats if not s.get("rapidapi_subscriber")]

    return {
        "day": day or date.today().isoformat(),
        "summary": {
            "total_unique_users": total_unique,
            "total_api_calls": total_calls,
            "rapidapi_subscribers": len(rapidapi_users),
            "direct_ip_users": len(direct_users),
            "real_users_count": len(real_users),
        },
        "plan_distribution": plan_distribution,
        "real_users": real_users[:50],  # 最多返回50个
        "all_users": subscriber_stats[:100],  # 完整列表截断
    }


@app.get("/v1/users/{subscriber_id}")
async def user_detail(
    request: Request,
    subscriber_id: str,
    days: int = Query(default=7, ge=1, le=90, description="回看天数"),
    _auth: bool = Depends(verify_admin),
):
    """单个用户的详细调用记录"""
    detail = request_logger.get_subscriber_detail(subscriber_id, days)
    return detail


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8900)