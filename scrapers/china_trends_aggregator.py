import json
import re
import hashlib
from typing import List, Dict, Any, Optional
from urllib.parse import quote
from loguru import logger
from bs4 import BeautifulSoup
from sqlmodel import Session, select
from core.database import RawTrend, raw_engine
from scrapers.base_scraper import BaseScraper
from scrapers.zhihu import ZhihuHotScraper
from scrapers.douyin import DouyinHotScraper
from scrapers.bilibili import BilibiliHotScraper
from scrapers.toutiao import ToutiaoHotScraper
from scrapers.baidu_api import BaiduApiHotScraper
from scrapers.weibo_api import WeiboApiHotScraper


class ChinaTrendsScraper(BaseScraper):
    """多平台中文热点爬虫 — 提取真实热度数据+分类+链接"""

    def __init__(self, proxy: Optional[str] = None):
        super().__init__(proxy)

    def fetch_weibo_hot_searches(self) -> List[Dict[str, Any]]:
        """抓取微博实时热搜，提取热度、排名、分类、链接"""
        url = "https://s.weibo.com/top/summary"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": "SUB=_2AkMSVpWdf8NxqwFRmP8SyWvhaY1wywjEieKj_vWJSTMyHRl-yD9jqy88tRB6PhG7wBWejG_0Z368Fas-KscXG_i435uM;"
        }
        html = self.fetch_html(url, headers_override=headers)
        trends = []
        if not html:
            return trends

        try:
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table")
            if table:
                rows = table.find_all("tr")
                for row in rows:
                    td_rank = row.find("td", class_="td-01")
                    td_keyword = row.find("td", class_="td-02")
                    if td_rank and td_keyword:
                        rank_str = td_rank.get_text(strip=True)
                        if not rank_str.isdigit():
                            continue

                        rank = int(rank_str)

                        a_tag = td_keyword.find("a")
                        keyword = a_tag.get_text(strip=True) if a_tag else ""

                        heat_span = td_keyword.find("span")
                        heat_str = heat_span.get_text(strip=True) if heat_span else "0"
                        heat = int(heat_str.replace(",", "")) if heat_str.replace(",", "").isdigit() else 0

                        # 微博分类：不再有 img[alt] 标签，改用排名推断
                        # top3→hot, 4-10→trending, 其余→general
                        if rank <= 3:
                            category = "hot"
                        elif rank <= 10:
                            category = "trending"
                        else:
                            category = "general"

                        # 原文链接
                        href = a_tag.get("href", "") if a_tag else ""
                        if href and not href.startswith("http"):
                            href = f"https://s.weibo.com{href}"
                        source_url = href or f"https://s.weibo.com/weibo?q={quote(keyword)}"

                        trends.append({
                            "keyword": keyword,
                            "rank": rank,
                            "heat": heat,
                            "category": category,
                            "source_url": source_url,
                            "summary": f"微博实时热搜第{rank}位：{keyword}（热度{heat}）",
                            "platform_label": "微博热搜"
                        })
            logger.info(f"✅ 微博热搜 {len(trends)} 条")
        except Exception as e:
            logger.error(f"微博解析失败: {e}")
        return trends

    def fetch_baidu_hot_searches(self) -> List[Dict[str, Any]]:
        """抓取百度实时热搜，提取热度、排名、分类、链接"""
        url = "https://top.baidu.com/board?tab=realtime"
        html = self.fetch_html(url)
        trends = []
        if not html:
            return trends

        try:
            soup = BeautifulSoup(html, "html.parser")
            content_items = soup.find_all("div", class_=lambda c: c and "category-wrap" in c)

            known_tags = {'热': 'general', '新': 'news', '沸': 'trending',
                         '荐': 'recommended', '爆': 'viral'}
            for item in content_items:
                # 排名：从 index_1Ew5p 提取（第1条无数字则推断为1）
                rank_el = item.find("div", class_=lambda c: c and "index" in (c if isinstance(c, str) else ""))
                rank_text = rank_el.get_text(strip=True) if rank_el else ""
                rank = int(rank_text) if rank_text.isdigit() else 1

                # 热度：从 hot-index_1Bl1a 提取
                heat_el = item.find("div", class_=lambda c: c and "hot-index" in (c if isinstance(c, str) else ""))
                heat_str = heat_el.get_text(strip=True) if heat_el else "0"
                heat = int("".join(filter(str.isdigit, heat_str))) if heat_str else 0

                # 关键词 + 标签（热/新/沸等黏在标题末尾）
                title_el = item.find("a", class_=lambda c: c and "title" in (c if isinstance(c, str) else ""))
                title_text = title_el.get_text(strip=True) if title_el else ""
                if not title_text:
                    continue

                category = "general"
                for tag_txt, cat_val in known_tags.items():
                    if title_text.endswith(tag_txt):
                        title_text = title_text[:-len(tag_txt)]
                        category = cat_val
                        break

                # 摘要
                desc_el = item.find("div", class_=lambda c: c and "hot-desc" in (c if isinstance(c, str) else ""))
                summary = desc_el.get_text(strip=True) if desc_el else f"百度实时热搜第{rank}位：{title_text}"
                summary = summary.replace("查看更多>", "").strip()

                # 原文链接
                a_tag = title_el if title_el else item.find("a", href=True)
                source_url = ""
                if a_tag:
                    href = a_tag.get("href", "")
                    source_url = href if href.startswith("http") else f"https://top.baidu.com{href}"

                trends.append({
                    "keyword": title_text,
                    "rank": rank,
                    "heat": heat,
                    "category": category,
                    "source_url": source_url,
                    "summary": summary,
                    "platform_label": "百度热搜"
                })

            logger.info(f"✅ 百度热搜 {len(trends)} 条")
        except Exception as e:
            logger.error(f"百度解析失败: {e}")
        return trends

    @staticmethod
    def get_md5_hash(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def run_ingestion_cycle(self, limit_trends: int = 20):
        """全量抓取并存入原始库（微博+百度+知乎+抖音+bilibili+头条+微博API+百度API）"""
        logger.info("=== 开始热点抓取 ===")
        weibo_trends = self.fetch_weibo_hot_searches()
        baidu_trends = self.fetch_baidu_hot_searches()
        zhihu_trends = ZhihuHotScraper().fetch_hot_list()
        douyin_trends = DouyinHotScraper().fetch_hot_list()
        bilibili_trends = BilibiliHotScraper().fetch_hot_list()
        toutiao_trends = ToutiaoHotScraper().fetch_hot_list()
        baidu_api_trends = BaiduApiHotScraper().fetch_hot_list()
        weibo_api_trends = WeiboApiHotScraper().fetch_hot_list()

        all_raw = []
        for t in weibo_trends[:limit_trends]:
            all_raw.append(("weibo", t))
        for t in baidu_trends[:limit_trends]:
            all_raw.append(("baidu", t))
        for t in zhihu_trends[:limit_trends]:
            all_raw.append(("zhihu", t))
        for t in douyin_trends[:limit_trends]:
            all_raw.append(("douyin", t))
        # bilibili returns ~40 items (20 popular + 20 trending), capture all
        for t in bilibili_trends:
            all_raw.append(("bilibili", t))
        for t in toutiao_trends[:limit_trends]:
            all_raw.append(("toutiao", t))
        for t in baidu_api_trends[:limit_trends]:
            all_raw.append(("baidu_api", t))
        for t in weibo_api_trends[:limit_trends]:
            all_raw.append(("weibo_api", t))

        logger.info(f"共采集 {len(all_raw)} 条原始热点")

        new_count = 0
        with Session(raw_engine) as session:
            for source, trend_data in all_raw:
                keyword = trend_data["keyword"]
                if not keyword:
                    continue
                raw_id = self.get_md5_hash(f"{source}:{keyword}")

                stmt = select(RawTrend).where(RawTrend.raw_id == raw_id)
                existing = session.exec(stmt).first()

                if existing:
                    existing.payload = json.dumps(trend_data, ensure_ascii=False)
                    session.add(existing)
                    logger.debug(f"更新: {source}:{keyword}")
                else:
                    new_raw = RawTrend(
                        source=source,
                        raw_id=raw_id,
                        payload=json.dumps(trend_data, ensure_ascii=False)
                    )
                    session.add(new_raw)
                    new_count += 1
                    logger.success(f"新增: [{source}] {keyword} (热度:{trend_data['heat']})")

            session.commit()
        logger.info(f"抓取完成，新增{new_count}条，更新{len(all_raw)-new_count}条")


if __name__ == "__main__":
    scraper = ChinaTrendsScraper()
    scraper.run_ingestion_cycle(limit_trends=30)