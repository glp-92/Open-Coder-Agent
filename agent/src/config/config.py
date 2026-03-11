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
    repository_root_path: str
    agent_ignore_path: str


with open(Path(__file__).resolve().parent / "prompt.md") as file:
    prompt: str = file.read()

repository_root_path: str = os.environ.get("REPOSITORY_ROOT_PATH")
assert repository_root_path is not None, "REPOSITORY_ROOT_PATH environ not specified"
agent_ignore_path: str = os.path.join(repository_root_path, ".agentignore")
if not os.path.exists(agent_ignore_path):
    agent_ignore_path = "not found"

config = Config(
    ollama_url=os.environ.get("OLLAMA_URL", "http://localhost:11434"),
    llm_model=os.environ.get("MODEL_NAME", "qwen3.5:2b"),
    agent_config_prompt=prompt,
    max_steps=os.environ.get("AGENT_MAX_STEPS", 30),
    repository_root_path=repository_root_path,
    agent_ignore_path=agent_ignore_path,
)
