"""微博热搜爬虫 — 通过微博JSON API无鉴权抓取

API端点: https://weibo.com/ajax/side/hotSearch
相比原有的HTML解析方式，JSON API更稳定快速。
返回实时热搜 + 文娱热搜 + 热搜gov置顶。
"""
import json
import hashlib
from typing import List, Dict, Any, Optional
from loguru import logger
from scrapers.base_scraper import BaseScraper


class WeiboApiHotScraper(BaseScraper):
    """通过JSON API抓取微博热搜数据"""

    API_URL = "https://weibo.com/ajax/side/hotSearch"

    def __init__(self, proxy: Optional[str] = None):
        super().__init__(proxy)

    def fetch_hot_list(self) -> List[Dict[str, Any]]:
        """从微博API获取热搜榜单"""
        trends = []
        html = self.fetch_html(
            self.API_URL,
            headers_override={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://weibo.com/",
            },
        )
        if not html:
            logger.error("微博热搜API无响应")
            return trends

        try:
            data = json.loads(html)
            if data.get("ok") != 1:
                logger.error(f"微博API返回状态异常: {data.get('ok')}")
                return trends

            realtime_data = data.get("data", {}).get("realtime", [])
            hotgov = data.get("data", {}).get("hotgov", {})

            # 处理置顶gov热搜
            if hotgov and hotgov.get("word"):
                trends.append({
                    "keyword": hotgov.get("word", "").replace("#", ""),
                    "rank": 0,
                    "heat": None,
                    "heat_level": "top",
                    "category": "government",
                    "source_url": hotgov.get("url", ""),
                    "summary": hotgov.get("note", "")[:300] or f"【政务推荐】{hotgov.get('word', '')}",
                    "platform_label": "微博热搜",
                    "extra": {
                        "is_gov": True,
                        "icon_desc": hotgov.get("icon_desc", ""),
                        "mid": hotgov.get("mid", ""),
                    }
                })

            # 处理实时热搜
            for item in realtime_data:
                note = item.get("note", "")
                word = item.get("word", "")
                title = note or word
                if not title:
                    continue

                title = title.replace("#", "")  # 去掉话题号

                num = item.get("num", 0)
                rank = item.get("rank", 0)
                realpos = item.get("realpos", 0)
                label_name = item.get("label_name", "")
                flag_desc = item.get("flag_desc", "")
                word_scheme = item.get("word_scheme", "")
                is_topic = item.get("topic_flag", 0) == 1

                # 使用realpos作为排名（如果没有则用rank）
                position = realpos if realpos else (rank + 1 if rank is not None else 0)

                heat = num if num else 0

                # 热度级别
                if heat >= 5000000:
                    heat_level = "viral"
                elif heat >= 2000000:
                    heat_level = "top"
                elif heat >= 500000:
                    heat_level = "hot"
                elif heat >= 100000:
                    heat_level = "trending"
                else:
                    heat_level = "normal"

                # 标签映射
                label_map = {
                    "热": "hot",
                    "沸": "boiling",
                    "新": "new",
                    "荐": "recommended",
                }
                category = label_map.get(label_name, "general")

                source_url = f"https://s.weibo.com/weibo?q={word}" if word else ""

                trends.append({
                    "keyword": title,
                    "rank": position,
                    "heat": heat,
                    "heat_level": heat_level,
                    "category": category,
                    "source_url": source_url,
                    "summary": f"微博热搜第{position}位：{title}（热度{heat}）",
                    "platform_label": "微博热搜",
                    "extra": {
                        "label_name": label_name,
                        "flag_desc": flag_desc,
                        "is_topic": is_topic,
                        "word_scheme": word_scheme,
                    }
                })

            # 按rank排序
            trends.sort(key=lambda t: (0 if t["rank"] == 0 else 1, t["rank"]))
            logger.info(f"✅ 微博热搜 {len(trends)} 条")
        except Exception as e:
            logger.error(f"微博热搜解析失败: {e}")

        return trends

    @staticmethod
    def get_md5_hash(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    scraper = WeiboApiHotScraper()
    results = scraper.fetch_hot_list()
    print(f"共抓取 {len(results)} 条")
    if results:
        print(json.dumps(results[1], ensure_ascii=False, indent=2))  # skip gov top
