import subprocess
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
    ".ruff_cache",
}
IGNORE_EXTENSIONS: set = {
    ".pyc",
    ".pyo",
    ".log",
    ".lock",
}
REPOSITORY_ROOT_PATH: Path = Path(config.repository_root_path)


def _normalize_repo_relative_input(file_path: str) -> str:
    candidate = file_path.strip().replace("\\", "/")
    if candidate in {"", ".", "./"}:
        return "."
    # UX: treat '/src/..' as path relative to repository root, not filesystem root.
    return candidate[1:] if candidate.startswith("/") else candidate


def resolve_path(file_path: str) -> Path:
    root: Path = REPOSITORY_ROOT_PATH.resolve()
    relative_input = _normalize_repo_relative_input(file_path)
    path: Path = (root / relative_input).expanduser().resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError("Error: file path does not match repository root") from exc
    return path


def to_repository_relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPOSITORY_ROOT_PATH).as_posix()
    except ValueError:
        return path.as_posix()


def run_subprocess_from_root_path(args: list[str]) -> str:
    """
    Function to run git commands on a safe way
    """
    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True, cwd=REPOSITORY_ROOT_PATH)
        return result.stdout.strip() or f"Success: {' '.join(args)}"
    except subprocess.CalledProcessError as e:
        return f"Error ejecutando {' '.join(args)}: {e.stderr}"
