from langchain.tools import tool
from tools.utilities import REPOSITORY_ROOT_PATH, resolve_path, run_subprocess_from_root_path


@tool
def make_dirs(dir_list: list[str]) -> str:
    """
    Create a list of empty directories, useful when creating a project structure with no code on it
    """
    try:
        for dir in dir_list:
            _ = resolve_path(dir).mkdir(parents=True, exist_ok=True)
        return "Success: directories created successfully"
    except Exception as e:
        return f"Error: make dirs {e!s}"


@tool
def create_file(file_path: str, content: str) -> str:
    """
    Create a new file with the provided content. Creates folder if there are not route to file

    The file will not be overwritten if it already exists.
    """
    try:
        path = resolve_path(file_path)
        if path.exists():
            return f"Error: {file_path} already exists. Use write_file only after reading it first."
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Success: created new file {file_path}"
    except Exception as e:
        return f"Error: writing file {file_path}: {e!s}"


@tool
def write_file(file_path: str, content: str) -> str:
    """
    Write a full file inside the repository.

    The path must be relative to the repository root.
    If the file exists it will be overwritten, and function will notice it.
    Missing directories will be created automatically.
    """
    try:
        path = resolve_path(file_path)
        if path.exists():
            path.write_text(content, encoding="utf-8")
            return f"Success: wrote existing file {file_path}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Success: wrote new file {file_path}"
    except Exception as e:
        return f"Error: writing code on {file_path}: {e}"


@tool
def run_linting(paths: list[str] | None = None) -> str:
    """
    Run project formatting and linting.

    Executes:
    - isort
    - ruff format
    - ruff check --fix

    Returns combined output.
    """
    normalized_paths = paths or ["."]
    resolved_targets = [resolve_path(path) for path in normalized_paths]
    lint_targets = [str(target.relative_to(REPOSITORY_ROOT_PATH)) for target in resolved_targets]
    python_targets = [
        str(target.relative_to(REPOSITORY_ROOT_PATH))
        for target in resolved_targets
        if target.is_dir() or target.suffix == ".py"
    ]

    cmds_args: list[list[str]] = [["ruff", "check", *lint_targets, "--fix"], ["ruff", "format", *lint_targets]]
    if python_targets:
        cmds_args.insert(0, ["isort", *python_targets])

    outputs = []
    try:
        for cmd_args in cmds_args:
            result: str = run_subprocess_from_root_path(args=cmd_args)
            outputs.append(f"$ {result}")
        return "\n".join(outputs)
    except Exception as e:
        return f"Error running linting: {e}"
