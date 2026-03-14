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
    messages_to_summarize: int
    chat_window_size: int
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
    max_messages_for_summary=os.environ.get("AGENT_MAX_MESSAGES_FOR_SUMMARY", 12),
    messages_to_summarize=os.environ.get("AGENT_MESSAGES_TO_SUMMARIZE", 6),
    chat_window_size=os.environ.get("AGENT_CHAT_WINDOW_SIZE", 8),
    repository_root_path=repository_root_path,
)

assert config.max_messages_for_summary >= config.messages_to_summarize, (
    f"Error: 'max_messages_for_summary' ({config.max_messages_for_summary}) must be higher or equal "
    f"to 'messages_to_summarize' ({config.messages_to_summarize})."
)
assert config.chat_window_size >= 4, "Error: 'chat_window_size' too small. Minimum amount of 4 to keep context healthy"
assert config.chat_window_size <= config.max_messages_for_summary, (
    f"Error: 'chat_window_size' ({config.chat_window_size}) should not be higher than "
    f"'max_messages_for_summary' ({config.max_messages_for_summary}), "
    "or summary will be lost before being useful."
)
assert all(
    v > 0
    for v in [config.max_steps, config.max_messages_for_summary, config.messages_to_summarize, config.chat_window_size]
), "Error: All params should be greater than 0."
