"""LLM富化管道 v2.2 — 带智能分类 + 指数退避重试 + 结构化JSON日志"""
import json
import httpx
import time
import os
import random
import datetime
from typing import Dict, Any, Optional, List
from loguru import logger
from sqlmodel import Session, select
from core.database import (
    RawTrend, CleanTrend,
    raw_engine, clean_engine,
    heat_to_level
)

# ─── 关键词分类映射（用于将general/normal回退分类为有意义的内容类别）───
_CATEGORY_KEYWORDS = {
    "technology": [
        "ai", "人工智能", "大模型", "机器学习", "深度学", "神经网络",
        "chatgpt", "gpt", "openai", "深度求索", "deepseek", "文心一言",
        "通义千问", "讯飞星火", "豆包", "kimi", "claude", "gemini",
        "机器人", "自动驾", "无人驾驶", "智能驾驶", "自动驾驶",
        "芯片", "半导体", "处理器", "cpu", "gpu", "华为", "麒麟",
        "高通", "英伟达", "nvidia", "amd", "英特尔", "intel",
        "手机", "智能手机", "iphone", "安卓", "ios", "鸿蒙", "harmonyos",
        "小米", "oppo", "vivo", "荣耀", "三星", "苹果",
        "5g", "6g", "wifi", "蓝牙", "物联网", "iot",
        "vr", "ar", "mr", "元宇宙", "区块链", "nft",
        "软件", "编程", "代码", "开发者", "开源", "linux", "windows",
        "数据", "大数据", "云计算", "云服务", "服务器", "数据库",
        "算法", "推荐算法", "数字人", "虚拟人", "aigc",
        "数码", "电子", "科技", "科学技术", "科研", "实验室",
        "航天", "火箭", "卫星", "太空", "宇宙", "飞船",
        "spacex", "星舰", "nasa", "嫦娥", "天宫", "空间站",
        "神舟", "载人飞船", "长征", "火箭发射",
        "专利", "创新", "黑科技", "数码产品", "可穿戴",
        "电脑", "笔记本", "平板", "耳机", "智能家居",
        "屏幕", "显示器", "分辨率", "折叠屏", "全面屏",
        "影像", "相机", "摄像头", "拍照", "摄影",
        "充电", "快充", "电池", "续航", "无线充",
        "操作系统", "系统更新", "应用",
    ],
    "finance": [
        "a股", "股市", "股票", "基金", "理财", "投资", "散户",
        "涨停", "跌停", "牛市", "熊市", "大盘", "指数",
        "上证", "深证", "创业板", "科创板", "北交所",
        "美股", "港股", "纳斯达克", "道琼斯", "标普",
        "期货", "外汇", "黄金", "比特币", "加密货", "数字货币",
        "央行", "降息", "加息", "降准", "利率", "汇率",
        "gdp", "cpi", "通胀", "通缩", "经济", "经济数据",
        "财政", "货币政策", "财政政策", "赤字", "国债",
        "买房", "房价", "楼市", "房地产", "房贷", "首付",
        "企业", "公司", "上市", "ipo", "融资", "营收",
        "利润", "财报", "业绩", "亏损", "盈利", "市值",
        "亿万", "千万", "百万", "财富", "富豪", "福布斯",
        "消费", "零售", "电商", "双十一", "618", "促销",
        "贸易", "关税", "出口", "进口", "贸易战", "制裁",
        "就业", "失业", "工资", "薪酬", "涨薪", "裁员",
        "税务", "税收", "个人所得", "增值税", "退税",
        "保费", "保险", "养老", "社保", "公积金",
        "金融", "银行", "贷款", "信贷", "理财", "存款",
        "创业", "融资", "天使轮", "a轮", "b轮",
        "跨境", "出海", "外贸", "供应链", "产业链",
        "产能", "产量", "供应", "需求", "涨价", "降价",
        "补贴", "消费券", "经济复苏",
        "科创", "科创50",
    ],
    "entertainment": [
        "明星", "演员", "歌手", "导演", "艺人", "偶像",
        "电影", "电视剧", "综艺", "选秀", "真人秀", "节目",
        "票房", "上映", "首映", "预告", "片场", "角色",
        "音乐", "专辑", "演唱会", "歌曲", "乐队",
        "舞蹈", "舞台", "表演", "演出", "观众",
        "热搜", "热搜榜", "话题", "粉丝", "应援",
        "微博", "文娱", "娱乐", "娱乐圈",
        "绯闻", "恋情", "离婚", "结婚", "分手", "复合",
        "出轨", "劈腿", "塌房", "翻车", "人设",
        "代言", "商务", "广告", "杂志", "封面",
        "戛纳", "奥斯卡", "金鸡奖", "金马奖", "金像奖", "奖项",
        "直播", "带货", "网红", "主播", "短视频",
        "抖音", "快手", "b站", "bilibili", "小红书",
        "爱奇艺", "腾讯视频", "优酷", "芒果tv", "netflix",
        "好莱坞", "华语", "导演", "制片",
        "综艺节目", "真人秀", "脱口秀", "相声", "小品",
        "春晚", "跨年", "晚会", "盛典", "颁奖",
        "微博之夜", "白玉兰", "飞天奖", "华表奖",
        "拍戏", "剧组", "片酬", "签约", "经纪",
        "音乐节", "live",
        "新歌", "新专辑", "单曲", "mv",
        "杨幂", "赵丽颖", "迪丽热巴", "肖战", "王一博",
        "易烊千玺", "王俊凯", "王源", "蔡徐坤", "刘亦菲",
        "周杰伦", "林俊杰", "陈奕迅", "邓紫棋", "张艺兴",
        "刘德华", "周星驰", "成龙", "梁朝伟", "张国荣",
        "演技", "影视", "剧集", "角色",
        "杨紫", "潘玮柏", "面瘫",
    ],
    "sports": [
        "nba", "cba", "足球", "篮球", "排球", "网球", "乒乓球",
        "羽毛球", "高尔夫", "橄榄球", "棒球", "冰球",
        "奥运会", "冬奥", "亚运", "大运", "全运",
        "世界杯", "欧洲杯", "英超", "西甲", "德甲", "意甲", "法甲",
        "欧冠", "亚冠", "中超", "中甲",
        "冠军", "亚军", "季军", "金牌", "银牌", "铜牌",
        "运动员", "教练", "裁判", "比赛", "赛事", "联赛",
        "进球", "得分", "助攻", "篮板", "抢断", "盖帽",
        "mvp", "全明星", "总决赛", "季后赛",
        "f1", "赛车", "拉力赛", "摩托车", "越野",
        "电竞", "电子竞技", "lpl", "kpl", "英雄联盟", "lol",
        "王者荣耀", "dota", "csgo", "绝地求生", "吃鸡",
        "中国女排", "中国男篮", "中国女篮", "国足", "男足",
        "姚明", "刘翔", "李娜", "苏炳添", "谷爱凌",
        "詹姆斯", "库里", "杜兰特", "乔丹", "科比",
        "梅西", "c罗", "姆巴佩", "内马尔", "哈兰德",
        "武磊", "张继科", "马龙", "孙颖莎", "樊振东",
        "游泳", "田径", "体操", "举重", "跳水",
        "拳击", "ufc", "综合格斗", "武术", "太极",
        "马拉松", "跑步", "健身", "瑜伽",
        "体育总局", "足协", "篮协", "体育赛事",
        "跳台", "滑雪", "滑冰", "花样滑冰", "短道速滑",
        "女篮", "女足", "男篮",
        "郑钦文", "法网",
        "文班亚马", "马刺",
    ],
    "gaming": [
        "游戏", "手游", "网游", "端游", "单机游戏", "独立游戏",
        "王者荣耀", "和平精英", "原神", "崩坏", "星穹铁道",
        "英雄联盟", "lol", "dota", "csgo", "cs2", "瓦罗兰特",
        "valorant", "守望先锋", "ow", "绝地求生", "pubg",
        "永劫无间", "逆水寒", "剑网3", "梦幻西游", "大话西游",
        "我的世界", "minecraft", "塞尔达", "任天堂", "switch",
        "playstation", "ps5", "ps4", "xbox", "steam", "epic",
        "游戏机", "主机", "掌机",
        "宝可梦", "pokemon", "动物森友会", "动森",
        "米哈游", "腾讯游戏", "网易游戏", "完美世界",
        "游戏攻略", "游戏更新", "新英雄", "新皮肤",
        "乙女游戏", "女性向", "二次元", "抽卡", "氪金",
        "黑神话", "黑神话悟空",
        "拳皇", "街霸", "格斗游戏", "模拟器",
        "开黑", "组队", "排位", "段位", "上分",
        "游戏主播", "游戏直播", "电竞选手", "职业选手",
        "dlc", "资料片", "扩展包",
        "评测", "测评", "试玩",
        "主机游戏", "独立游戏", "3a大作",
        "tga", "金摇杆",
        "第五人格", "阴阳师", "明日方舟", "碧蓝航线",
        "手机游戏", "网络游戏", "电子竞技", "桌游棋牌",
    ],
    "health": [
        "健康", "医疗", "医院", "医生", "护士", "患者",
        "疾病", "病毒", "细菌", "疫情", "新冠", "疫苗",
        "癌症", "肿瘤", "心梗", "脑梗", "中风", "糖尿病",
        "高血压", "高血脂", "肥胖", "减肥", "减重",
        "运动", "健身", "锻炼", "瑜伽", "跑步",
        "营养", "饮食", "食谱", "养生", "保健", "中医",
        "药物", "药品", "中药", "西药", "处方", "医保",
        "手术", "治疗", "康复", "体检", "检查",
        "心理", "抑郁", "焦虑", "压力", "睡眠",
        "失眠", "熬夜", "疲劳", "医药", "临床", "研究",
        "卫健委", "疾控", "公共卫生",
        "针灸", "按摩", "理疗", "护理",
        "头发", "脱发", "皮肤", "护肤", "美容",
        "眼睛", "视力", "近视", "眼科", "牙科",
        "食品安全", "食品", "添加剂", "防腐剂",
        "生育", "怀孕", "孕妇", "产后", "育儿",
        "老龄化", "养老", "长寿", "基因",
        "过敏", "哮喘", "流感", "感冒",
        "养生", "食疗", "药膳", "保健品",
    ],
    "education": [
        "教育", "学校", "大学", "学院", "中学", "小学",
        "高考", "中考", "考研", "考公", "考编", "考证",
        "考试", "成绩", "分数", "录取", "招生", "入学",
        "学生", "老师", "教师", "教授", "校长", "导师",
        "课程", "课堂", "教学", "作业",
        "留学", "出国", "海外", "国际学校", "交换",
        "培训", "补习", "辅导", "家教", "网课",
        "毕业", "学位", "博士", "硕士", "本科", "专科",
        "论文", "科研", "学术", "研究", "实验",
        "图书馆", "教材", "课本", "教辅", "试卷",
        "学前教育", "幼儿园", "早教", "启蒙",
        "职业教育", "技校", "技能",
        "素质教育", "双减", "减负", "教育改革",
        "公务员", "国考", "省考", "事业单位",
        "985", "211", "双一流", "北大", "清华",
        "考研上岸", "考研国家线", "分数线",
        "寒假", "暑假", "放假", "开学",
        "自习", "学霸",
        "专升本", "保研", "推免",
        "毕业季", "论文答辩", "学位证", "毕业证",
        "少儿", "青少年", "儿童", "亲子",
        "考试大纲", "备考", "复习", "冲刺",
        "教育局", "教育部", "教育政策",
    ],
    "travel": [
        "旅游", "旅行", "出游", "出行", "度假", "休闲",
        "景点", "景区", "风景", "名胜", "古镇", "公园",
        "酒店", "民宿", "客栈", "度假村",
        "机票", "高铁", "火车", "自驾", "租车",
        "航班", "航空", "机场", "登机", "值机", "转机",
        "签证", "护照", "入境", "出境", "海关",
        "导游", "旅行社", "跟团", "自由行", "攻略",
        "五一", "国庆", "春节", "长假", "黄金周", "小长假",
        "国内游", "国外游", "出境游", "周边游",
        "海岛", "沙滩", "海边", "海滩",
        "爬山", "徒步", "露营", "户外",
        "美食", "小吃", "餐厅",
        "拍照", "打卡", "网红景点",
        "穷游", "背包客", "自驾游", "房车",
        "博物馆", "美术馆", "展览", "展馆",
        "滑雪", "温泉", "游乐场", "主题公园",
        "迪士尼", "环球影城", "方特", "欢乐谷",
        "摄影", "旅拍", "风光",
        "出国", "境外", "跨国",
        "城市漫步", "citywalk",
        "古迹", "文化遗址",
    ],
    "food": [
        "美食", "好吃", "美味", "烹饪", "做饭", "下厨",
        "餐厅", "饭店", "餐馆", "小吃", "摊位", "夜市",
        "菜谱", "食谱", "教程", "做法", "烘焙",
        "食材", "配料", "调料", "香料", "厨房",
        "火锅", "烧烤", "烤肉", "炸鸡", "汉堡", "披萨",
        "奶茶", "咖啡", "饮料", "饮品", "茶饮",
        "水果", "蔬菜", "肉类", "海鲜",
        "面包", "蛋糕", "甜点", "冰淇淋",
        "中国菜", "川菜", "粤菜", "湘菜", "鲁菜", "淮扬菜",
        "日料", "寿司", "刺身", "韩餐", "西餐",
        "面条", "米饭", "水饺", "饺子", "馄饨", "包子",
        "外卖", "点餐", "送餐",
        "吃货", "探店", "打卡", "美食博主", "美食家",
        "超市", "菜市场", "买菜",
        "烹饪比赛", "厨师", "厨艺", "料理",
        "品尝", "试吃", "品鉴", "美食节",
        "减肥餐", "健康饮食", "轻食", "沙拉",
        "美食制作", "美食侦探", "美食记录",
        "食堂",
    ],
    "fashion": [
        "时尚", "穿搭", "搭配", "着装", "衣服",
        "服装", "服饰", "衣橱", "衣柜", "穿衣",
        "品牌", "奢侈品", "大牌", "高定", "设计师",
        "lv", "gucci", "香奈儿", "爱马仕", "迪奥", "dior",
        "巴黎世家", "balenciaga", "prada", "fendi",
        "鞋子", "运动鞋", "球鞋", "高跟鞋",
        "包包", "包袋", "手袋", "配饰", "首饰",
        "化妆", "化妆品", "美妆", "护肤", "护肤品",
        "口红", "粉底", "眼影", "腮红", "面膜",
        "发型", "染发", "美发", "剪发", "造型",
        "模特", "走秀", "时装周", "米兰", "巴黎",
        "潮流", "潮牌", "联名", "限定",
        "二手", "闲置", "转卖", "中古", "vintage",
        "改造", "diy", "手工", "手作",
        "简约", "复古", "日系", "韩系", "欧美",
        "显瘦", "显高", "遮肉", "配色",
        "香水", "香氛",
        "美容", "整形", "医美", "微整",
        "女装", "男装", "童装",
    ],
    "auto": [
        "汽车", "车型", "新车", "买车", "卖车",
        "新能源", "电动车", "电动汽车", "混动", "插混",
        "特斯拉", "比亚迪", "蔚来", "小鹏", "理想",
        "小米汽车", "华为汽车", "问界", "智界", "享界",
        "极氪", "岚图", "阿维塔", "深蓝", "零跑",
        "bba", "奔驰", "宝马", "奥迪", "保时捷",
        "丰田", "本田", "大众", "日产", "福特",
        "发动机", "变速箱", "底盘", "悬挂",
        "试驾", "评测", "测评", "驾驶", "驾乘",
        "油耗", "续航", "充电", "加油", "省油",
        "自动驾驶", "智能驾驶", "辅助驾驶",
        "交通", "路况", "违章", "事故",
        "保养", "维修", "配件", "改装",
        "考驾照", "驾照", "驾考", "驾校",
        "停车场", "停车", "车位",
        "suv", "mpv", "轿车", "跑车", "皮卡",
        "赛车", "f1", "拉力", "越野",
        "电动自行车", "摩托车", "骑行",
        "车展", "广州车展", "上海车展",
        "二手车", "置换", "折旧",
        "燃油车", "油车", "纯电",
        "通勤", "代步",
        "汽车生活", "新能源车",
    ],
    "real_estate": [
        "买房", "卖房", "购房", "房价", "房子", "楼盘",
        "房地产", "楼市", "房产", "地产", "开发商",
        "房贷", "贷款", "首付", "按揭",
        "二手房", "新房", "期房", "现房", "毛坯",
        "物业", "物业费", "房东", "租户", "租房",
        "租金", "出租", "租赁", "中介",
        "装修", "家装", "软装", "硬装", "设计",
        "户型", "面积", "公摊", "得房率", "层高",
        "小区", "社区", "业主",
        "学区房", "学位", "落户", "户口",
        "政策", "调控", "限购", "限售", "限价",
        "公积金", "公积金贷款", "商贷",
        "下跌", "上涨", "降价", "涨价", "行情",
        "产权", "房产证", "不动产", "登记",
        "豪宅", "别墅", "公寓", "loft",
        "安置房", "保障房", "廉租房", "人才房",
        "住宅", "商铺", "写字楼",
        "城市规划", "拆迁", "棚改", "旧改",
    ],
    "international": [
        "美国", "英国", "法国", "德国", "日本", "韩国",
        "俄罗斯", "印度", "巴西", "加拿大", "澳大利亚",
        "欧盟", "联合国", "北约", "wto", "imf",
        "外交", "大使", "外长", "外交部", "领事",
        "国际", "全球", "世界", "海外", "国外",
        "特朗普", "拜登", "普京", "马克龙", "泽连斯基",
        "欧洲", "亚洲", "非洲", "美洲", "中东",
        "地缘", "地缘政治", "冲突", "战争", "制裁",
        "中国外交", "中美关系", "中欧关系", "中俄关系",
        "一带一路", "合作", "峰会", "会谈",
        "联合国大会", "g7", "g20", "apec", "金砖",
        "叙利亚", "伊朗", "以色列", "巴勒斯坦", "乌克兰",
        "英国脱欧", "欧元", "英镑", "美元",
        "难民", "移民", "签证", "护照", "出入境",
        "海外华人", "华侨", "华裔", "唐人街",
        "国际新闻", "环球", "国际社会",
        "台湾", "两岸", "台海", "台独",
        "朝鲜",
        "争议", "争端", "谈判", "协议",
        "出口", "进口", "贸易", "关税",
        "访问", "出访", "国事访问", "元首",
        "使馆", "领事馆", "大使馆",
    ],
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
        "教育改革", "医疗改革",
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
        "宠物", "蛇", "蟒蛇",
        # Other
        "民警", "警方", "媒体", "新闻", "通报", "发布",
        "逝世", "去世", "袁隆平", "纪念",
        "文化", "强国", "精神", "传统",
        "农业", "农民", "小麦", "种粮", "收割", "养殖",
    ],
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
        "反恐", "维和", "国防部",
        "美军", "俄军", "乌军", "以军",
        "战略", "战术", "杀伤", "打击",
        "舰艇", "潜艇", "巡洋舰", "两栖",
        "兵种", "编制", "番号", "师团",
        "国防预算", "军事科技", "军工产业",
        "环台岛",
    ],
    "anime": [
        "动漫", "动画", "漫画", "番剧", "新番",
        "二次元", "日漫", "国漫", "漫改",
        "火影忍者", "海贼王", "死神", "龙珠",
        "鬼灭之刃", "咒术回战", "进击的巨人",
        "柯南", "名侦探柯南", "哆啦a梦",
        "宫崎骏", "新海诚", "吉卜力",
        "国产动画", "动漫杂谈",
        "cos", "cosplay", "漫展", "同人",
        "手办", "模型", "周边", "盲盒",
        "声优", "配音", "cv",
        "剧场版", "ova",
        "画风", "人设", "剧情", "漫评",
        "鬼畜", "鬼畜剧场",
        "宅舞", "翻唱", "演奏",
    ],
}

# Compile keyword list sorted by length descending (longer matches first)
_FLAT_KEYWORDS = sorted(
    [(kw.lower(), cat) for cat, kws in _CATEGORY_KEYWORDS.items() for kw in kws],
    key=lambda x: -len(x[0])
)


def categorize_by_keywords(text: str) -> Optional[str]:
    """Assign a content category by matching Chinese keywords in the text.

    Returns a category string like 'entertainment', 'technology', etc.,
    or None if no keywords match.
    """
    if not text:
        return None
    text_lower = text.lower()
    for kw, cat in _FLAT_KEYWORDS:
        if kw in text_lower:
            return cat
    return None


# ─── LLM配置（从环境变量读取）───
API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = "deepseek-v4-flash"
# 调用间隔（秒）— 降低限频风险
CALL_DELAY = 3.0

# ─── JSON 日志文件（用于Grafana对接）───
JSON_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "enrichment.jsonl")
os.makedirs(os.path.dirname(JSON_LOG_PATH), exist_ok=True)


def log_json(event: str, data: dict):
    """写结构化JSON日志行（一行一个JSON对象，兼容logstash/filebeat）"""
    record = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "event": event,
        **data,
    }
    with open(JSON_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def call_llm_with_retry(payload: dict, headers: dict,
                         max_retries: int = 3,
                         base_delay: float = 1.0) -> Optional[Dict]:
    """调用LLM API，遇到429/5xx时指数退避重试（带随机抖动jitter）"""
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limited — 指数退避 + 随机jitter
                    delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                    logger.warning(
                        f"429限流，第{attempt}次重试，等待{delay:.1f}s"
                    )
                    log_json("llm_retry", {
                        "attempt": attempt,
                        "delay": round(delay, 2),
                        "status": 429,
                        "model": MODEL,
                    })
                    time.sleep(delay)
                    last_error = f"429 after {attempt} retries"
                elif response.status_code in (502, 503, 504):
                    # 服务器临时错误 — 也重试
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"服务暂时不可用 {response.status_code}，第{attempt}次重试"
                    )
                    time.sleep(delay)
                    last_error = f"{response.status_code} after {attempt} retries"
                else:
                    logger.error(f"LLM请求失败 {response.status_code}: {response.text[:200]}")
                    log_json("llm_error", {
                        "status": response.status_code,
                        "detail": response.text[:200],
                        "model": MODEL,
                    })
                    return None  # 非重试错误直接放弃
        except httpx.TimeoutException:
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"LLM超时，第{attempt}次重试")
            time.sleep(delay)
            last_error = f"timeout after {attempt} retries"
        except Exception as e:
            logger.error(f"LLM异常: {e}")
            log_json("llm_error", {"error": str(e), "model": MODEL})
            return None

    logger.error(f"LLM重试耗尽 ({max_retries}次): {last_error}")
    log_json("llm_exhausted", {
        "max_retries": max_retries,
        "last_error": last_error,
        "model": MODEL,
    })
    return None


def enrich_with_llm(title: str, summary: str, source: str,
                     heat: int, rank: int, category: str) -> Optional[Dict[str, Any]]:
    """调用LLM进行增值富化：翻译 + 行业标签 + 变现建议
    
    核心原则：LLM不虚构评分，只做人类需要阅读/推理才能完成的事。
    真实热度数据直接从平台获取，不经过LLM判断。
    """
    # 截断过长摘要防止LLM超时（百度摘要可达400+字符）
    if len(summary) > 200:
        summary = summary[:197] + "..."

    prompt = f"""You are a professional cross-border e-commerce and social media trend analyst. Your client is a dropshipper, marketer, or brand owner looking to monetize Chinese trending topics on global platforms (TikTok, Instagram, Amazon).

## Trend Data (real engagement metrics)
- Title: {title}
- Summary: {summary}
- Source Platform: {source}
- Real Heat Score: {heat} (actual platform engagement count)
- Real Rank: #{rank}
- Platform Category: {category}

## Your Task
Analyze this trend and respond with ONLY a JSON object containing:

1. **translated_title**: Professional English title translation optimized for international audiences.
2. **translated_summary**: Concise, grammatically correct English summary of the trend.
3. **industry_tags**: Array of 2-4 professional English industry tags (e.g. ["Electric Vehicles", "Consumer Electronics"]).
4. **monetization_tags**: Array of 2-3 actionable English tags describing WHAT products/categories this trend can help sell (e.g. ["Phone Accessories", "Car Gadgets", "Tech Reviews"]). Be specific and practical for dropshippers.
5. **monetization_potential**: A brief 1-sentence explanation of how a business could exploit this trend.
6. **content_type**: One of: "product_launch", "celebrity_news", "policy", "technology", "lifestyle", "entertainment", "finance", "sports", "social_topic"

Respond with ONLY the JSON object. No markdown, no code blocks, no extra text."""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You extract commercial value from Chinese trending topics. Output JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1024
    }

    result = call_llm_with_retry(payload, headers, max_retries=3, base_delay=1.0)
    if result is None:
        return None

    return robust_json_parse(result)


def robust_json_parse(result: dict) -> Optional[Dict[str, Any]]:
    """多策略容错解析LLM返回的JSON，应对DeepSeek的格式问题"""
    import re
    try:
        content = result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError):
        return None

    if not content:
        return None

    strategy = [
        ("直接json.loads", lambda c: _try_json(c)),
        ("strict=False", lambda c: _try_json(c, strict=False)),
        ("正则提取{...}块", lambda c: _try_extract_braces(c)),
        ("修复换行后解析", lambda c: _try_fix_newlines(c)),
        ("单引号→双引号", lambda c: _try_fix_quotes(c)),
        ("ast.literal_eval兜底", lambda c: _try_ast(c)),
    ]

    for name, fn in strategy:
        result = fn(content)
        if result is not None:
            logger.debug(f"✓ JSON解析成功 (策略: {name})")
            return result

    logger.error(f"LLM返回解析失败 (所有策略均失败)")
    log_json("llm_parse_error", {
        "error": "all_strategies_failed",
        "raw_content": content[:300],
    })
    return None


def _try_json(c, strict=True):
    try:
        cleaned = c
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:])
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        return json.loads(cleaned, strict=strict)
    except (json.JSONDecodeError, ValueError):
        return None


def _try_extract_braces(c):
    """正则提取最外层{...} JSON块"""
    import re
    # 先尝试完整{...}匹配
    match = re.search(r'\{[\s\S]*\}', c)
    if match:
        blob = match.group()
        if not blob.endswith('}'):
            last_brace = blob.rfind('}')
            if last_brace > 0:
                blob = blob[:last_brace+1]
        blob = _fix_truncated_json(blob)
        return _try_json(blob, strict=False)
    # 无闭合大括号：尝试 { 到行尾
    match = re.search(r'({[\s\S]*)', c)
    if match:
        blob = match.group(1)
        blob = _fix_truncated_json(blob)
        return _try_json(blob, strict=False)
    return None


def _fix_truncated_json(blob):
    """修复被max_tokens截断的JSON - 补全尾部"""
    import ast
    # 修复未闭合大括号
    opens = blob.count('{')
    closes = blob.count('}')
    if opens > closes:
        blob += '}' * (opens - closes)
    blob = blob.rstrip().rstrip(',')

    # 移除最后一个不完整的key-value对
    lines = blob.split('\n')
    for i in range(len(lines) - 1, -1, -1):
        trial = '\n'.join(lines[:i+1]).rstrip().rstrip(',')
        if trial.endswith('}'):
            try:
                json.loads(trial, strict=False)
                return trial
            except:
                pass
    
    return blob


def _try_fix_newlines(c):
    """修复JSON字符串值中的未转义换行符"""
    import re
    # 找到JSON块
    match = re.search(r'\{[\s\S]*\}', c)
    if not match:
        return None
    blob = match.group()
    # 将字符串值内的换行符替换为 \\n
    # 简单的启发式: 在引号内的换行替换
    in_string = False
    result_chars = []
    for ch in blob:
        if ch == '"' and (not result_chars or result_chars[-1] != '\\'):
            in_string = not in_string
        if in_string and ch in '\n\r':
            result_chars.append('\\n')
        else:
            result_chars.append(ch)
    fixed = ''.join(result_chars)
    if not fixed.endswith('}'):
        fixed += '}'
    fixed = fixed.rstrip().rstrip(',')
    return _try_json(fixed, strict=False)


def _try_fix_quotes(c):
    """尝试将单引号JSON替换为双引号"""
    import re
    match = re.search(r'\{[\s\S]*\}', c)
    if not match:
        return None
    blob = match.group()
    # 将key的单引号替换为双引号
    fixed = re.sub(r"'([^']+)'(\s*:)", r'"\1"\2', blob)
    # 将value的单引号替换为双引号
    fixed = re.sub(r":\s*'([^']+)'", r': "\1"', fixed)
    return _try_json(fixed, strict=False)


def _try_ast(c):
    """Python dict格式兜底 (ast.literal_eval)"""
    import ast, re
    match = re.search(r'\{[\s\S]*\}', c)
    if not match:
        return None
    blob = match.group()
    blob = _fix_truncated_json(blob)
    try:
        return ast.literal_eval(blob)
    except:
        return None


def run_enrichment_pipeline():
    """全量富化管道：读取原始数据 → LLM增强 → 写入清洗库（保留真实热度）"""
    logger.info("=== 开始热点富化 ===")
    log_json("pipeline_start", {"model": MODEL, "provider": "deepseek"})

    stats = {
        "total_raw": 0,
        "skipped": 0,
        "enriched_llm": 0,
        "enriched_raw": 0,
        "errors": 0,
        "sources": {},
        "start_time": datetime.datetime.utcnow().isoformat() + "Z",
    }

    with Session(raw_engine) as raw_session, Session(clean_engine) as clean_session:
        raw_trends = raw_session.exec(select(RawTrend)).all()
        stats["total_raw"] = len(raw_trends)
        logger.info(f"待处理原始数据 {len(raw_trends)} 条")

        enriched_count = 0
        skipped_count = 0

        for raw in raw_trends:
            # 跳过已处理
            stmt = select(CleanTrend).where(CleanTrend.original_id == raw.raw_id)
            if clean_session.exec(stmt).first():
                skipped_count += 1
                stats["skipped"] += 1
                continue

            try:
                trend_data = json.loads(raw.payload)
                keyword = trend_data.get("keyword", "")
                summary = trend_data.get("summary", "")
                heat = trend_data.get("heat", 0) or 0
                rank = trend_data.get("rank", 0) or 0
                category = trend_data.get("category", "general")
                # 关键词分类提升：如果平台给的分类是general/normal，用关键词匹配重新分类
                if category in ("general", "normal"):
                    text_for_cat = " ".join(filter(None, [keyword, summary, trend_data.get("title", "")]))
                    kw_category = categorize_by_keywords(text_for_cat)
                    if kw_category:
                        logger.info(f"  关键词分类 {category}→{kw_category}: {keyword}")
                        category = kw_category
                source_url = trend_data.get("source_url", "")

                logger.info(f"富化 [{raw.source}] {keyword} (热度:{heat})")

                # LLM增强（带指数退避重试）
                enriched = enrich_with_llm(
                    title=keyword,
                    summary=summary,
                    source=raw.source,
                    heat=heat,
                    rank=rank,
                    category=category
                )

                if enriched:
                    clean_trend = CleanTrend(
                        keyword=keyword,
                        source=raw.source,
                        original_id=raw.raw_id,
                        title=keyword,
                        content_clean=summary,
                        source_url=source_url,
                        heat=heat,
                        rank=rank,
                        heat_level=heat_to_level(heat),
                        category=category,
                        tags=",".join(enriched.get("industry_tags", [])),
                        translated_title=enriched.get("translated_title", ""),
                        translated_content=enriched.get("translated_summary", ""),
                        monetization_tags=",".join(enriched.get("monetization_tags", [])),
                        updated_at=raw.scraped_at,
                    )
                    clean_session.add(clean_trend)
                    clean_session.commit()

                    monetization = enriched.get("monetization_potential", "")
                    content_type = enriched.get("content_type", "")
                    m_tags = enriched.get("monetization_tags", [])
                    logger.success(f"  ✓ 完成 | 类型:{content_type} | 变现:{m_tags} | {monetization[:60]}")

                    stats["enriched_llm"] += 1
                    log_json("enrich_success", {
                        "source": raw.source,
                        "keyword": keyword,
                        "heat": heat,
                        "content_type": content_type,
                        "monetization_tags": m_tags,
                    })
                else:
                    # LLM失败时，保留原始数据但标记无增强
                    clean_trend = CleanTrend(
                        keyword=keyword,
                        source=raw.source,
                        original_id=raw.raw_id,
                        title=keyword,
                        content_clean=summary,
                        source_url=source_url,
                        heat=heat,
                        rank=rank,
                        heat_level=heat_to_level(heat),
                        category=category,
                        updated_at=raw.scraped_at,
                    )
                    clean_session.add(clean_trend)
                    clean_session.commit()
                    logger.warning(f"  ⚠ LLM失败，保留原始数据: {keyword}")

                    stats["enriched_raw"] += 1
                    log_json("enrich_fallback", {
                        "source": raw.source,
                        "keyword": keyword,
                        "heat": heat,
                        "reason": "llm_failed",
                    })

                # 按来源统计
                src = raw.source
                if src not in stats["sources"]:
                    stats["sources"][src] = {"total": 0, "llm_ok": 0, "raw": 0}
                stats["sources"][src]["total"] += 1
                if enriched:
                    stats["sources"][src]["llm_ok"] += 1
                else:
                    stats["sources"][src]["raw"] += 1

            except Exception as e:
                clean_session.rollback()
                logger.error(f"处理异常 {raw.raw_id}: {e}")
                stats["errors"] += 1
                log_json("enrich_error", {
                    "original_id": raw.raw_id,
                    "error": str(e),
                })

            time.sleep(CALL_DELAY)  # LLM限流保护

    stats["end_time"] = datetime.datetime.utcnow().isoformat() + "Z"
    stats["duration_seconds"] = round(
        (datetime.datetime.fromisoformat(stats["end_time"].rstrip("Z")) -
         datetime.datetime.fromisoformat(stats["start_time"].rstrip("Z"))).total_seconds(),
        1
    )

    # 输出结构化日志
    log_json("pipeline_complete", stats)
    logger.info(f"=== 富化完成: LLM{stats['enriched_llm']}条 + 原始{stats['enriched_raw']}条, "
                f"跳过{stats['skipped']}条, 耗时{stats['duration_seconds']}s ===")

    # 终端打印摘要
    logger.info(f"📊 富化统计:")
    logger.info(f"  - 总数据: {stats['total_raw']}")
    logger.info(f"  - LLM富化: {stats['enriched_llm']} ({round(stats['enriched_llm']/max(stats['total_raw'],1)*100)}%)")
    logger.info(f"  - 原始保底: {stats['enriched_raw']}")
    logger.info(f"  - 耗时: {stats['duration_seconds']}s")
    for src, s in sorted(stats["sources"].items()):
        rate = round(s["llm_ok"] / max(s["total"], 1) * 100)
        logger.info(f"    {src}: {s['llm_ok']}/{s['total']} ({rate}%)")

    return stats


def refresh_all():
    """强制重新富化所有数据（用于模型升级后）"""
    logger.warning("强制重新富化全量数据...")
    with Session(clean_engine) as session:
        session.exec(CleanTrend.__table__.delete())
        session.commit()
    run_enrichment_pipeline()


if __name__ == "__main__":
    run_enrichment_pipeline()