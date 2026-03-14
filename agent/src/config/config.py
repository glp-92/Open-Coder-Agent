import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent.parent / ".env")


@dataclass
class Config:
    ollama_url: str
    llm_model: str
    agent_config_prompt: str
    max_steps: int
    max_messages_for_summary: int
    max_chat_history: int
    repository_root_path: str


with open(Path(__file__).resolve().parent / "prompt.md") as file:
    prompt: str = file.read()

repository_root_path: str = os.environ.get("REPOSITORY_ROOT_PATH")
assert repository_root_path is not None, "REPOSITORY_ROOT_PATH environ not specified"

config = Config(
    ollama_url=os.environ.get("OLLAMA_URL", "http://localhost:11434"),
    llm_model=os.environ.get("MODEL_NAME", "qwen3.5:2b"),
    agent_config_prompt=prompt,
    max_steps=os.environ.get("AGENT_MAX_STEPS", 30),
    max_messages_for_summary=os.environ.get("AGENT_MAX_MESSAGES_FOR_SUMMARY", 5),
    max_chat_history=os.environ.get("AGENT_MAX_CHAT_HISTORY", 8),
    repository_root_path=repository_root_path,
)
