"""
API Request Logger - 记录所有API调用并支持按日/按IP/按Endpoint查询统计
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
    """初始化数据库和表结构"""
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ip TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            api_key_type TEXT NOT NULL,
            response_status INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_api_usage_ip_date
        ON api_usage_log(ip, timestamp)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint
        ON api_usage_log(endpoint, timestamp)
    """)
    conn.commit()
    conn.close()


def log_api_call(ip: str, endpoint: str, api_key_type: str, response_status: int):
    """记录一次API调用"""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO api_usage_log (timestamp, ip, endpoint, api_key_type, response_status) VALUES (?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), ip, endpoint, api_key_type, response_status),
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


# 模块导入时自动初始化数据库
init_db()
