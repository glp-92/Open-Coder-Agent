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
    steps = state["steps"] + 1
    if state["steps"] > config.max_steps:
        return {"steps": steps, "messages": [AIMessage(content="Stopping: too many steps")]}
    messages = state.get("messages")
    response = model.invoke(messages)
    return {"steps": steps, "messages": [response]}


def router_logic(state: AgentState):
    """
    Control function that decides next step
    """
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tool_executor"
    return "end"
