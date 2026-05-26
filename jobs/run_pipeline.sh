#!/bin/bash
# Arbitrage-API Data Pipeline v2.2
# 8源热点抓取(微博+百度+知乎+抖音+bilibili+头条+微博API+百度API) → DeepSeek v4 Flash富化 → API输出
set -euo pipefail
cd /home/ubuntu/projects/arbitrage_api

# Export API keys for cron environment
export DEEPSEEK_API_KEY="sk-36b76cc1ad4a4bce892b2e7414b60477"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"

source venv/bin/activate

mkdir -p logs

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ======= Phase 1: 多平台热点抓取 ======="
PYTHONPATH=. python3 scrapers/china_trends_aggregator.py 2>&1 | tee -a logs/scraper_$(date +%Y%m%d).log

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ======= Phase 2: DeepSeek v4 Flash富化 ======="
PYTHONPATH=. python3 pipeline/enricher.py 2>&1 | tee -a logs/enricher_$(date +%Y%m%d).log

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ======= 管道完成 ======="
echo "结构化日志: logs/enrichment.jsonl"

# Phase 3: 邮件通知
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ======= Phase 3: 发送邮件报告 ======="
SUBJECT="[Arbitrage API] 管道完成 $(date '+%Y-%m-%d %H:%M UTC')"

# 抓取统计
SCRAPER_NEW=$(grep -c "新增:" logs/scraper_$(date +%Y%m%d).log 2>/dev/null || echo "?")
SCRAPER_UPD=$(grep -c "更新:" logs/scraper_$(date +%Y%m%d).log 2>/dev/null || echo "?")

# 富化统计 (取最后一行富化完成行)
ENRICH_SUMMARY=$(grep "富化完成:" logs/enricher_$(date +%Y%m%d).log 2>/dev/null | tail -1 || echo "富化: 无数据")

# API 统计
API_STATS=$(curl -s http://localhost:8900/v1/stats 2>/dev/null || echo '{"total_trends":"?","avg_heat":"?"}')

# 构建邮件正文
{
  echo "Subject: ${SUBJECT}"
  echo "Content-Type: text/plain; charset=UTF-8"
  echo ""
  echo "══════════════════════════════════════════"
  echo "  Arbitrage API 管道运行报告"
  echo "══════════════════════════════════════════"
  echo ""
  echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S UTC')"
  echo ""
  echo "📊 抓取: 新增 ${SCRAPER_NEW} 条, 更新 ${SCRAPER_UPD} 条"
  echo "🤖 ${ENRICH_SUMMARY}"
  echo ""
  echo "📈 API 大盘:"
  curl -s http://localhost:8900/v1/stats 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f\"  总趋势: {d['total_trends']}  平均热度: {d.get('avg_heat','?')}\")
    print(f\"  热度分布: {d.get('heat_levels',{})}\")
    hs = d.get('sources',{})
    print(f\"  来源: {', '.join(f'{k}:{v}' for k,v in sorted(hs.items()))}\")
except: print('  (API不可达)')
"
  echo ""
  echo "---"
  echo "Hermes Cron | Arbitrage API Pipeline v2.2"
  echo "详情: http://161.153.56.113:8900/"
} | msmtp jkk542830@gmail.com 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 邮件已发送到 jkk542830@gmail.com"