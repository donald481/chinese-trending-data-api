import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session

# ─── RawTrend: 原始抓取数据 ───
class RawTrend(SQLModel, table=True):
    __tablename__ = "raw_trend"
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str
    raw_id: str = Field(index=True, unique=True)
    payload: str  # JSON string of raw data
    scraped_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

# ─── CleanTrend: 清洗富化后数据（高价值维度）───
class CleanTrend(SQLModel, table=True):
    __tablename__ = "clean_trend"
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # ── 核心标识 ──
    keyword: str = Field(index=True)
    source: str
    original_id: str = Field(index=True, unique=True)
    
    # ── 标题和内容 ──
    title: str
    content_clean: str
    source_url: Optional[str] = None  # 原文或热点页链接
    
    # ── 真实热度指标（核心竞争力）──
    heat: Optional[int] = None         # 平台真实热度数值
    rank: Optional[int] = None         # 排名
    heat_level: Optional[str] = None   # 热度级别: trending / hot / viral / top
    category: Optional[str] = None     # 文本分类（娱乐/科技/社会/财经等，从平台直接获取）
    
    # ── LLM增强字段 ──
    tags: Optional[str] = None         # 行业标签（逗号分隔）
    translated_title: Optional[str] = None
    translated_content: Optional[str] = None
    monetization_tags: Optional[str] = None  # 变现方向标签（可带货品类）
    
    # ── 元数据 ──
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    first_seen_at: Optional[datetime.datetime] = None

# Database Engines
RAW_DB_URL = "sqlite:///data/raw_data.db"
CLEAN_DB_URL = "sqlite:///data/clean_data.db"

raw_engine = create_engine(RAW_DB_URL, echo=False)
clean_engine = create_engine(CLEAN_DB_URL, echo=False)

def init_db():
    """初始化数据库（建表）"""
    import os
    os.makedirs("data", exist_ok=True)
    RawTrend.__table__.create(raw_engine, checkfirst=True)
    CleanTrend.__table__.create(clean_engine, checkfirst=True)

def heat_to_level(heat: int) -> str:
    """热度数值 → 等级标签"""
    if heat >= 1000000:
        return "viral"
    elif heat >= 500000:
        return "top"
    elif heat >= 100000:
        return "hot"
    elif heat >= 10000:
        return "trending"
    return "normal"

if __name__ == "__main__":
    # 强制重建表（有数据变化时用）
    import sys
    if "--force" in sys.argv:
        CleanTrend.__table__.drop(clean_engine, checkfirst=True)
        RawTrend.__table__.drop(raw_engine, checkfirst=True)
        print("Old tables dropped.")
    init_db()
    print("Databases initialized successfully.")