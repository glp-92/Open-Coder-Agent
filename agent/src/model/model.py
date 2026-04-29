from config.config import config
from langchain_ollama import ChatOllama
from tools.registry import TOOLS_REGISTRY

base_model = ChatOllama(
    model=config.llm_model,
    temperature=0,
    num_ctx=config.model_num_ctx,
    base_url=config.ollama_url,
)

model = base_model.bind_tools(tools=TOOLS_REGISTRY)
summary_model = base_model
