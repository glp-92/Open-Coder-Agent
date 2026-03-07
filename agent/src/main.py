from config.config import config
from langchain.agents import create_agent
from langchain.messages import SystemMessage
from langchain_ollama import ChatOllama
from loguru import logger
from middlewares.tool_error_handler import tool_error_handler
from tools.git import git_commit, git_status, git_switch
from tools.inspector import (
    create_file,
    get_function_signatures,
    get_imports,
    insert_in_file,
    list_files,
    preview_patch,
    read_file,
    read_symbol,
    replace_in_file,
    search_code,
)

model = ChatOllama(model=config.llm_model, temperature=0)
tools = [
    git_commit,
    git_status,
    git_switch,
    create_file,
    get_function_signatures,
    get_imports,
    insert_in_file,
    list_files,
    preview_patch,
    read_file,
    read_symbol,
    replace_in_file,
    search_code,
]
agent = create_agent(
    model=model,
    name="coding_assistant",
    tools=tools,
    middleware=[tool_error_handler],
    system_prompt=SystemMessage(content=config.agent_config_prompt),
)

if __name__ == "__main__":
    result = agent.invoke({"messages": [{"role": "user", "content": "add logging to api"}]})
    logger.info(result["messages"][-1].content)
