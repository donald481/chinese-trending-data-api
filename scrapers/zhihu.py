"""知乎热榜爬虫 — 通过 api.zhihu.com 无鉴权抓取"""
import json
import hashlib
from typing import List, Dict, Any, Optional
from loguru import logger
from scrapers.base_scraper import BaseScraper


class ZhihuHotScraper(BaseScraper):
    """抓取知乎热榜数据（https://www.zhihu.com/hot）"""

    API_URL = "https://api.zhihu.com/topstory/hot-list"

    def __init__(self, proxy: Optional[str] = None):
        super().__init__(proxy)

    def fetch_hot_list(self) -> List[Dict[str, Any]]:
        """从知乎API获取热榜数据"""
        trends = []
        html = self.fetch_html(
            self.API_URL,
            headers_override={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "application/json",
                "x-api-version": "3.0.40",
            }
        )
        if not html:
            logger.error("知乎热榜API无响应")
            return trends

        try:
            data = json.loads(html)
            items = data.get("data", [])
            for i, item in enumerate(items):
                target = item.get("target", {})
                title = target.get("title", "")
                if not title:
                    continue

                excerpt = target.get("excerpt", "")
                answer_count = target.get("answer_count", 0)
                follower_count = target.get("follower_count", 0)
                url = target.get("url", "")
                card_label = item.get("card_label", {})
                label_type = card_label.get("type", "")

                # 热度值：综合关注数和回答数作为热度指标
                heat = follower_count * 10 + answer_count * 10

                # 标签映射
                category_map = {
                    "hot": "trending",
                    "boiling": "hot",
                    "new": "news",
                    "recommend": "general",
                }
                category = category_map.get(label_type, "general")

                # 热度级别
                if heat >= 1000000:
                    heat_level = "viral"
                elif heat >= 500000:
                    heat_level = "top"
                elif heat >= 100000:
                    heat_level = "hot"
                elif heat >= 10000:
                    heat_level = "trending"
                else:
                    heat_level = "normal"

                trends.append({
                    "keyword": title,
                    "rank": i + 1,
                    "heat": heat,
                    "heat_level": heat_level,
                    "category": category,
                    "source_url": url,
                    "summary": excerpt[:300] if excerpt else f"知乎热榜第{i+1}位：{title}",
                    "platform_label": "知乎热榜",
                    "extra": {
                        "answer_count": answer_count,
                        "follower_count": follower_count,
                        "label_type": label_type,
                    }
                })

            logger.info(f"✅ 知乎热榜 {len(trends)} 条")
        except Exception as e:
            logger.error(f"知乎热榜解析失败: {e}")

        return trends

    @staticmethod
    def get_md5_hash(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    scraper = ZhihuHotScraper()
    results = scraper.fetch_hot_list()
    print(f"共抓取 {len(results)} 条")
    if results:
        print(json.dumps(results[0], ensure_ascii=False, indent=2))