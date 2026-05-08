from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompt
from agent.tool.agent_tools import (rag_summarize, get_weather, get_user_location,
                            get_user_id, get_current_month, fetch_external_data, fill_context_for_report)
from agent.tool.middleware import (monitor_tool, log_before_model, report_prompt_switch)
from utils.logger_handler import logger


class ReactAgent:
    """
    ReAct Agent 封装类

    优化说明：
    - excute_stream 只输出最终回答，过滤中间思考过程（Thought/Action/Observation）
    - 中间过程通过 logger 记录，方便调试但不暴露给用户
    """
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompt(),
            tools=[rag_summarize, get_weather, get_user_location,
                            get_user_id, get_current_month, fetch_external_data, fill_context_for_report],
            middleware=[monitor_tool, log_before_model, report_prompt_switch]
        )

    def excute_stream(self, query: str):
        """
        执行 Agent 并流式输出最终回答。

        关键优化：过滤中间思考过程
        - ReAct Agent 会产出多轮 Thought/Action/Observation 消息
        - 只有最后一条 AIMessage 才是给用户的最终回答
        - 中间过程记录到日志，不 yield 给前端
        """
        input_dict = {
            "messages": [
                {"role": "user", "content": query}
            ]
        }

        final_answer = ""
        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            content = latest_message.content

            if not content:
                continue

            # 判断是否为最终回答：跳过中间思考过程
            # 中间思考通常包含工具调用特征（如"我需要"、"让我"、"首先"等开头的推理）
            # 最终回答是完整的、面向用户的回复
            msg_type = type(latest_message).__name__

            # 如果消息类型是 AIMessage 且没有 tool_calls，说明是最终回答
            if msg_type == "AIMessage":
                # 检查是否有工具调用（有则为中间思考，无则为最终回答）
                has_tool_calls = hasattr(latest_message, 'tool_calls') and latest_message.tool_calls
                if has_tool_calls:
                    # 中间思考过程，记录日志但不输出给用户
                    logger.debug(f"Agent 中间思考: {content[:100]}...")
                    continue

                # 最终回答，输出给用户
                final_answer = content.strip()

        # 只 yield 最终回答
        if final_answer:
            yield final_answer