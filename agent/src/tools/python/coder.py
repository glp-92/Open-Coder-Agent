from langchain.tools import tool
from tools.utilities import REPOSITORY_ROOT_PATH, resolve_path, run_subprocess_from_root_path

MAX_WRITE_CHARS = 200_000
PROTECTED_RELATIVE_PATHS = {".env", ".env.example"}
PROTECTED_PREFIXES = (".git/",)


def _is_protected_path(path: str) -> bool:
    normalized = path.strip().replace("\\", "/").lstrip("./")
    return normalized in PROTECTED_RELATIVE_PATHS or normalized.startswith(PROTECTED_PREFIXES)


def _normalize_lint_paths(paths: object | None) -> list[str]:
    if paths is None:
        return []
    if isinstance(paths, str):
        candidate = paths.strip()
        return [candidate] if candidate else []
    if isinstance(paths, (list, tuple, set)):
        return [str(path).strip() for path in paths if str(path).strip()]
    if isinstance(paths, dict):
        # Common model mistake: paths={} or paths={"paths": [...]}
        if not paths:
            return []
        nested = paths.get("paths")
        if isinstance(nested, str):
            return [nested.strip()] if nested.strip() else []
        if isinstance(nested, (list, tuple, set)):
            return [str(path).strip() for path in nested if str(path).strip()]
        single = paths.get("path")
        if isinstance(single, str):
            return [single.strip()] if single.strip() else []
        return []
    return []


@tool
def make_dirs(dir_list: list[str]) -> str:
    """
    Create a list of empty directories, useful when creating a project structure with no code on it
    """
    try:
        for dir in dir_list:
            if _is_protected_path(dir):
                return f"Error: creating protected directory is not allowed: {dir}"
            _ = resolve_path(dir).mkdir(parents=True, exist_ok=True)
        return "Success: directories created successfully"
    except Exception as e:
        return f"Error: make dirs {e!s}"


@tool
def make_dir(dir_path: str) -> str:
    """
    Create a single directory.
    """
    if not dir_path.strip():
        return "Error: dir_path cannot be empty"
    return make_dirs([dir_path])


@tool
def create_file(file_path: str, content: str) -> str:
    """
    Create a new file with the provided content. Creates folder if there are not route to file

    The file will not be overwritten if it already exists.
    """
    try:
        if _is_protected_path(file_path):
            return f"Error: writing protected file is not allowed: {file_path}"
        if len(content) > MAX_WRITE_CHARS:
            return f"Error: content too large ({len(content)} chars). Limit is {MAX_WRITE_CHARS}."
        path = resolve_path(file_path)
        if path.exists():
            return f"Error: {file_path} already exists. Use write_file only after reading it first."
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Success: created new file {file_path}"
    except Exception as e:
        return f"Error: writing file {file_path}: {e!s}"


@tool
def write_file(file_path: str, content: str, allow_overwrite: bool = False) -> str:
    """
    Write a full file inside the repository.

    The path must be relative to the repository root.
    If the file exists it will be overwritten, and function will notice it.
    Missing directories will be created automatically.
    """
    try:
        if _is_protected_path(file_path):
            return f"Error: writing protected file is not allowed: {file_path}"
        if len(content) > MAX_WRITE_CHARS:
            return f"Error: content too large ({len(content)} chars). Limit is {MAX_WRITE_CHARS}."
        path = resolve_path(file_path)
        if path.exists():
            if not allow_overwrite:
                return (
                    f"Error: {file_path} already exists. "
                    "Set allow_overwrite=true only after read_file and explicit confirmation."
                )
            path.write_text(content, encoding="utf-8")
            return f"Success: wrote existing file {file_path}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Success: wrote new file {file_path}"
    except Exception as e:
        return f"Error: writing code on {file_path}: {e}"


@tool
def run_linting(paths: object | None = None) -> str:
    """
    Run project formatting and linting.

    Executes:
    - isort
    - ruff format
    - ruff check --fix

    Returns combined output.
    """
    normalized_paths = _normalize_lint_paths(paths)
    if not normalized_paths:
        return "Error: run_linting requires explicit non-empty paths of files or folders touched."
    if any(path in {".", "./"} for path in normalized_paths):
        return "Error: run_linting does not allow '.'; provide only specific touched paths."

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
