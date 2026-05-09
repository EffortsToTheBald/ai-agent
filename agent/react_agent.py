from langchain.agents import create_agent
from langchain_core.messages import AIMessage, AIMessageChunk
from model.factory import chat_model
from utils.prompt_loader import load_system_prompt
from agent.tool.agent_tools import (rag_summarize, get_weather, get_user_location,
                            get_user_id, get_current_month, fetch_external_data, fill_context_for_report)
from agent.tool.middleware import (monitor_tool, log_before_model, report_prompt_switch)
from utils.logger_handler import logger


class ReactAgent:
    """
    ReAct Agent 封装类

    使用 stream_mode="messages" 实现流式输出：
    - 过滤中间工具调用阶段的消息（tool_calls / tool_call_chunks）
    - 只 yield 最终回答的文本内容给前端
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

        使用 stream_mode="messages"：
        - 过滤 AIMessage/AIMessageChunk 中的 tool_calls / tool_call_chunks
        - 只有最终回答的文本内容才 yield 给前端
        """
        input_dict = {
            "messages": [
                {"role": "user", "content": query}
            ]
        }

        for msg_chunk, metadata in self.agent.stream(
            input_dict, stream_mode="messages", context={"report": False}
        ):
            if not isinstance(msg_chunk, (AIMessage, AIMessageChunk)):
                continue

            tool_calls = getattr(msg_chunk, 'tool_calls', None) or []
            tool_call_chunks = getattr(msg_chunk, 'tool_call_chunks', None) or []
            if tool_calls or tool_call_chunks:
                logger.debug("Agent 中间思考阶段，跳过")
                continue

            content = msg_chunk.content or ''
            if content:
                yield content
