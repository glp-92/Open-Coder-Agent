from pathlib import Path

from config.config import config

IGNORE_DIRS: set = {
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".idea",
    ".vscode",
    "ollama-server",
    "ollama-data",
    "data",
    "db-data",
}
IGNORE_EXTENSIONS: set = {
    ".pyc",
    ".pyo",
    ".log",
    ".lock",
}
REPOSITORY_ROOT_PATH: Path = Path(config.repository_root_path)


def _resolve_path(file_path: str) -> Path:
    path: Path = (REPOSITORY_ROOT_PATH / file_path).resolve()
    if not str(path).startswith(str(REPOSITORY_ROOT_PATH)):
        raise ValueError("Error: file path provide does not match repository root")
    return path
