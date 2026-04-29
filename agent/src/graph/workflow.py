from graph.nodes import explorer_node, memory_manager_node, router_logic, tool_node
from graph.state import AgentState
from langgraph.graph import END, StateGraph

workflow = StateGraph(AgentState)
workflow.add_node("explorer", explorer_node)
workflow.add_node("tool_executor", tool_node)
workflow.add_node("memory_manager", memory_manager_node)
workflow.set_entry_point("explorer")
workflow.add_conditional_edges(
    "explorer", router_logic, {"tool_executor": "tool_executor", "retry": "explorer", "end": END}
)
workflow.add_edge("tool_executor", "memory_manager")
workflow.add_edge("memory_manager", "explorer")
graph = workflow.compile()
