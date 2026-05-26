"""B站热榜爬虫 — 通过B站官方API无鉴权抓取
两个数据源:
1. 热门视频: https://api.bilibili.com/x/web-interface/popular
2. 热搜关键词: https://api.bilibili.com/x/web-interface/search/square
"""
import json
import hashlib
from typing import List, Dict, Any, Optional
from loguru import logger
from scrapers.base_scraper import BaseScraper


class BilibiliHotScraper(BaseScraper):
    """抓取B站热门视频与热搜关键词"""

    POPULAR_URL = "https://api.bilibili.com/x/web-interface/popular"
    TRENDING_URL = "https://api.bilibili.com/x/web-interface/search/square?limit=20"

    def __init__(self, proxy: Optional[str] = None):
        super().__init__(proxy)

    def fetch_popular_videos(self) -> List[Dict[str, Any]]:
        """从B站API获取热门视频榜单"""
        trends = []
        html = self.fetch_html(
            self.POPULAR_URL,
            headers_override={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://www.bilibili.com/",
            },
        )
        if not html:
            logger.error("B站热门视频API无响应")
            return trends

        try:
            data = json.loads(html)
            if data.get("code") != 0:
                logger.error(f"B站API返回错误: {data.get('message')}")
                return trends

            items = data.get("data", {}).get("list", [])
            for i, item in enumerate(items):
                title = item.get("title", "")
                if not title:
                    continue

                stat = item.get("stat", {})
                owner = item.get("owner", {})
                rcmd_reason = item.get("rcmd_reason", {})

                # 热度计算：综合播放、点赞、弹幕、收藏等
                view = stat.get("view", 0)
                like = stat.get("like", 0)
                danmaku = stat.get("danmaku", 0)
                favorite = stat.get("favorite", 0)
                coin = stat.get("coin", 0)
                share = stat.get("share", 0)
                heat = view + like * 5 + danmaku * 10 + favorite * 20 + coin * 30 + share * 50

                bvid = item.get("bvid", "")
                short_link = item.get("short_link_v2", "")
                source_url = short_link or f"https://www.bilibili.com/video/{bvid}"

                category = item.get("tname", "综合")

                # 热度级别
                if heat >= 5000000:
                    heat_level = "viral"
                elif heat >= 1000000:
                    heat_level = "top"
                elif heat >= 500000:
                    heat_level = "hot"
                elif heat >= 100000:
                    heat_level = "trending"
                else:
                    heat_level = "normal"

                trends.append({
                    "keyword": title,
                    "rank": i + 1,
                    "heat": heat,
                    "heat_level": heat_level,
                    "category": category,
                    "source_url": source_url,
                    "summary": item.get("desc", "")[:300] or f"B站热门视频第{i+1}位：{title}",
                    "platform_label": "B站热门视频",
                    "extra": {
                        "aid": item.get("aid"),
                        "bvid": bvid,
                        "author": owner.get("name", ""),
                        "author_mid": owner.get("mid"),
                        "view": view,
                        "like": like,
                        "danmaku": danmaku,
                        "favorite": favorite,
                        "coin": coin,
                        "share": share,
                        "duration": item.get("duration"),
                        "pic": item.get("pic", ""),
                        "pubdate": item.get("pubdate"),
                        "rcmd_reason": rcmd_reason.get("content", ""),
                    }
                })

            logger.info(f"✅ B站热门视频 {len(trends)} 条")
        except Exception as e:
            logger.error(f"B站热门视频解析失败: {e}")

        return trends

    def fetch_trending_search(self) -> List[Dict[str, Any]]:
        """从B站API获取热搜关键词榜单"""
        trends = []
        html = self.fetch_html(
            self.TRENDING_URL,
            headers_override={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://www.bilibili.com/",
            },
        )
        if not html:
            logger.error("B站热搜API无响应")
            return trends

        try:
            data = json.loads(html)
            if data.get("code") != 0:
                logger.error(f"B站热搜API返回错误: {data.get('message')}")
                return trends

            items = data.get("data", {}).get("trending", {}).get("list", [])
            for i, item in enumerate(items):
                keyword = item.get("keyword", "")
                show_name = item.get("show_name", "")
                heat_score = item.get("heat_score", 0)
                icon = item.get("icon", "")

                if not keyword:
                    continue

                source_url = f"https://search.bilibili.com/all?keyword={keyword}"

                # 热度级别
                if heat_score >= 5000000:
                    heat_level = "viral"
                elif heat_score >= 1000000:
                    heat_level = "top"
                elif heat_score >= 500000:
                    heat_level = "hot"
                else:
                    heat_level = "trending"

                # 带图标的热搜通常有特殊标记（如"热"、"新"、"沸"）
                label_type = "hot" if icon else "normal"

                trends.append({
                    "keyword": keyword,
                    "rank": i + 1,
                    "heat": heat_score,
                    "heat_level": heat_level,
                    "category": "trending_search",
                    "source_url": source_url,
                    "summary": f"B站热搜第{i+1}位：{show_name or keyword}（热度{heat_score}）",
                    "platform_label": "B站热搜",
                    "extra": {
                        "show_name": show_name,
                        "icon": icon,
                        "label_type": label_type,
                    }
                })

            logger.info(f"✅ B站热搜 {len(trends)} 条")
        except Exception as e:
            logger.error(f"B站热搜解析失败: {e}")

        return trends

    def fetch_hot_list(self) -> List[Dict[str, Any]]:
        """合并热门视频+热搜关键词"""
        all_trends = []
        all_trends.extend(self.fetch_popular_videos())
        all_trends.extend(self.fetch_trending_search())
        return all_trends

    @staticmethod
    def get_md5_hash(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    scraper = BilibiliHotScraper()
    results = scraper.fetch_hot_list()
    print(f"共抓取 {len(results)} 条")
    if results:
        print(json.dumps(results[0], ensure_ascii=False, indent=2))
