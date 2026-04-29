from config.config import config
from graph.state import AgentState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from model.model import model, summary_model
from tools.registry import TOOLS_REGISTRY

tool_node = ToolNode(tools=TOOLS_REGISTRY, messages_key="messages")


def _is_repeating_tool_result(messages: list) -> bool:
    recent_non_system = [message for message in messages if message.type != "system"][-8:]
    recent_tool_messages = [message for message in recent_non_system if isinstance(message, ToolMessage)]
    if len(recent_tool_messages) < 2:
        return False
    last_tool = recent_tool_messages[-1]
    prev_tool = recent_tool_messages[-2]
    return last_tool.name == prev_tool.name and str(last_tool.content).strip() == str(prev_tool.content).strip()


def _task_requires_file_changes(messages: list) -> bool:
    first_human = next((message for message in messages if isinstance(message, HumanMessage)), None)
    if not first_human:
        return False
    prompt_text = str(first_human.content).lower()
    write_keywords = [
        "crea",
        "create",
        "implement",
        "estructura",
        "scaffold",
        "refactor",
        "fix",
        "corrige",
        "modifica",
        "build",
    ]
    return any(keyword in prompt_text for keyword in write_keywords)


def _has_successful_write(messages: list) -> bool:
    write_tools = {"make_dir", "make_dirs", "create_file", "write_file"}
    for message in messages:
        if isinstance(message, ToolMessage) and message.name in write_tools:
            content = str(message.content)
            if "Success:" in content:
                return True
    return False


def _last_tool_error(messages: list) -> bool:
    for message in reversed(messages):
        if isinstance(message, ToolMessage):
            return str(message.content).strip().startswith("Error")
        if isinstance(message, AIMessage):
            break
    return False


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
    if _is_repeating_tool_result(all_messages):
        return {
            "steps": steps,
            "messages": [
                AIMessage(
                    content=(
                        "Stopping to avoid a tool loop: same tool result was repeated. "
                        "Use a different tool or finalize with a concise result."
                    )
                )
            ],
        }
    system_message = all_messages[0]
    window_size = config.chat_window_size
    if len(all_messages) > window_size:
        recent_history = all_messages[-window_size:]
        chat_context = [m for m in recent_history if m.type != "system"]
        messages_to_send = [system_message, *chat_context]
    else:
        messages_to_send = all_messages

    if _last_tool_error(all_messages):
        messages_to_send = [
            *messages_to_send,
            HumanMessage(content="The previous tool call failed. Retry with corrected tool arguments."),
        ]
    elif _task_requires_file_changes(all_messages) and not _has_successful_write(all_messages):
        messages_to_send = [
            *messages_to_send,
            HumanMessage(content="This task requires file changes. Use writing tools before finishing."),
        ]

    response = model.invoke(messages_to_send)
    return {"messages": [response], "steps": steps}


def router_logic(state: AgentState):
    """
    Control function that decides next step
    """
    if state.get("steps", 0) < config.max_steps:
        if _last_tool_error(state["messages"]):
            return "retry"
        if _task_requires_file_changes(state["messages"]) and not _has_successful_write(state["messages"]):
            return "retry"

    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tool_executor"
    return "end"
