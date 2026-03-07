import json
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from tools.registry import TOOL_REGISTRY


class AgentState(TypedDict):
    user_input: str
    branch_name: str
    agent_config_prompt: str
    root_project_path: str
    project_tree: str | None
    file_content: dict[str, str]
    file_symbols: dict[str, str]
    target_files: list[str]
    last_search: str | None
    last_diff: str | None
    execution_plan: list[dict]
    plan_finished: bool


def planner_node(state: AgentState, model):
    user_input = state.get("user_input", "")
    messages = [
        SystemMessage(content=state.get("agent_config_prompt")),
        HumanMessage(content=user_input),
    ]
    response = model.invoke(messages)
    try:
        data: dict = json.loads(response.content)
        plan = data.get("plan", [])
        if not isinstance(plan, list):
            plan = []
        plan_finished = data.get("plan_finished", False)
        return {
            **state,
            "branch_name": data.get("branch_name", ""),
            "execution_plan": plan,
            "plan_finished": plan_finished,
        }
    except Exception:
        return {
            **state,
            "execution_plan": [
                {
                    "tool": "search_code",
                    "input": {"query": user_input},
                }
            ],
            "plan_finished": False,
        }


def executor_node(state: AgentState):
    plan = list(state.get("execution_plan") or [])
    if not plan:
        return {**state, "plan_finished": True}
    step = plan[0]
    remaining_plan = plan[1:]
    tool_name = step.get("tool")
    tool_input = step.get("input") or {}
    tool = TOOL_REGISTRY.get(tool_name)
    if tool is None:
        return state
    try:
        output = tool.invoke(tool_input)
    except Exception as e:
        output = f"tool execution error: {e!s}"
    return {**state, "execution_plan": remaining_plan, "last_tool_output": output}


def reflection_node(state: AgentState):
    plan = state.get("execution_plan") or []
    plan_finished = len(plan) == 0
    return {
        **state,
        "plan_finished": plan_finished,
    }
