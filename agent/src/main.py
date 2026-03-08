from pprint import pprint

from config.config import config
from graph.state import AgentState
from graph.workflow import graph
from langchain_core.messages import HumanMessage, SystemMessage


def run(user_input: str) -> None:
    initial_state: AgentState = AgentState(
        messages=[
            SystemMessage(content=config.agent_config_prompt),
            HumanMessage(content=user_input),
        ],
        steps=0,
    )
    for event in graph.stream(initial_state, stream_mode="updates"):
        pprint(event)  # noqa: T203


if __name__ == "__main__":
    run("git tools on tools folder must log some steps")
