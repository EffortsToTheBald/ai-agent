import os
import random

from utils.logger_handler import logger
from rag.rag_service import RagSummaryService
from langchain_core.tools import tool
from utils.path_tool import get_absolute_path
from utils.config_handler import agent_config
rag_summary_service = RagSummaryService()
user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010"]
month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"]
external_data = {}

@tool(description="基于用户查询，检索相关文档并生成总结")
def rag_summarize(query: str) -> str:
    return rag_summary_service.rag_summarize(query)

@tool(description="获取指定城市的天气信息,传入城市名称，返回字符串")
def get_weather(city: str) -> str:
    # 这里可以调用天气API获取天气信息
    return f"{city}的天气是晴朗，温度25度，空气湿度60%，南风一级，AQI指数21，最近6小时降雨概率极低。"

@tool(description="获取用户所在城市的名称，返回字符串")
def get_user_location() -> str:
    return random.choice(["北京", "上海", "广州", "深圳", "杭州"])

@tool(description="获取用户ID，返回字符串")
def get_user_id() -> str:
    return random.choice(user_ids)

@tool(description="获取当前月份，返回字符串")
def get_current_month() -> str:
    return random.choice(month_arr)

def get_external_data():
    """
    {
        user_id: {
            "month": {"特征": xxx, "效率": xxx},
            "month": {"特征": xxx, "效率": xxx},
             ...
        }
    }
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