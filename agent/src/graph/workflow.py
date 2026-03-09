from graph.nodes import explorer_node, router_logic, tool_node
from graph.state import AgentState
from langgraph.graph import END, StateGraph

workflow = StateGraph(AgentState)
workflow.add_node("explorer", explorer_node)
workflow.add_node("tool_executor", tool_node)
workflow.set_entry_point("explorer")
workflow.add_conditional_edges("explorer", router_logic, {"tool_executor": "tool_executor", "end": END})
workflow.add_edge("tool_executor", "explorer")
graph = workflow.compile()
