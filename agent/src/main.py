from config.config import config
from graph.state import AgentState
from graph.workflow import graph
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger


def run(user_input: str) -> None:
    initial_state: AgentState = AgentState(
        messages=[
            SystemMessage(content=config.agent_config_prompt),
            HumanMessage(content=user_input),
        ],
    )
    for event in graph.stream(initial_state, stream_mode="updates"):
        if "messages" in event:
            msg = event["messages"][-1]
            logger.info(f"{msg.type}: {msg.content}")


if __name__ == "__main__":
    run("git tools on tools folder must log some steps")
