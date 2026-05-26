"""抖音热搜爬虫 — 通过抖音官方API无鉴权抓取"""
import json
import hashlib
from typing import List, Dict, Any, Optional
from loguru import logger
from scrapers.base_scraper import BaseScraper


class DouyinHotScraper(BaseScraper):
    """抓取抖音热搜数据"""

    API_URL = (
        "https://www.douyin.com/aweme/v1/web/hot/search/list/"
        "?detail_list=1&source=0&main_billboard_count=10"
    )

    def __init__(self, proxy: Optional[str] = None):
        super().__init__(proxy)

    def fetch_hot_list(self) -> List[Dict[str, Any]]:
        """从抖音API获取热搜榜单"""
        trends = []
        html = self.fetch_html(
            self.API_URL,
            headers_override={
                "User-Agent": (
                    "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.6099.144 Mobile Safari/537.36"
                ),
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://www.douyin.com/",
            },
        )
        if not html:
            logger.error("抖音热搜API无响应")
            return trends

        try:
            data = json.loads(html)
            word_list = data.get("data", {}).get("word_list", [])
            for item in word_list:
                keyword = item.get("word", "")
                if not keyword:
                    continue

                position = item.get("position", 0)
                hot_value = item.get("hot_value", 0)
                label = item.get("label", 0)  # 0=普通, 1=热, 2=沸, 3=新, 4=荐
                video_count = item.get("video_count", 0)
                discuss_video_count = item.get("discuss_video_count", 0)
                group_id = item.get("group_id", "")

                # 官方标签 → 我们的分类
                label_map = {
                    0: "general",
                    1: "trending",   # 热
                    2: "hot",        # 沸
                    3: "new",        # 新
                    4: "recommended",  # 荐
                }
                category = label_map.get(label, "general")

                # 热度级别
                if hot_value >= 10000000:
                    heat_level = "viral"
                elif hot_value >= 5000000:
                    heat_level = "top"
                elif hot_value >= 1000000:
                    heat_level = "hot"
                elif hot_value >= 100000:
                    heat_level = "trending"
                else:
                    heat_level = "normal"

                # 生成原文链接
                source_url = (
                    f"https://www.douyin.com/search/{keyword}"
                    if keyword else ""
                )

                summary = (
                    f"抖音热搜第{position}位：{keyword}"
                    f"（热度{hot_value}，{video_count}个视频讨论）"
                )

                trends.append({
                    "keyword": keyword,
                    "rank": position,
                    "heat": hot_value,
                    "heat_level": heat_level,
                    "category": category,
                    "source_url": source_url,
                    "summary": summary,
                    "platform_label": "抖音热搜",
                    "extra": {
                        "video_count": video_count,
                        "discuss_video_count": discuss_video_count,
                        "group_id": group_id,
                        "label": label,
                    }
                })

            # 按position排序
            trends.sort(key=lambda t: t["rank"])
            logger.info(f"✅ 抖音热搜 {len(trends)} 条")
        except Exception as e:
            logger.error(f"抖音热搜解析失败: {e}")

        return trends

    @staticmethod
    def get_md5_hash(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    scraper = DouyinHotScraper()
    results = scraper.fetch_hot_list()
    print(f"共抓取 {len(results)} 条")
    if results:
        print(json.dumps(results[0], ensure_ascii=False, indent=2))