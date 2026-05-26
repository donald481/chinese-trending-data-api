#!/usr/bin/env python3
"""
Re-run recategorization for remaining 'general'/'normal' records.
Adds more keyword patterns to catch weather, crime, disaster, mining, etc.
"""

import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "clean_data.db"))

# Additional keywords for the remaining hard cases
EXTRA_KEYWORDS = {
    "social": [
        # Weather & natural disasters
        "暴雨", "降雨", "汛情", "龙卷风", "台风", "高温", "冰雹",
        "洪水", "积水", "洪灾", "干旱", "寒潮", "暴雪", "强降雨",
        "大暴雨", "大到暴雨", "防汛", "应急响应",
        # Crime & justice
        "死刑", "判刑", "刑拘", "刑侦", "犯罪", "凶手", "杀人",
        "致死", "死亡", "身亡", "遇难", "失联", "被困",
        "被抓", "被查", "立案", "侦查", "起诉", "庭审",
        "殴打", "伤害", "暴力", "虐待", "家暴", "出轨",
        "诈骗", "骗财", "骗色", "抢劫", "盗窃",
        # Mining accidents
        "矿难", "煤矿", "瓦斯", "爆炸", "矿井", "下井",
        # Rumor control
        "谣言", "辟谣", "净网", "网传", "假的", "不实信息",
        # Government & enforcement
        "市长", "省长", "书记", "局长", "全总", "总工会",
        "纪委", "被查", "正部级", "落马",
        # Other social
        "被狗", "被蛇", "蟒蛇", "动物", "宠物", "猫", "狗",
        "老人", "奶奶", "爷爷", "儿童", "孩子", "村民",
        "民警", "警方", "公安", "消防", "救援", "求助",
        "媒体", "新闻", "通报", "发布", "声明",
        "逝世", "去世", "袁隆平", "纪念",
        # Culture
        "文化", "强国", "精神", "传统",
        # Agriculture
        "小麦", "种粮", "收割", "农业", "农民",
        "猪", "牛", "羊", "养殖",
    ],
    "entertainment": [
        "演技", "影视", "剧集", "角色", "剧情",
        "杨紫", "潘玮柏", "面瘫", "郑钦文",
        "乘风", "姐姐", "公演",
        "综艺", "真人秀", "表演",
    ],
    "education": [
        "历史", "哲学", "逻辑", "智慧",
        "面试", "职场", "工作", "辞职",
        "大学", "专业", "知识",
    ],
    "sports": [
        "郑钦文", "法网", "网球",
        "文班亚马", "马刺", "雷霆", "NBA",
        "世少赛", "分组",
        "吴艳妮", "栏",
    ],
}

# Also add single-char/isolation entries that need careful placement
SINGLE_CHAR_PATTERNS = {
    "social": "被",
    "sports": "胜",
}

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Check remaining
    total = conn.execute("SELECT COUNT(*) FROM clean_trend WHERE category IN ('general','normal')").fetchone()[0]
    print(f"Records remaining in general/normal: {total}")

    rows = conn.execute("""
        SELECT id, keyword, title, content_clean, source, category
        FROM clean_trend
        WHERE category IN ('general', 'normal')
    """).fetchall()

    # Flatten extra keywords
    flat_extra = []
    for cat, kws in EXTRA_KEYWORDS.items():
        for kw in kws:
            flat_extra.append((kw.lower(), cat))
    flat_extra.sort(key=lambda x: -len(x[0]))

    updates = {}
    no_match = 0
    import collections
    matched = collections.Counter()

    for row in rows:
        text = " ".join(filter(None, [row["keyword"], row["title"], row["content_clean"]]))
        text_lower = text.lower()

        found = None
        for kw, cat in flat_extra:
            if kw in text_lower:
                found = cat
                break

        if found:
            updates[row["id"]] = found
            matched[found] += 1
        else:
            no_match += 1

    print(f"\nMatch results:")
    print(f"  Matched: {len(updates)}")
    print(f"  Still no match: {no_match}")
    for cat, cnt in matched.most_common():
        print(f"    {cat}: {cnt}")

    if updates:
        print(f"\nApplying {len(updates)} updates...")
        cursor = conn.cursor()
        for i, (row_id, new_cat) in enumerate(updates.items()):
            cursor.execute("UPDATE clean_trend SET category = ? WHERE id = ?", (new_cat, row_id))
            if (i+1) % 100 == 0:
                conn.commit()
        conn.commit()
        print(f"Done!")

    # Final stats
    after = conn.execute("SELECT COUNT(*) FROM clean_trend WHERE category IN ('general','normal')").fetchone()[0]
    print(f"\nRemaining general/normal: {after} ({round(after/total*100, 1)}% of original)")
    print(f"Reduction: {total - after} records")

    conn.close()

if __name__ == "__main__":
    main()
