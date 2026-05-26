"""百度实时热搜爬虫 — 通过top.baidu.com JSON API无鉴权抓取

API端点: https://top.baidu.com/api/board?tab=realtime
返回50条实时热搜，含标题、热度分、描述、URL等。
相比原有的baidu HTML解析器，这是一个更稳定快速的JSON API方式。
"""
import json
import hashlib
from typing import List, Dict, Any, Optional
from loguru import logger
from scrapers.base_scraper import BaseScraper


class BaiduApiHotScraper(BaseScraper):
    """通过JSON API抓取百度实时热搜数据"""

    API_URL = "https://top.baidu.com/api/board?tab=realtime"

    def __init__(self, proxy: Optional[str] = None):
        super().__init__(proxy)

    def fetch_hot_list(self) -> List[Dict[str, Any]]:
        """从百度实时热搜API获取数据"""
        trends = []
        html = self.fetch_html(
            self.API_URL,
            headers_override={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://top.baidu.com/board?tab=realtime",
            },
        )
        if not html:
            logger.error("百度实时热搜API无响应")
            return trends

        try:
            data = json.loads(html)
            if not data.get("success"):
                logger.error(f"百度API返回失败: {data.get('error')}")
                return trends

            cards = data.get("data", {}).get("cards", [])
            content = cards[0].get("content", []) if cards else []

            for item in content:
                word = item.get("word", "")
                query = item.get("query", "")
                desc = item.get("desc", "")
                hot_score_str = item.get("hotScore", "0")
                hot_change = item.get("hotChange", "same")
                hot_tag = item.get("hotTag", "0")
                raw_url = item.get("rawUrl", "")
                index = item.get("index", 0)

                title = word or query
                if not title:
                    continue

                try:
                    hot_score = int(hot_score_str)
                except (ValueError, TypeError):
                    hot_score = 0

                # 热度变化方向
                change_map = {
                    "up": "上升",
                    "down": "下降",
                    "same": "持平",
                    "new": "新上榜",
                }
                change_label = change_map.get(hot_change, "")

                # 热度标签: 0=普通, 1=热, 2=沸, 3=新
                tag_map = {"0": "normal", "1": "hot", "2": "boiling", "3": "new"}
                label_type = tag_map.get(hot_tag, "normal")

                # 热度级别
                if hot_score >= 5000000:
                    heat_level = "viral"
                elif hot_score >= 2000000:
                    heat_level = "top"
                elif hot_score >= 500000:
                    heat_level = "hot"
                elif hot_score >= 100000:
                    heat_level = "trending"
                else:
                    heat_level = "normal"

                trends.append({
                    "keyword": title,
                    "rank": index + 1,
                    "heat": hot_score,
                    "heat_level": heat_level,
                    "category": label_type,
                    "source_url": raw_url or f"https://www.baidu.com/s?wd={title}",
                    "summary": desc[:300] or f"百度实时热搜第{index + 1}位：{title}",
                    "platform_label": "百度实时热搜",
                    "extra": {
                        "hot_change": hot_change,
                        "change_label": change_label,
                        "hot_tag": hot_tag,
                        "desc": desc,
                    }
                })

            logger.info(f"✅ 百度实时热搜 {len(trends)} 条")
        except Exception as e:
            logger.error(f"百度实时热搜解析失败: {e}")

        return trends

    @staticmethod
    def get_md5_hash(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    scraper = BaiduApiHotScraper()
    results = scraper.fetch_hot_list()
    print(f"共抓取 {len(results)} 条")
    if results:
        print(json.dumps(results[0], ensure_ascii=False, indent=2))
