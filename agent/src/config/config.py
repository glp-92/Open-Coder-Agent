import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent.parent / ".env")


def _first_env(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value is not None:
            return value
    return default


class Config(BaseModel):
    ollama_url: str = Field(default="http://localhost:11434")
    llm_model: str = Field(default="qwen3.5:2b")
    model_num_ctx: int = Field(default=4096, gt=0)
    agent_config_prompt: str
    max_steps: int = Field(default=20, gt=0)
    max_messages_for_summary: int = Field(default=10, gt=0)
    messages_to_summarize: int = Field(default=4, gt=0)
    chat_window_size: int = Field(default=6, ge=4)
    repository_root_path: str = Field(min_length=1)

    @field_validator("repository_root_path")
    @classmethod
    def _validate_repository_root_path(cls, value: str) -> str:
        root = Path(value).expanduser().resolve()
        if not root.is_absolute():
            raise ValueError("repository_root_path must be an absolute path")
        if not root.exists() or not root.is_dir():
            raise ValueError("repository_root_path must exist and be a directory")
        return str(root)

    @model_validator(mode="after")
    def _validate_message_windows(self):
        if self.max_messages_for_summary < self.messages_to_summarize:
            raise ValueError("max_messages_for_summary must be >= messages_to_summarize")
        if self.chat_window_size > self.max_messages_for_summary:
            raise ValueError("chat_window_size must be <= max_messages_for_summary")
        return self


with open(Path(__file__).resolve().parent / "prompt.md", encoding="utf-8") as file:
    prompt: str = file.read()

config = Config(
    ollama_url=_first_env("OLLAMA_URL", default="http://localhost:11434"),
    llm_model=_first_env("MODEL_NAME", default="qwen3.5:2b"),
    model_num_ctx=_first_env("AGENT_MODEL_NUM_CTX", "MODEL_NUM_CTX", default="4096"),
    agent_config_prompt=prompt,
    max_steps=_first_env("AGENT_MAX_STEPS", "MAX_STEPS", default="20"),
    max_messages_for_summary=_first_env("AGENT_MAX_MESSAGES_FOR_SUMMARY", default="10"),
    messages_to_summarize=_first_env("AGENT_MESSAGES_TO_SUMMARIZE", default="4"),
    chat_window_size=_first_env("AGENT_CHAT_WINDOW_SIZE", default="6"),
    repository_root_path=_first_env("REPOSITORY_ROOT_PATH") or "",
)
