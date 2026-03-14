import sys

from cli.cli import run_cli
from config.config import config
from graph.state import AgentState
from graph.workflow import graph
from langchain_core.messages import HumanMessage, SystemMessage


def run(user_input: str) -> None:
    initial_state = AgentState(
        messages=[
            SystemMessage(content=config.agent_config_prompt),
            HumanMessage(content=user_input),
        ],
        steps=0,
        current_branch=None,
    )
    run_cli(user_input=user_input, graph=graph, initial_state=initial_state)


if __name__ == "__main__":
    user_input: str = sys.argv[1]
    run(user_input=user_input)
