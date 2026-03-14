from config.config import config
from graph.state import AgentState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from model.model import model
from tools.registry import TOOLS_REGISTRY

tool_node = ToolNode(tools=TOOLS_REGISTRY, messages_key="messages")


def memory_manager_node(state: AgentState):
    """
    Makes a summary of oldest messages keeping last 3 entire on memory
    """
    messages = state["messages"]
    steps = state.get("steps", 0)
    if len(messages) > config.max_messages_for_summary:
        system_prompt = messages[0]
        immediate_context = messages[-3:]
        to_summarize = messages[1:-3]
        summary_prompt = (
            "Summarize the actions taken and code changes made so far. "
            "This summary will serve as a reference for continuing the task."
        )
        summary_response = model.invoke([*to_summarize, HumanMessage(content=summary_prompt)])
        summary_message = SystemMessage(content=f"Summary from past steps: {summary_response.content}")
        return {"messages": [system_prompt, summary_message, *immediate_context], "steps": steps}
    return {"steps": steps}


def explorer_node(state: AgentState):
    """
    Receives current state, decides tool to use based on model decision
    """
    steps = state.get("steps", 0) + 1
    if state["steps"] > config.max_steps:
        return {"steps": steps, "messages": [AIMessage(content="Stopping: too many steps")]}
    msgs = state["messages"]
    filtered_messages = (
        [msgs[0], *msgs[-config.max_chat_history :]] if len(msgs) > config.max_chat_history + 1 else msgs
    )
    response = model.invoke(filtered_messages)
    return {"messages": [response], "steps": state["steps"] + 1}


def router_logic(state: AgentState):
    """
    Control function that decides next step
    """
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tool_executor"
    return "end"
