import subprocess
from pathlib import Path

from langchain.tools import tool
from tools.utilities import REPOSITORY_ROOT_PATH, _resolve_path


@tool
def create_file(file_path: str, content: str) -> str:
    """
    Create a new file with the provided content. Creates folder if there are not route to file

    The file will not be overwritten if it already exists.
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Success: file write on: {file_path}"
    except Exception as e:
        return f"Error: writing file {file_path}: {e!s}"


@tool
def write_file(file_path: str, content: str) -> str:
    """
    Write a full file inside the repository.

    The path must be relative to the repository root.
    If the file exists it will be overwritten.
    Missing directories will be created automatically.
    """
    try:
        path = _resolve_path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Success: wrote file {file_path}"
    except Exception as e:
        return f"Error: writing code on {file_path}: {e}"


@tool
def run_linting() -> str:
    """
    Run project formatting and linting.

    Executes:
    - isort
    - ruff format
    - ruff check --fix

    Returns combined output.
    """
    commands = [
        ["isort", "."],
        ["ruff", "format", "."],
        ["ruff", "check", ".", "--fix"],
    ]
    outputs = []
    try:
        for cmd in commands:
            result = subprocess.run(
                cmd,
                cwd=REPOSITORY_ROOT_PATH,
                capture_output=True,
                text=True,
            )
            outputs.append(f"$ {' '.join(cmd)}\n{result.stdout}\n{result.stderr}")
        return "\n".join(outputs) or "Success: Linting completed."
    except Exception as e:
        return f"Error running linting: {e}"
