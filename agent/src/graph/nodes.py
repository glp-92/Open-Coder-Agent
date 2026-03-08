from config.config import config
from graph.state import AgentState
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode
from model.model import model
from tools.registry import TOOLS_REGISTRY

tool_node = ToolNode(tools=TOOLS_REGISTRY, messages_key="messages")


def explorer_node(state: AgentState):
    """
    Receives current state, decides tool to use based on model decision
    """
    state["steps"] += 1
    if state["steps"] > config.max_steps:
        return {"messages": [AIMessage(content="Stopping: too many steps")]}
    messages = state.get("messages")
    response = model.invoke(messages)
    return {"messages": [response]}


def router_logic(state: AgentState):
    """
    Control function that decides next step
    """
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tool_executor"
    return "end"
