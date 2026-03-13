import sys

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
        steps=0,
        current_branch=None,
    )
    logger.info(f"\n🚀 {'RUNNING AGENT':^50}\n" + "=" * 52)
    logger.info(
        f"Model {config.llm_model}, Ollama Server {config.ollama_url}, repository root {config.repository_root_path}"
    )
    for event in graph.stream(initial_state, stream_mode="updates"):
        for node_name, state_update in event.items():
            logger.info(f"\n>>> Node: {node_name}")
            if "messages" in state_update:
                last_message = state_update["messages"][-1]
                if last_message.type == "ai":
                    if last_message.content:
                        logger.info(f"🤖 AI Thinking:\n{last_message.content}")
                    if last_message.tool_calls:
                        for tool in last_message.tool_calls:
                            logger.info(f"🛠️  AI Calling: {tool['name']}({tool['args']})")
                elif last_message.type == "tool":
                    logger.info(f"Result [{last_message.name}]:\n{last_message.content}")
    logger.info("\n" + "=" * 52 + f"\n✅ {'TASK FINISHED':^50}\n")


if __name__ == "__main__":
    user_input: str = sys.argv[1]
    run(user_input=user_input)
