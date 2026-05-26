"""今日头条热榜爬虫 — 通过头条官方API无鉴权抓取

API端点: https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc
返回50条热搜数据，含标题、热度值、URL、分类标签等。
"""
import json
import hashlib
from typing import List, Dict, Any, Optional
from loguru import logger
from scrapers.base_scraper import BaseScraper


class ToutiaoHotScraper(BaseScraper):
    """抓取今日头条热榜数据"""

    API_URL = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"

    def __init__(self, proxy: Optional[str] = None):
        super().__init__(proxy)

    def fetch_hot_list(self) -> List[Dict[str, Any]]:
        """从今日头条API获取热榜数据"""
        trends = []
        html = self.fetch_html(
            self.API_URL,
            headers_override={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://www.toutiao.com/",
            },
        )
        if not html:
            logger.error("今日头条热榜API无响应")
            return trends

        try:
            data = json.loads(html)
            if data.get("status") != "success":
                logger.error(f"今日头条API返回状态异常: {data.get('status')}")
                return trends

            items = data.get("data", [])
            # 处理置顶数据（如果有）
            fixed_top = data.get("fixed_top_data", [])
            top_data_list = []
            if fixed_top:
                for ft in fixed_top:
                    top_data_list.append({
                        "keyword": ft.get("Title", ""),
                        "rank": 0,  # 置顶
                        "heat": None,  # 置顶无热度值
                        "heat_level": "top",
                        "category": "fixed_top",
                        "source_url": ft.get("Url", ""),
                        "summary": f"【置顶】{ft.get('Title', '')}",
                        "platform_label": "头条热榜",
                        "extra": {}
                    })

            for i, item in enumerate(items):
                title = item.get("Title", "")
                if not title:
                    continue

                hot_value_str = item.get("HotValue", "0")
                try:
                    hot_value = int(hot_value_str)
                except (ValueError, TypeError):
                    hot_value = 0

                url = item.get("Url", "")
                cluster_id = item.get("ClusterIdStr", "")
                interest = item.get("InterestCategory", [])
                category = interest[0] if interest and isinstance(interest, list) else "general"

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

                trends.append({
                    "keyword": title,
                    "rank": i + 1,
                    "heat": hot_value,
                    "heat_level": heat_level,
                    "category": category,
                    "source_url": url,
                    "summary": f"头条热榜第{i+1}位：{title}（热度{hot_value}）",
                    "platform_label": "头条热榜",
                    "extra": {
                        "cluster_id": cluster_id,
                        "interest_category": interest,
                    }
                })

            # 置顶放在最前面
            all_trends = top_data_list + trends
            logger.info(f"✅ 今日头条热榜 {len(all_trends)} 条（含{len(top_data_list)}条置顶）")
            return all_trends

        except Exception as e:
            logger.error(f"今日头条热榜解析失败: {e}")

        return trends

    @staticmethod
    def get_md5_hash(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    scraper = ToutiaoHotScraper()
    results = scraper.fetch_hot_list()
    print(f"共抓取 {len(results)} 条")
    if results:
        print(json.dumps(results[0], ensure_ascii=False, indent=2))
