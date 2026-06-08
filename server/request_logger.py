"""
API Request Logger - 记录所有API调用并支持按日/按IP/按Endpoint/按Subscriber查询统计
v2: 增加RapidAPI subscriber追踪字段
"""
import sqlite3
import os
from datetime import datetime, date
from typing import Optional, List, Dict

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_DB_PATH = os.path.join(_MODULE_DIR, "api_usage.db")


def _get_conn():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库和表结构（含subscriber追踪字段）"""
    conn = _get_conn()
    
    # 先检查表是否已存在
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_usage_log'")
    table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        # 全新建表（包含所有字段）
        conn.execute("""
        CREATE TABLE api_usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ip TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            api_key_type TEXT NOT NULL,
            response_status INTEGER NOT NULL,
            rapidapi_subscriber TEXT,
            rapidapi_plan TEXT,
            user_agent TEXT,
            request_id TEXT
        )
        """)
    else:
        # 旧表迁移：添加新列（幂等）
        existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(api_usage_log)").fetchall()}
        new_cols = {
            "rapidapi_subscriber": "TEXT",
            "rapidapi_plan": "TEXT",
            "user_agent": "TEXT",
            "request_id": "TEXT",
        }
        for col, col_type in new_cols.items():
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE api_usage_log ADD COLUMN {col} {col_type}")
    
    # 索引（幂等，IF NOT EXISTS）
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_api_usage_ip_date
    ON api_usage_log(ip, timestamp)
    """)
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint
    ON api_usage_log(endpoint, timestamp)
    """)
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_api_usage_subscriber
    ON api_usage_log(rapidapi_subscriber, timestamp)
    """)
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_api_usage_plan
    ON api_usage_log(rapidapi_plan, timestamp)
    """)
    conn.commit()
    conn.close()


def _migrate_add_columns():
    """迁移辅助（已合入init_db，保留为空函数以防import错误）"""
    pass


def log_api_call(
    ip: str,
    endpoint: str,
    api_key_type: str,
    response_status: int,
    rapidapi_subscriber: str = None,
    rapidapi_plan: str = None,
    user_agent: str = None,
    request_id: str = None,
):
    """记录一次API调用（含RapidAPI subscriber信息）"""
    conn = _get_conn()
    conn.execute(
        """INSERT INTO api_usage_log 
        (timestamp, ip, endpoint, api_key_type, response_status, 
         rapidapi_subscriber, rapidapi_plan, user_agent, request_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.utcnow().isoformat(),
            ip, endpoint, api_key_type, response_status,
            rapidapi_subscriber, rapidapi_plan, user_agent, request_id,
        ),
    )
    conn.commit()
    conn.close()


def get_daily_count(ip: str, endpoint: str) -> int:
    """获取某IP在某endpoint今天的免费调用次数（用于免费层限额检查）"""
    today = date.today().isoformat()
    conn = _get_conn()
    cursor = conn.execute(
        "SELECT COUNT(*) FROM api_usage_log WHERE ip = ? AND endpoint = ? AND api_key_type = 'free' AND timestamp >= ?",
        (ip, endpoint, today),
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_stats_by_day(day: Optional[str] = None) -> List[Dict]:
    """按日统计各endpoint的调用量"""
    if day is None:
        day = date.today().isoformat()
    conn = _get_conn()
    cursor = conn.execute(
        """
        SELECT endpoint, api_key_type, COUNT(*) as calls
        FROM api_usage_log
        WHERE timestamp >= ?
        GROUP BY endpoint, api_key_type
        ORDER BY calls DESC
        """,
        (f"{day}T00:00:00",),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_stats_by_ip(day: Optional[str] = None) -> List[Dict]:
    """按IP统计调用量"""
    if day is None:
        day = date.today().isoformat()
    conn = _get_conn()
    cursor = conn.execute(
        """
        SELECT ip, endpoint, api_key_type, COUNT(*) as calls
        FROM api_usage_log
        WHERE timestamp >= ?
        GROUP BY ip, endpoint
        ORDER BY calls DESC
        """,
        (f"{day}T00:00:00",),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_stats_by_endpoint(day: Optional[str] = None) -> List[Dict]:
    """按endpoint统计调用量和成功率"""
    if day is None:
        day = date.today().isoformat()
    conn = _get_conn()
    cursor = conn.execute(
        """
        SELECT endpoint, COUNT(*) as calls,
        SUM(CASE WHEN response_status >= 200 AND response_status < 300 THEN 1 ELSE 0 END) as success,
        SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as errors
        FROM api_usage_log
        WHERE timestamp >= ?
        GROUP BY endpoint
        ORDER BY calls DESC
        """,
        (f"{day}T00:00:00",),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# ─── 新增：Subscriber 维度查询 ───

def get_subscriber_stats(day: Optional[str] = None) -> List[Dict]:
    """按RapidAPI subscriber统计调用量"""
    if day is None:
        day = date.today().isoformat()
    conn = _get_conn()
    cursor = conn.execute(
        """
        SELECT 
            COALESCE(rapidapi_subscriber, ip) as user_id,
            rapidapi_subscriber,
            rapidapi_plan,
            ip,
            COUNT(*) as total_calls,
            COUNT(DISTINCT endpoint) as endpoints_used,
            MIN(timestamp) as first_call,
            MAX(timestamp) as last_call,
            SUM(CASE WHEN response_status >= 200 AND response_status < 300 THEN 1 ELSE 0 END) as success,
            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as errors
        FROM api_usage_log
        WHERE timestamp >= ?
        GROUP BY COALESCE(rapidapi_subscriber, ip)
        ORDER BY total_calls DESC
        """,
        (f"{day}T00:00:00",),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_subscriber_detail(subscriber_id: str, days: int = 7) -> Dict:
    """获取某个subscriber的详细调用记录"""
    conn = _get_conn()
    cursor = conn.execute(
        """
        SELECT 
            date(timestamp) as call_date,
            endpoint,
            rapidapi_plan,
            COUNT(*) as calls,
            SUM(CASE WHEN response_status >= 200 AND response_status < 300 THEN 1 ELSE 0 END) as success,
            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as errors
        FROM api_usage_log
        WHERE (rapidapi_subscriber = ? OR ip = ?)
          AND timestamp >= datetime('now', ?)
        GROUP BY date(timestamp), endpoint
        ORDER BY call_date DESC, calls DESC
        """,
        (subscriber_id, subscriber_id, f"-{days} days"),
    )
    daily = [dict(r) for r in cursor.fetchall()]
    
    # 概览
    cursor2 = conn.execute(
        """
        SELECT 
            COUNT(*) as total_calls,
            COUNT(DISTINCT date(timestamp)) as active_days,
            COUNT(DISTINCT endpoint) as endpoints_used,
            MIN(timestamp) as first_call,
            MAX(timestamp) as last_call
        FROM api_usage_log
        WHERE (rapidapi_subscriber = ? OR ip = ?)
          AND timestamp >= datetime('now', ?)
        """,
        (subscriber_id, subscriber_id, f"-{days} days"),
    )
    summary = dict(cursor2.fetchone())
    conn.close()
    
    return {"summary": summary, "daily_breakdown": daily}


def get_plan_distribution(day: Optional[str] = None) -> List[Dict]:
    """按RapidAPI plan统计调用量分布"""
    if day is None:
        day = date.today().isoformat()
    conn = _get_conn()
    cursor = conn.execute(
        """
        SELECT 
            COALESCE(rapidapi_plan, api_key_type) as plan,
            COUNT(*) as calls,
            COUNT(DISTINCT COALESCE(rapidapi_subscriber, ip)) as unique_users
        FROM api_usage_log
        WHERE timestamp >= ?
        GROUP BY COALESCE(rapidapi_plan, api_key_type)
        ORDER BY calls DESC
        """,
        (f"{day}T00:00:00",),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_real_users(day: Optional[str] = None, min_calls: int = 2) -> List[Dict]:
    """获取真实用户列表（排除Bot/探针：要求min_calls次以上且有具体endpoint调用）"""
    if day is None:
        day = date.today().isoformat()
    conn = _get_conn()
    cursor = conn.execute(
        """
        SELECT 
            COALESCE(rapidapi_subscriber, ip) as user_id,
            rapidapi_subscriber,
            rapidapi_plan,
            ip,
            COUNT(*) as total_calls,
            COUNT(DISTINCT endpoint) as endpoints_used,
            GROUP_CONCAT(DISTINCT endpoint) as endpoints,
            MIN(timestamp) as first_call,
            MAX(timestamp) as last_call
        FROM api_usage_log
        WHERE timestamp >= ?
          AND endpoint LIKE '/v1/%'
        GROUP BY COALESCE(rapidapi_subscriber, ip)
        HAVING total_calls >= ? AND endpoints_used >= 1
        ORDER BY total_calls DESC
        """,
        (f"{day}T00:00:00", min_calls),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# 模块导入时自动初始化数据库 + 迁移
init_db()
_migrate_add_columns()
