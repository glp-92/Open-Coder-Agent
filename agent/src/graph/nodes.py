from config.config import config
from graph.state import AgentState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from model.model import model, summary_model
from tools.registry import TOOLS_REGISTRY

tool_node = ToolNode(tools=TOOLS_REGISTRY, messages_key="messages")


def memory_manager_node(state: AgentState):
    """
    Makes a summary of oldest 'config.messages_to_summarize' messages
    when the maximum amount of messages to make a summary is reached
    """
    messages = state["messages"]
    steps = state.get("steps", 0)
    if len(messages) > config.max_messages_for_summary:
        end_index = 1 + config.messages_to_summarize
        to_summarize = messages[1:end_index]
        summary_prompt = (
            f"Summarize these {len(to_summarize)} messages in compact technical bullet points. "
            "Keep only files changed, tools used, and current task status."
        )
        summary_response = summary_model.invoke([*to_summarize, HumanMessage(content=summary_prompt)])
        summary_message = SystemMessage(
            content=f"--- ACUMULATED SUMMARY ({len(to_summarize)} msgs) ---\n{summary_response.content}"
        )
        return {"messages": [summary_message], "steps": steps}
    return {"steps": steps}


def explorer_node(state: AgentState):
    """
    Receives current state, decides tool to use based on model decision
    """
    steps = state.get("steps", 0) + 1
    if steps > config.max_steps:
        return {"steps": steps, "messages": [AIMessage(content="Stopping: too many steps")]}
    all_messages = state["messages"]
    system_message = all_messages[0]
    window_size = config.chat_window_size
    if len(all_messages) > window_size:
        recent_history = all_messages[-window_size:]
        chat_context = [m for m in recent_history if m.type != "system"]
        messages_to_send = [system_message, *chat_context]
    else:
        messages_to_send = all_messages
    response = model.invoke(messages_to_send)
    return {"messages": [response], "steps": steps}


def router_logic(state: AgentState):
    """
    Control function that decides next step
    """
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tool_executor"
    return "end"
