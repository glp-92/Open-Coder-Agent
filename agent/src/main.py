from config.config import config
from graph.nodes import AgentState
from graph.state_graph import build_coder_agent_graph
from langchain_ollama import ChatOllama
from loguru import logger


def run(user_input: str):
    model = ChatOllama(model=config.llm_model, temperature=0)
    agent_graph = build_coder_agent_graph(model=model)
    state: AgentState = {
        "user_input": user_input,
        "agent_config_prompt": config.agent_config_prompt,
        "branch_name": "",
        "root_project_path": ".",
        "project_tree": None,
        "file_content": {},
        "file_symbols": {},
        "target_files": [],
        "last_search": None,
        "last_diff": None,
        "execution_plan": [],
        "plan_finished": False,
    }
    for event in agent_graph.stream(state, stream_mode="updates"):
        logger.info(event)


if __name__ == "__main__":
    run("git tools on tools folder must log some steps")
