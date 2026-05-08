import os
import random
from datetime import datetime

import requests
from utils.logger_handler import logger
from rag.rag_service import RagSummaryService
from langchain_core.tools import tool
from utils.path_tool import get_absolute_path
from utils.config_handler import agent_config

# =============================================================================
# Phase 1.1: Mock 工具替换为真实服务
# 说明：将 get_weather / get_user_location / get_current_month 从 Mock 替换为真实实现
#       get_user_id / fetch_external_data 暂保留 Mock，需接入认证系统和数据库后替换
# =============================================================================

rag_summary_service = RagSummaryService()
user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010"]
external_data = {}

@tool(description="基于用户查询，检索相关文档并生成总结")
def rag_summarize(query: str) -> str:
    return rag_summary_service.rag_summarize(query)

@tool(description="获取指定城市的天气信息,传入城市名称，返回包含温度、湿度、天气状况的字符串")
def get_weather(city: str) -> str:
    """
    Phase 1.1 优化：接入 wttr.in 免费天气 API（无需 API Key）
    如需更精确数据，可替换为和风天气/高德天气 API
    """
    try:
        # 使用 wttr.in 的 JSON 格式获取天气
        resp = requests.get(
            f"https://wttr.in/{city}?format=j1",
            timeout=10,
            headers={"Accept-Language": "zh-CN"}
        )
        resp.raise_for_status()
        data = resp.json()
        current = data["current_condition"][0]

        temp = current["temp_C"]           # 温度
        humidity = current["humidity"]     # 湿度
        desc = current["lang_zh"][0]["value"]  # 中文天气描述
        wind_speed = current["windspeedKmph"]  # 风速
        feels_like = current["FeelsLikeC"]     # 体感温度

        return (
            f"{city}当前天气：{desc}，"
            f"温度{temp}°C（体感{feels_like}°C），"
            f"空气湿度{humidity}%，"
            f"风速{wind_speed}km/h。"
        )
    except Exception as e:
        logger.warning(f"天气 API 调用失败，使用降级数据: {e}")
        return f"{city}的天气查询暂时不可用，请稍后再试。"

@tool(description="获取用户所在城市的名称，基于 IP 地址定位，返回字符串")
def get_user_location() -> str:
    """
    Phase 1.1 优化：接入 ip-api.com 免费 IP 定位 API
    如需更高精度，可替换为高德/百度 IP 定位 API
    """
    try:
        resp = requests.get(
            "http://ip-api.com/json/?lang=zh-CN&fields=city,status",
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "success":
            city = data.get("city", "")
            if city:
                logger.info(f"IP 定位成功: {city}")
                return city
        # IP 定位失败时降级
        logger.warning("IP 定位未返回有效城市，使用默认值")
        return "北京"
    except Exception as e:
        logger.warning(f"IP 定位 API 调用失败: {e}，使用默认值")
        return "北京"

@tool(description="获取用户ID，返回字符串")
def get_user_id() -> str:
    """
    Phase 1 说明：此工具需接入认证系统后替换为真实实现
    当前仍为 Mock，实际应从 JWT token / Session 中提取
    TODO: 接入 OAuth2/JWT 认证后，从 request context 获取真实 user_id
    """
    return random.choice(user_ids)

@tool(description="获取当前月份，返回 YYYY-MM 格式字符串")
def get_current_month() -> str:
    """
    Phase 1.1 优化：使用 datetime.now() 返回真实当前月份
    原实现为 random.choice，返回随机月份，这是错误的
    """
    return datetime.now().strftime("%Y-%m")

def get_external_data():
    """
    Phase 1 说明：此函数需接入数据库后替换为真实实现
    当前仍从 CSV 文件读取，实际应接入 PostgreSQL/MySQL
    TODO: 接入数据库后，使用 SQLAlchemy ORM 查询
    """
    if not external_data:
        external_data_path = get_absolute_path(agent_config["external_data_path"])

        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"External data file not found at path: {external_data_path}")

        with open(external_data_path, 'r', encoding='utf-8') as f:
            for line in f.readlines()[1:]:  # skip header
                arr: list[str] = line.strip().split(',')

                user_id: str = arr[0].replace('"', '')
                feature: str = arr[1].replace('"', '')
                efficiency: str = arr[2].replace('"', '')
                consumables: str = arr[3].replace('"', '')
                comparison: str = arr[4].replace('"', '')
                time: str = arr[5].replace('"', '')

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "特征": feature,
                    "efficiency": efficiency,
                    "耗材": consumables,
                    "对比": comparison
                }

@tool(description="根据用户ID和月份查询外部数据，传入用户ID和月份，返回指定用户指定月份的字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    get_external_data()

    try:
        return external_data[user_id][month]
    except KeyError:
        logger.warning(f"未找到用户ID {user_id} 在月份 {month} 的数据。")
        return ""

@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态动态注入上下文场景，为后续提示词切换提供支持")
def fill_context_for_report():
    return "fill context for report 已调用"