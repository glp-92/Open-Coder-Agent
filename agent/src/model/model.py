from config.config import config
from langchain_ollama import ChatOllama
from tools.registry import TOOLS_REGISTRY

model = ChatOllama(model=config.llm_model, temperature=0).bind_tools(tools=TOOLS_REGISTRY)
