from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from tools.git import git_commit, git_status, git_switch

model = ChatOllama(model="qwen3", temperature=1)
tools = [git_commit, git_status, git_switch]
agent = create_agent(model=model, tools=tools)
