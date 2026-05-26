from fastapi import FastAPI, Depends, HTTPException, Security, status, Query, Request
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import json
from pathlib import Path
from fastapi.responses import HTMLResponse
import sys
from pathlib import Path
from datetime import date

# 添加request_logger模块
sys.path.insert(0, str(Path(__file__).parent))
import request_logger

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Arbitrage High-Value Niche Data API", version="2.2.0",
              description="多平台中文热点数据API — 真实热度 + LLM增强分析 + 变现建议")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── 免费层配置 ───
FREE_TIER_LIMITS = {
    "/v1/trends/search": 3,
    "/v1/trends/sample": 2,
}

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
    return {"status": "healthy", "version": "2.2.0", "database": "clean_data.db", "sources": 8}


# ─── API调用日志中间件 ───
@app.middleware("http")
async def log_api_usage(request: Request, call_next):
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

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/clean_data.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="Clean database not initialized.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT id, keyword, source, original_id, title, content_clean, source_url, heat, rank, heat_level, category, tags, translated_title, translated_content, monetization_tags, updated_at FROM clean_trend WHERE 1=1"
    params = []

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
    params.extend([limit, offset])

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8900)