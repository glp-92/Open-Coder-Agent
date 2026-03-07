from config.config import config
from config.logger import log_agent_event
from langchain.agents import create_agent
from langchain.messages import SystemMessage
from langchain_ollama import ChatOllama
from middlewares.tool_error_handler import tool_error_handler
from tools.registry import TOOLS_REGISTRY

model = ChatOllama(model=config.llm_model, temperature=0)
agent = create_agent(
    model=model,
    name="coding_assistant",
    tools=TOOLS_REGISTRY,
    middleware=[tool_error_handler],
    system_prompt=SystemMessage(content=config.agent_config_prompt),
)

if __name__ == "__main__":
    for event in agent.stream(
        {"messages": [{"role": "user", "content": "add logging with loguru library to git tools"}]}
    ):
        log_agent_event(event)
