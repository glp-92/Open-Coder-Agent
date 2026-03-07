"""
START
  ├─ Git Setup (create_branch)
  ├─ Project Scan
  │    ├─ list_files
  │    ├─ read_needed_files
  │    ├─ extract_symbols
  ├─ Code Search / Analysis
  │    ├─ search_code
  │    ├─ get_imports
  │    └─ read_symbol
  ├─ Edit / Patch Stage
  │    ├─ create_file
  │    ├─ insert_in_file
  │    ├─ replace_in_file
  │    └─ preview_patch
  ├─ Commit Changes
  │    ├─ git_status
  │    └─ git_commit
END
"""

import graph.nodes
from langgraph.graph import END, START, StateGraph


def build_coder_agent_graph(model):
    _graph = StateGraph(graph.nodes.AgentState)
    _graph.add_node("planner", lambda s: graph.nodes.planner_node(s, model))
    _graph.add_node("executor", graph.nodes.executor_node)
    _graph.add_node("reflection", lambda s: graph.nodes.reflection_node(s))
    _graph.add_edge(START, "planner")
    _graph.add_edge("planner", "executor")
    _graph.add_edge("executor", "reflection")
    _graph.add_conditional_edges("reflection", lambda s: END if s.get("plan_finished", True) else "executor")
    return _graph.compile()
