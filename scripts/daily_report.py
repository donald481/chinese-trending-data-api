#!/usr/bin/env python3
"""
Daily monitoring report for Chinese Trending Data API.
Checks API health, queries DB for stats, outputs a compact Chinese report to stdout.
Designed to be run as a Hermes cron job with no_agent=True.
"""

import sqlite3
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── Configuration ───
# Resolve DB path — script may run from projects dir or ~/.hermes/scripts/
_script_dir = Path(__file__).resolve().parent
if (_script_dir.parent.name == ".hermes" and _script_dir.name == "scripts"):
    # Running from ~/.hermes/scripts/ — use absolute project path
    DB_PATH = Path("/home/ubuntu/projects/arbitrage_api/data/clean_data.db")
else:
    # Running from project directory
    DB_PATH = _script_dir.parent / "data" / "clean_data.db"
HEALTH_URL = "http://localhost:8900/health"
BEIJING_TZ = timezone(timedelta(hours=8))


def check_health() -> tuple[str, str]:
    """Returns (status_emoji, status_text)."""
    try:
        req = urllib.request.Request(HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "healthy":
                return "🟢", "healthy"
            return "🟡", data.get("status", "unknown")
    except Exception as e:
        return "🔴", f"down ({str(e)[:50]})"


def query_db() -> dict:
    """Query clean_data.db for all stats."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    result = {}

    # Total records
    cursor.execute("SELECT COUNT(*) FROM clean_trend")
    result["total"] = cursor.fetchone()[0]

    # Records updated in last 24h
    yesterday = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    cursor.execute(
        "SELECT COUNT(*) FROM clean_trend WHERE updated_at >= ?", (yesterday,)
    )
    result["updated_24h"] = cursor.fetchone()[0]

    # Source distribution
    cursor.execute(
        "SELECT source, COUNT(*) as cnt FROM clean_trend GROUP BY source ORDER BY cnt DESC"
    )
    result["sources"] = {row["source"]: row["cnt"] for row in cursor.fetchall()}

    # Heat level distribution
    cursor.execute(
        "SELECT heat_level, COUNT(*) as cnt FROM clean_trend GROUP BY heat_level ORDER BY cnt DESC"
    )
    result["heat_levels"] = {row["heat_level"]: row["cnt"] for row in cursor.fetchall()}

    # Top 5 categories
    cursor.execute(
        """SELECT category, COUNT(*) as cnt FROM clean_trend 
           WHERE category IS NOT NULL AND category != '' 
           GROUP BY category ORDER BY cnt DESC LIMIT 5"""
    )
    result["top_categories"] = {row["category"]: row["cnt"] for row in cursor.fetchall()}

    conn.close()
    return result


def format_kv(items: dict, sep: str = " | ") -> str:
    """Format a dict as 'key val key val ...' entries."""
    return sep.join(f"{k} {v}" for k, v in items.items())


def main():
    now_bj = datetime.now(BEIJING_TZ)
    time_str = now_bj.strftime("%Y-%m-%d %H:%M")

    # 1. Health check
    status_emoji, status_text = check_health()

    # 2. DB stats
    stats = query_db()

    # 3. Build report
    lines = [
        "📊 Chinese Trending API 日报",
        f"{status_emoji} 服务状态: {status_text}",
        f"💾 数据总量: {stats['total']:,}条 | 24h更新: {stats['updated_24h']:,}条",
    ]

    # Heat level distribution
    heat_str = format_kv(stats["heat_levels"])
    lines.append(f"🔥 热度分布: {heat_str}")

    # Top categories
    cat_str = format_kv(stats["top_categories"])
    lines.append(f"📂 Top分类: {cat_str}")

    # Source distribution
    src_str = format_kv(stats["sources"])
    lines.append(f"📡 数据源: {src_str}")

    # Timestamp
    lines.append(f"⏰ 更新时间: {time_str}")

    # Output
    report = "\n".join(lines)
    print(report)


if __name__ == "__main__":
    main()
