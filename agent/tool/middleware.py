from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from typing import Callable
from utils.logger_handler import logger
from langchain.agents.middleware import before_model, wrap_tool_call,dynamic_prompt
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from langchain.agents.factory import ModelRequest
from utils.prompt_loader import load_report_prompt,load_system_prompt

@wrap_tool_call
def monitor_tool(
        request:ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    logger.info(f"工具被调用，工具名称：{request.tool_call['name']}，工具输入：{request.tool_call['args']}")
 
    try:
        response = handler(request) 
        logger.info(f"工具调用完成，工具名称：{request.tool_call['name']}，工具输出：{response}")
        
        if request.tool_call['name'] == "fill_context_for_report":
            request.runtime.context["report"] = True

        return response
    except Exception as e:
        logger.error(f"工具调用出错，工具名称：{request.tool_call['name']}，错误信息：{e}")
        raise e

@before_model    
def log_before_model(
    state: AgentState, # 整个agent 智能体中的状态记录
    runtime: Runtime, # 记录了整个执行过程中的上下文信息
):
    logger.info(f"模型调用前，带有{len(state['messages'])}条消息")
    logger.debug(f"{type(state['messages'][-1]).__name__} | {state['messages'][-1].content}")

    return 

@dynamic_prompt
def report_prompt_switch(request: ModelRequest):
    if request.runtime.context.get("report",False):
        return load_report_prompt()
    return load_system_prompt()