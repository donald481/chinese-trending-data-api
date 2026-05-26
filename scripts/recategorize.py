#!/usr/bin/env python3
"""
Recategorization Script for Chinese Trending Data API
=====================================================
Re-classifies 'general' and 'normal' category records using comprehensive
Chinese keyword matching → proper content-based categories.

Safe: backs up DB first, updates in-place, prints before/after stats.

Target categories (matching API spec):
  科技(technology), 财经(finance), 娱乐(entertainment), 体育(sports),
  游戏(gaming), 健康(health), 教育(education), 旅游(travel),
  美食(food), 时尚(fashion), 汽车(auto), 房产(real_estate),
  国际(international), 社会(social), 军事(military), 动漫(anime)
"""

import sqlite3
import os
import shutil
from collections import Counter

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "clean_data.db")
DB_PATH = os.path.abspath(DB_PATH)


# ══════════════════════════════════════════════════════════════════════
# Comprehensive Chinese Keyword Maps
# ══════════════════════════════════════════════════════════════════════

CATEGORY_KEYWORDS = {
    # ─── 科技 / Technology ───
    "technology": [
        "AI", "人工智能", "大模型", "机器学习", "深度学", "神经网络",
        "ChatGPT", "GPT", "OpenAI", "深度求索", "DeepSeek", "文心一言",
        "通义千问", "讯飞星火", "豆包", "Kimi", "Claude", "Gemini",
        "机器人", "自动驾", "无人驾驶", "智能驾驶", "自动驾驶",
        "芯片", "半导体", "处理器", "CPU", "GPU", "华为", "麒麟",
        "高通", "英伟达", "NVIDIA", "AMD", "英特尔", "Intel",
        "手机", "智能手机", "iPhone", "安卓", "iOS", "鸿蒙", "HarmonyOS",
        "小米", "OPPO", "vivo", "荣耀", "三星", "苹果",
        "5G", "6G", "WiFi", "蓝牙", "物联网", "IoT",
        "VR", "AR", "MR", "元宇宙", "区块链", "NFT",
        "软件", "编程", "代码", "开发者", "开源", "Linux", "Windows",
        "数据", "大数据", "云计算", "云服务", "服务器", "数据库",
        "算法", "推荐算法", "数字人", "虚拟人", "AIGC",
        "数码", "电子", "科技", "科学技术", "科研", "实验室",
        "航天", "火箭", "卫星", "太空", "宇宙", "飞船",
        "SpaceX", "星舰", "NASA", "嫦娥", "天宫", "空间站",
        "专利", "创新", "黑科技", "数码产品", "可穿戴",
        "电脑", "笔记本", "平板", "耳机", "智能家居",
        "屏幕", "显示器", "分辨率", "折叠屏", "全面屏",
        "影像", "相机", "摄像头", "拍照", "摄影",
        "充电", "快充", "电池", "续航", "无线充",
        "操作系统", "系统更新", "应用", "app", "APP",
    ],

    # ─── 财经 / Finance ───
    "finance": [
        "A股", "股市", "股票", "基金", "理财", "投资", "散户",
        "涨停", "跌停", "牛市", "熊市", "大盘", "指数",
        "上证", "深证", "创业板", "科创板", "北交所",
        "美股", "港股", "纳斯达克", "道琼斯", "标普",
        "期货", "外汇", "黄金", "比特币", "加密货", "数字货币",
        "央行", "降息", "加息", "降准", "利率", "汇率",
        "GDP", "CPI", "通胀", "通缩", "经济", "经济数据",
        "财政", "货币政策", "财政政策", "赤字", "国债",
        "买房", "房价", "楼市", "房地产", "房贷", "首付",
        "企业", "公司", "上市", "IPO", "融资", "营收",
        "利润", "财报", "业绩", "亏损", "盈利", "市值",
        "亿万", "千万", "百万", "财富", "富豪", "福布斯",
        "消费", "零售", "电商", "双十一", "618", "促销",
        "贸易", "关税", "出口", "进口", "贸易战", "制裁",
        "就业", "失业", "工资", "薪酬", "涨薪", "裁员",
        "税务", "税收", "个人所得", "增值税", "退税",
        "保费", "保险", "养老", "社保", "公积金",
        "金融", "银行", "贷款", "信贷", "理财", "存款",
        "创业", "投资", "融资", "天使轮", "A轮", "B轮",
        "区块链", "Web3", "DeFi", "NFT", "数字货",
        "跨境", "出海", "外贸", "供应链", "产业链",
        "产能", "产量", "供应", "需求", "涨价", "降价",
        "小米汽车", "特斯拉", "新能源车", "电动车", "EV",
        "补贴", "消费券", "经济复苏",
    ],

    # ─── 娱乐 / Entertainment ───
    "entertainment": [
        "明星", "演员", "歌手", "导演", "艺人", "偶像",
        "电影", "电视剧", "综艺", "选秀", "真人秀", "节目",
        "票房", "上映", "首映", "预告", "片场", "角色",
        "音乐", "专辑", "演唱会", "歌曲", "歌", "乐队",
        "舞蹈", "舞台", "表演", "演出", "观众",
        "热搜", "热搜榜", "话题", "粉丝", "应援",
        "微博", "热搜", "文娱", "娱乐", "娱乐圈",
        "绯闻", "恋情", "离婚", "结婚", "分手", "复合",
        "出轨", "劈腿", "塌房", "翻车", "人设",
        "代言", "商务", "广告", "杂志", "封面",
        "戛纳", "奥斯卡", "金鸡奖", "金马奖", "金像奖", "奖项",
        "直播", "带货", "网红", "主播", "短视频",
        "抖音", "快手", "B站", "bilibili", "小红书",
        "爱奇艺", "腾讯视频", "优酷", "芒果TV", "Netflix",
        "好莱坞", "华语", "票房", "电影", "导演", "制片",
        "综艺节目", "真人秀", "脱口秀", "相声", "小品",
        "春晚", "跨年", "晚会", "盛典", "颁奖",
        "微博之夜", "白玉兰", "飞天奖", "华表奖",
        "拍戏", "剧组", "片酬", "签约", "经纪",
        "演唱会", "音乐节", "live", "现场",
        "新歌", "新专辑", "单曲", "EP", "MV",
        "杨幂", "赵丽颖", "迪丽热巴", "肖战", "王一博",
        "易烊千玺", "王俊凯", "王源", "蔡徐坤", "刘亦菲",
        "周杰伦", "林俊杰", "陈奕迅", "邓紫棋", "张艺兴",
        "杨颖", "Angelababy", "范冰冰", "李冰冰", "章子怡",
        "刘德华", "周星驰", "成龙", "梁朝伟", "张国荣",
        "SNH48", "THE9", "硬糖少女", "火箭少女",
    ],

    # ─── 体育 / Sports ───
    "sports": [
        "NBA", "CBA", "足球", "篮球", "排球", "网球", "乒乓球",
        "羽毛球", "高尔夫", "橄榄球", "棒球", "冰球",
        "奥运会", "冬奥", "亚运", "大运", "全运",
        "世界杯", "欧洲杯", "英超", "西甲", "德甲", "意甲", "法甲",
        "欧冠", "亚冠", "中超", "中甲",
        "冠军", "亚军", "季军", "金牌", "银牌", "铜牌",
        "运动员", "教练", "裁判", "比赛", "赛事", "联赛",
        "进球", "得分", "助攻", "篮板", "抢断", "盖帽",
        "MVP", "全明星", "总决赛", "季后赛",
        "F1", "赛车", "拉力赛", "摩托车", "越野",
        "电竞", "电子竞技", "LPL", "KPL", "英雄联盟", "LOL",
        "王者荣耀", "DOTA", "CSGO", "绝地求生", "吃鸡",
        "中国女排", "中国男篮", "中国女篮", "国足", "男足",
        "姚明", "刘翔", "李娜", "苏炳添", "谷爱凌",
        "詹姆斯", "库里", "杜兰特", "乔丹", "科比",
        "梅西", "C罗", "姆巴佩", "内马尔", "哈兰德",
        "武磊", "张继科", "马龙", "孙颖莎", "樊振东",
        "游泳", "田径", "体操", "举重", "跳水",
        "拳击", "UFC", "综合格斗", "武术", "太极",
        "马拉松", "跑步", "健身", "瑜伽",
        "体育总局", "足协", "篮协", "体育赛事",
        "跳台", "滑雪", "滑冰", "花样滑冰", "短道速滑",
        "女篮", "女足", "男篮", "比赛",
    ],

    # ─── 游戏 / Gaming ───
    "gaming": [
        "游戏", "手游", "网游", "端游", "单机游戏", "独立游戏",
        "王者荣耀", "和平精英", "原神", "崩坏", "星穹铁道",
        "英雄联盟", "LOL", "DOTA", "CSGO", "CS2", "瓦罗兰特",
        "Valorant", "守望先锋", "OW", "绝地求生", "PUBG",
        "永劫无间", "逆水寒", "剑网3", "梦幻西游", "大话西游",
        "我的世界", "Minecraft", "塞尔达", "任天堂", "Switch",
        "PlayStation", "PS5", "PS4", "Xbox", "Steam", "Epic",
        "游戏机", "主机", "掌机", "PC", "电脑游戏",
        "宝可梦", "Pokemon", "动物森友会", "动森",
        "米哈游", "腾讯游戏", "网易游戏", "完美世界",
        "游戏攻略", "游戏更新", "游戏版本", "新英雄", "新皮肤",
        "乙女游戏", "女性向", "二次元", "抽卡", "氪金",
        "游戏公司", "游戏产业", "游戏展会", "ChinaJoy",
        "黑神话", "黑神话悟空", "悟空",
        "拳皇", "街霸", "格斗游戏", "模拟器",
        "开黑", "组队", "排位", "段位", "上分",
        "游戏主播", "游戏直播", "电竞选手", "职业选手",
        "DLC", "资料片", "扩展包", "更新补丁",
        "评测", "测评", "试玩", "体验版", "demo",
        "主机游戏", "独立游戏", "3A大作", "大作",
        "游戏奖项", "TGA", "金摇杆", "游戏年度",
        "第五人格", "阴阳师", "明日方舟", "碧蓝航线",
        "手机游戏", "网络游戏", "电子竞技", "桌游棋牌",
    ],

    # ─── 健康 / Health ───
    "health": [
        "健康", "医疗", "医院", "医生", "护士", "患者",
        "疾病", "病毒", "细菌", "疫情", "新冠", "疫苗",
        "癌症", "肿瘤", "心梗", "脑梗", "中风", "糖尿病",
        "高血压", "高血脂", "肥胖", "减肥", "减重",
        "运动", "健身", "锻炼", "瑜伽", "跑步", "游泳",
        "营养", "饮食", "食谱", "养生", "保健", "中医",
        "药物", "药品", "中药", "西药", "处方", "医保",
        "手术", "治疗", "康复", "体检", "检查",
        "心理", "心理", "抑郁", "焦虑", "压力", "睡眠",
        "失眠", "熬夜", "疲劳", "医药", "临床", "研究",
        "卫健委", "疾控", "疾控中心", "公共卫生",
        "针灸", "按摩", "理疗", "康复", "护理",
        "头发", "脱发", "皮肤", "护肤", "美容",
        "眼睛", "视力", "近视", "眼科", "牙科",
        "食品安全", "食品", "添加剂", "防腐剂",
        "生育", "怀孕", "孕妇", "产后", "育儿",
        "老龄化", "养老", "长寿", "基因",
        "运动健康", "健身", "肌肉", "力量训练",
        "过敏", "哮喘", "流感", "感冒",
        "养生", "食疗", "药膳", "保健品",
        "医生", "医院", "医疗", "手术", "治疗",
    ],

    # ─── 教育 / Education ───
    "education": [
        "教育", "学校", "大学", "学院", "中学", "小学",
        "高考", "中考", "考研", "考公", "考编", "考证",
        "考试", "成绩", "分数", "录取", "招生", "入学",
        "学生", "老师", "教师", "教授", "校长", "导师",
        "课程", "课堂", "教学", "学", "作业",
        "留学", "出国", "海外", "国际学校", "交换",
        "培训", "补习", "辅导", "家教", "网课",
        "毕业", "学位", "博士", "硕士", "本科", "专科",
        "论文", "科研", "学术", "研究", "实验",
        "图书馆", "教材", "课本", "教辅", "试卷",
        "学前教育", "幼儿园", "早教", "启蒙",
        "职业教育", "技校", "培训", "技能",
        "素质教育", "双减", "减负", "教育改革",
        "公务员", "国考", "省考", "事业单位",
        "985", "211", "双一流", "C9", "北大", "清华",
        "考研上岸", "考研国家线", "分数线",
        "寒假", "暑假", "放假", "开学",
        "自习", "图书馆", "学霸", "学渣",
        "专升本", "考研", "保研", "推免",
        "毕业季", "论文答辩", "学位证", "毕业证",
        "少儿", "青少年", "儿童", "亲子", "育儿",
        "考试大纲", "备考", "复习", "冲刺",
        "教育局", "教育部", "教育政策",
    ],

    # ─── 旅游 / Travel ───
    "travel": [
        "旅游", "旅行", "出游", "出行", "度假", "休闲",
        "景点", "景区", "风景", "名胜", "古镇", "公园",
        "酒店", "民宿", "客栈", "度假村", "入住",
        "机票", "高铁", "火车", "自驾", "租车", "打车",
        "航班", "航空", "机场", "登机", "值机", "转机",
        "签证", "护照", "入境", "出境", "海关",
        "导游", "旅行社", "跟团", "自由行", "攻略",
        "五一", "国庆", "春节", "长假", "黄金周", "小长假",
        "国内游", "国外游", "出境游", "周边游",
        "海岛", "沙滩", "海边", "海边", "海滩",
        "山", "爬山", "徒步", "露营", "户外",
        "美食", "小吃", "餐厅", "当地", "特产",
        "拍照", "打卡", "网红景点", "网红店",
        "穷游", "背包客", "自驾游", "房车",
        "博物馆", "美术馆", "展览", "展馆",
        "滑雪", "温泉", "游乐场", "主题公园",
        "迪士尼", "环球影城", "方特", "欢乐谷",
        "摄影", "拍照", "旅拍", "风光",
        "出国", "海外", "境外", "跨国",
        "城市漫步", "Citywalk", "citywalk",
        "景区", "名胜", "古迹", "文化遗址",
        "乘坐", "航班", "列车", "出行",
    ],

    # ─── 美食 / Food ───
    "food": [
        "美食", "好吃", "美味", "烹饪", "做饭", "下厨",
        "餐厅", "饭店", "餐馆", "小吃", "摊位", "夜市",
        "菜谱", "食谱", "教程", "做法", "烘焙",
        "食材", "配料", "调料", "香料", "厨房",
        "火锅", "烧烤", "烤肉", "炸鸡", "汉堡", "披萨",
        "奶茶", "咖啡", "饮料", "饮品", "茶饮",
        "水果", "蔬菜", "肉类", "海鲜", "鱼",
        "面包", "蛋糕", "甜点", "蛋糕", "冰淇淋",
        "中国菜", "川菜", "粤菜", "湘菜", "鲁菜", "淮扬菜",
        "日料", "寿司", "刺身", "韩餐", "西餐",
        "面条", "米饭", "水饺", "饺子", "馄饨", "包子",
        "外卖", "点餐", "送餐", "配餐",
        "吃货", "探店", "打卡", "美食博主", "美食家",
        "超市", "菜市场", "菜场", "买菜",
        "烹饪比赛", "厨师", "厨艺", "料理",
        "品尝", "试吃", "品鉴", "美食节",
        "减肥餐", "健康饮食", "轻食", "沙拉",
        "美食制作", "美食侦探", "美食记录",
        "食堂", "餐厅", "厨房",
        "吃", "喝", "味", "香", "鲜",
    ],

    # ─── 时尚 / Fashion ───
    "fashion": [
        "时尚", "穿搭", "搭配", "着装", "衣服", "穿搭",
        "服装", "服饰", "衣橱", "衣柜", "穿衣",
        "品牌", "奢侈品", "大牌", "高定", "设计师",
        "LV", "Gucci", "香奈儿", "爱马仕", "迪奥", "Dior",
        "巴黎世家", "Balenciaga", "Prada", "Fendi",
        "鞋子", "鞋", "运动鞋", "球鞋", "高跟鞋",
        "包包", "包袋", "手袋", "配饰", "首饰",
        "化妆", "化妆品", "美妆", "护肤", "护肤品",
        "口红", "粉底", "眼影", "腮红", "面膜",
        "发型", "染发", "美发", "剪发", "造型",
        "模特", "走秀", "时装周", "米兰", "巴黎",
        "潮流", "潮牌", "联名", "限定",
        "二手", "闲置", "转卖", "中古", "vintage",
        "改造", "DIY", "手工", "手作",
        "简约", "复古", "日系", "韩系", "欧美",
        "显瘦", "显高", "遮肉", "配色",
        "香水", "香氛", "味道", "香味",
        "美容", "整形", "医美", "微整",
        "青春", "少女", "女装", "男装", "童装",
    ],

    # ─── 汽车 / Auto ───
    "auto": [
        "汽车", "车", "车型", "新车", "买车", "卖车",
        "新能源", "电动车", "电动汽车", "混动", "插混",
        "特斯拉", "比亚迪", "蔚来", "小鹏", "理想",
        "小米汽车", "华为汽车", "问界", "智界", "享界",
        "极氪", "岚图", "阿维塔", "深蓝", "零跑",
        "BBA", "奔驰", "宝马", "奥迪", "保时捷",
        "丰田", "本田", "大众", "日产", "福特",
        "发动机", "变速箱", "底盘", "悬挂",
        "试驾", "评测", "测评", "驾驶", "驾乘",
        "油耗", "续航", "充电", "加油", "省油",
        "自动驾驶", "智能驾驶", "辅助驾驶",
        "交通", "路况", "违章", "事故", "保险",
        "保养", "维修", "配件", "改装",
        "考驾照", "驾照", "驾考", "驾校",
        "停车场", "停车", "车位",
        "SUV", "MPV", "轿车", "跑车", "皮卡",
        "赛车", "F1", "拉力", "越野",
        "电动自行车", "电动车", "摩托车", "骑行",
        "车展", "汽车展览", "广州车展", "上海车展",
        "二手车", "置换", "折旧",
        "燃油车", "油车", "纯电",
        "出行", "通勤", "代步",
        "汽车生活", "新能源车",
    ],

    # ─── 房产 / Real Estate ───
    "real_estate": [
        "买房", "卖房", "购房", "房价", "房子", "楼盘",
        "房地产", "楼市", "房产", "地产", "开发商",
        "房贷", "贷款", "首付", "按揭", "利率",
        "二手房", "新房", "期房", "现房", "毛坯",
        "物业", "物业费", "房东", "租户", "租房",
        "租金", "出租", "租赁", "中介",
        "装修", "家装", "软装", "硬装", "设计",
        "户型", "面积", "公摊", "得房率", "层高",
        "小区", "社区", "物业", "业主",
        "学区房", "学位", "落户", "户口",
        "政策", "调控", "限购", "限售", "限价",
        "公积金", "公积金贷款", "商贷",
        "下跌", "上涨", "降价", "涨价", "行情",
        "产权", "房产证", "不动产", "登记",
        "豪宅", "别墅", "公寓", "loft",
        "安置房", "保障房", "廉租房", "人才房",
        "住宅", "商铺", "写字楼", "商业",
        "城市规划", "拆迁", "棚改", "旧改",
    ],

    # ─── 国际 / International ───
    "international": [
        "美国", "英国", "法国", "德国", "日本", "韩国",
        "俄罗斯", "印度", "巴西", "加拿大", "澳大利亚",
        "欧盟", "联合国", "北约", "WTO", "IMF",
        "外交", "大使", "外长", "外交部", "领事",
        "国际", "全球", "世界", "海外", "国外",
        "特朗普", "拜登", "普京", "马克龙", "泽连斯基",
        "欧洲", "亚洲", "非洲", "美洲", "中东",
        "地缘", "地缘政治", "冲突", "战争", "制裁",
        "中国外交", "中美关系", "中欧关系", "中俄关系",
        "一带一路", "合作", "峰会", "会谈",
        "联合国大会", "G7", "G20", "APEC", "金砖",
        "叙利亚", "伊朗", "以色列", "巴勒斯坦", "乌克兰",
        "英国脱欧", "欧盟", "欧元", "英镑", "美元",
        "难民", "移民", "签证", "护照", "出入境",
        "海外华人", "华侨", "华裔", "唐人街",
        "国际新闻", "环球", "国际社会",
        "台湾", "两岸", "台海", "台独",
        "日本", "韩国", "朝鲜", "亚洲",
        "争议", "争端", "谈判", "协议",
        "出口", "进口", "贸易", "关税",
        "访问", "出访", "国事访问", "元首",
        "使馆", "领事馆", "大使馆",
    ],

    # ─── 社会 / Social ───
    "social": [
        "社会", "民生", "百姓", "人民", "群众",
        "政策", "法规", "法律", "立法", "司法",
        "政府", "公务员", "官员", "领导",
        "公安", "警察", "检察院", "法院",
        "交通", "地铁", "公交", "道路", "铁路",
        "安全", "事故", "灾难", "火灾", "地震",
        "保护", "环境", "环保", "污染", "生态",
        "维权", "投诉", "举报", "曝光",
        "公益", "慈善", "捐款", "志愿者",
        "就业", "失业", "工资", "劳动", "合同",
        "结婚", "离婚", "婚姻", "家庭", "婚恋",
        "养老", "老人", "老年人", "老龄化",
        "儿童", "孩子", "青少年", "未成年人",
        "女性", "妇女", "性别", "平等", "家暴",
        "暴力", "犯罪", "盗窃", "诈骗", "抢劫",
        "消防", "救援", "急救", "求助",
        "举报", "投诉", "维权", "起诉",
        "法律", "律师", "法院", "立法",
        "社保", "医保", "养老金", "低保",
        "教育改革", "医疗改革", "政策",
        "劳动者", "农民工", "工人", "职工",
        "公共", "设施", "服务", "便民",
        "乡村", "农村", "三农", "扶贫",
        "城市", "社区", "街道", "城中村",
        "争议", "冲突", "纠纷", "矛盾",
        "调查", "监管", "执法", "管理",
        "云南", "四川", "湖南", "河南", "山东",
        "广东", "浙江", "江苏", "上海", "北京",
        # Weather & disasters
        "暴雨", "降雨", "汛情", "龙卷风", "台风", "高温", "冰雹",
        "洪水", "积水", "洪灾", "干旱", "寒潮", "暴雪", "强降雨",
        "大暴雨", "大到暴雨", "防汛", "应急响应",
        # Crime & justice
        "死刑", "判刑", "刑拘", "刑侦", "凶手", "杀人",
        "致死", "死亡", "身亡", "遇难", "失联", "被困",
        "被抓", "被查", "立案", "侦查", "起诉", "庭审",
        # Mining accidents
        "矿难", "煤矿", "瓦斯", "爆炸", "矿井", "下井",
        # Rumor control
        "谣言", "辟谣", "净网", "网传", "假的", "不实信息",
        # Government
        "市长", "省长", "书记", "局长", "全总", "总工会",
        "纪委", "落马",
        # Animals & pets
        "宠物", "狗", "猫", "蛇", "蟒蛇",
        # Other
        "民警", "警方", "媒体", "新闻", "通报", "发布",
        "逝世", "去世", "袁隆平", "纪念",
        "文化", "强国", "精神", "传统",
        "农业", "农民", "小麦", "种粮", "收割", "养殖",
        "猪", "牛", "羊",
    ],

    # ─── 军事 / Military ───
    "military": [
        "军事", "军队", "部队", "国防", "军事演习",
        "解放军", "陆军", "海军", "空军", "火箭军",
        "武器", "装备", "导弹", "战机", "军舰",
        "坦克", "火炮", "枪械", "弹药", "无人机",
        "核武器", "核弹", "核潜艇", "核动力",
        "航母", "航空母舰", "驱逐舰", "护卫舰",
        "歼", "歼击机", "战斗机", "轰炸机",
        "训练", "演习", "军演", "阅兵",
        "战争", "冲突", "作战", "战斗", "战役",
        "边境", "边界", "领海", "领空", "主权",
        "退役", "现役", "服役", "军工",
        "军官", "士兵", "战士", "退伍",
        "军事基地", "驻军", "部署",
        "台海", "南海", "钓鱼岛", "藏南",
        "军售", "军援", "军备", "军费",
        "反恐", "维和", "安全", "国防部",
        "美军", "俄军", "乌军", "以军",
        "战略", "战术", "杀伤", "打击",
        "舰艇", "潜艇", "巡洋舰", "两栖",
        "兵种", "编制", "番号", "师团",
        "国防预算", "军事科技", "军工产业",
        "环台岛", "军演", "演习",
    ],

    # ─── 动漫 / Anime ───
    "anime": [
        "动漫", "动画", "漫画", "番剧", "新番",
        "二次元", "日漫", "国漫", "漫改",
        "火影忍者", "海贼王", "死神", "龙珠",
        "鬼灭之刃", "咒术回战", "进击的巨人",
        "柯南", "名侦探柯南", "哆啦A梦",
        "宫崎骏", "新海诚", "吉卜力",
        "B站", "bilibili", "番剧",
        "国产动画", "动漫杂谈",
        "cos", "cosplay", "漫展", "同人",
        "手办", "模型", "周边", "盲盒",
        "声优", "配音", "CV",
        "剧场版", "OVA", "TV版",
        "画风", "人设", "剧情", "漫评",
        "原神", "崩坏", "星穹铁道", "二次元游戏",
        "鬼畜", "鬼畜剧场",
        "宅舞", "翻唱", "演奏",
    ],
}

# Combined keywords for searching (compile once)
def compile_keywords():
    """Flatten keyword map for efficient matching, storing original category."""
    result = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            result.append((kw.lower(), cat))
    # Sort by length descending so longer (more specific) keywords match first
    result.sort(key=lambda x: -len(x[0]))
    return result

FLAT_KEYWORDS = compile_keywords()


def categorize_text(text: str) -> str:
    """Match text (keyword + title + summary combined) against keyword list."""
    if not text:
        return None
    text_lower = text.lower()
    for kw, cat in FLAT_KEYWORDS:
        if kw in text_lower:
            return cat
    return None


def backup_db():
    """Create a timestamped backup of clean_data.db."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return None
    backup_dir = os.path.join(os.path.dirname(DB_PATH), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    import datetime
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"clean_data_{ts}.db")
    shutil.copy2(DB_PATH, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path


def get_stats(conn):
    """Get category distribution statistics."""
    cur = conn.execute("""
        SELECT category, COUNT(*) as cnt
        FROM clean_trend
        GROUP BY category
        ORDER BY cnt DESC
    """)
    rows = cur.fetchall()
    total = sum(r[1] for r in rows)
    stats = {}
    for cat, cnt in rows:
        stats[cat] = {"count": cnt, "pct": round(cnt / total * 100, 1)}
    stats["_total"] = total
    return stats


def print_stats(stats, label="Category Distribution"):
    """Pretty print category statistics."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    total = stats.get("_total", sum(s["count"] for k, s in stats.items() if not k.startswith("_")))
    for cat, data in sorted(stats.items(), key=lambda x: -x[1]["count"] if isinstance(x[1], dict) and "count" in x[1] else 0):
        if cat == "_total":
            continue
        bar = "█" * int(data["pct"] / 2)
        print(f"  {cat:25s} {data['count']:5d} ({data['pct']:5.1f}%) {bar}")
    print(f"  {'─'*50}")
    print(f"  {'TOTAL':25s} {total:5d}")


def main():
    print("🔍 Chinese Trending Data API — Recategorization Tool")
    print(f"📂 Database: {DB_PATH}")

    # ── Step 1: Backup ──
    print("\n📦 Creating backup...")
    backup_path = backup_db()
    if not backup_path:
        return

    # ── Step 2: Connect & analyze ──
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    total_rows = conn.execute("SELECT COUNT(*) FROM clean_trend").fetchone()[0]
    print(f"\n📊 Total records: {total_rows}")

    before_stats = get_stats(conn)
    print_stats(before_stats, "Before Recategorization")

    general_normal = conn.execute(
        "SELECT COUNT(*) FROM clean_trend WHERE category IN ('general', 'normal')"
    ).fetchone()[0]
    print(f"\n🔴 Records to recategorize: {general_normal} (general + normal)")

    # ── Step 3: Fetch all 'general' and 'normal' records ──
    rows = conn.execute("""
        SELECT id, keyword, title, content_clean, source, category
        FROM clean_trend
        WHERE category IN ('general', 'normal')
    """).fetchall()
    print(f"📥 Loaded {len(rows)} records for recategorization")

    # ── Step 4: Apply keyword matching ──
    updates = {}
    no_match = 0
    matched_categories = Counter()

    for row in rows:
        # Combine all text fields for matching
        text_fields = " ".join(filter(None, [
            row["keyword"],
            row["title"],
            row["content_clean"],
        ]))

        new_cat = categorize_text(text_fields)
        if new_cat:
            updates[row["id"]] = new_cat
            matched_categories[new_cat] += 1
        else:
            # Don't update if no match found — keep as general/normal
            no_match += 1

    print(f"\n🎯 Keyword matching results:")
    print(f"   ✓ Matched: {len(updates)} records (→ new categories)")
    print(f"   ✗ No match: {no_match} records (stayed as-is)")
    print(f"\n📈 Distribution of new assignments:")
    for cat, cnt in matched_categories.most_common():
        print(f"   {cat:25s} {cnt:4d}")

    # ── Step 5: Apply updates ──
    if updates:
        print(f"\n💾 Applying {len(updates)} updates to database...")
        cursor = conn.cursor()
        update_count = 0
        for row_id, new_cat in updates.items():
            cursor.execute(
                "UPDATE clean_trend SET category = ? WHERE id = ?",
                (new_cat, row_id)
            )
            update_count += 1
            if update_count % 200 == 0:
                conn.commit()
                print(f"   ... {update_count} / {len(updates)} updated")
        conn.commit()
        print(f"✅ Successfully updated {update_count} records")

    # ── Step 6: Show after stats ──
    after_stats = get_stats(conn)
    print_stats(after_stats, "After Recategorization")

    # ── Step 7: Summary ──
    general_after = conn.execute(
        "SELECT COUNT(*) FROM clean_trend WHERE category IN ('general', 'normal')"
    ).fetchone()[0]
    reduction = general_normal - general_after
    pct_reduction = round(reduction / max(general_normal, 1) * 100, 1)

    print(f"\n{'='*60}")
    print(f"  📋 FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"  Before: {general_normal} records in 'general'/'normal'")
    print(f"  After:  {general_after} records in 'general'/'normal'")
    print(f"  Reduced by: {reduction} ({pct_reduction}%)")
    print(f"  General rate: {before_stats.get('general', {}).get('pct', 0)}% → {after_stats.get('general', {}).get('pct', 0)}%")
    print(f"\n  Total records: {total_rows}")
    print(f"  Unique categories: {len([k for k in after_stats if k != '_total'])}")

    conn.close()
    print(f"\n💾 Backup saved at: {backup_path}")
    print("✅ Done!")


if __name__ == "__main__":
    main()
