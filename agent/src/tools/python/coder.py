from langchain.tools import tool
from tools.utilities import resolve_path, run_subprocess_from_root_path


@tool
def create_file(file_path: str, content: str) -> str:
    """
    Create a new file with the provided content. Creates folder if there are not route to file

    The file will not be overwritten if it already exists.
    """
    try:
        path = resolve_path(file_path)
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
        path = resolve_path(file_path)
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
    cmds_args: list[str] = [
        ["isort", "."],
        ["ruff", "format", "."],
        ["ruff", "check", ".", "--fix"],
    ]
    outputs = []
    try:
        for cmd_args in cmds_args:
            result: str = run_subprocess_from_root_path(args=cmd_args)
            outputs.append(f"$ {result}")
        return "\n".join(outputs)
    except Exception as e:
        return f"Error running linting: {e}"
