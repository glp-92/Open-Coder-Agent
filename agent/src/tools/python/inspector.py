import ast
import difflib
import fnmatch
import os
from pathlib import Path

from langchain.tools import tool
from tools.utilities import (
    IGNORE_DIRS,
    IGNORE_EXTENSIONS,
    REPOSITORY_ROOT_PATH,
    resolve_path,
    to_repository_relative_path,
)

MAX_TREE_DEPTH = 2
MAX_TREE_ENTRIES = 200
MAX_LIST_DIR_ITEMS = 200
MAX_SEARCH_RESULTS = 20
MAX_READ_LINES = 200
MAX_FIND_RESULTS = 100
SEARCHABLE_EXTENSIONS = {".py", ".md", ".txt", ".toml", ".json", ".yml", ".yaml", ".ini", ".env"}


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts) or path.suffix in IGNORE_EXTENSIONS


def _is_searchable_text_file(path: Path) -> bool:
    return path.suffix in SEARCHABLE_EXTENSIONS or path.name in {"Dockerfile", ".env", ".env.example"}


@tool
def get_repository_tree(path: str = ".", max_depth: int = MAX_TREE_DEPTH) -> str:
    """
    Obtain a limited directory tree from a root path.
    Some folders and extensions are ignored, by default and if agentignore file exists containing some files.
    """
    agent_ignores = set()
    ignore_file: Path = REPOSITORY_ROOT_PATH / ".agentignore"
    if ignore_file.exists():
        with open(ignore_file) as f:
            agent_ignores = {line.strip() for line in f if line.strip() and not line.startswith("#")}

    root_path = resolve_path(path)
    emitted_entries = 0

    def build_tree(current_path: Path, prefix: str = "", depth: int = 0) -> list[str]:
        nonlocal emitted_entries
        lines = []
        if depth >= max_depth:
            return lines
        try:
            items = [
                it
                for it in current_path.iterdir()
                if it.name not in agent_ignores
                and it.name not in IGNORE_DIRS
                and not (it.is_file() and it.suffix in IGNORE_EXTENSIONS)
            ]
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return [f"{prefix}└── [Access Denied]"]
        for i, item in enumerate(items):
            if emitted_entries >= MAX_TREE_ENTRIES:
                lines.append(f"{prefix}└── ... truncated after {MAX_TREE_ENTRIES} entries")
                break
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{item.name}{'/' if item.is_dir() else ''}")
            emitted_entries += 1
            if item.is_dir():
                new_prefix = prefix + ("    " if is_last else "│   ")
                lines.extend(build_tree(item, new_prefix, depth + 1))
        return lines

    if not root_path.exists():
        return "Error: Root path not found"
    output = [f"{to_repository_relative_path(root_path) or REPOSITORY_ROOT_PATH.name}/"]
    tree: list[str] = build_tree(root_path)
    if not tree:
        return "Warning: Empty repository"
    output.extend(tree)
    return "\n".join(output)


@tool
def list_dir(path: str = ".", max_items: int = MAX_LIST_DIR_ITEMS) -> str:
    """
    Lists directory content (only files and folders) with bounded output.
    """
    absolute_path: str = str(resolve_path(file_path=path))
    try:
        items = sorted(os.listdir(str(absolute_path)))
        clipped_items = items[:max_items]
        rendered_items = []
        for item in clipped_items:
            full_path = Path(absolute_path) / item
            rendered_items.append(f"{item}/" if full_path.is_dir() else item)
        if len(items) > max_items:
            rendered_items.append(f"... truncated after {max_items} items")
        return "\n".join(rendered_items) if rendered_items else "Warning: Empty directory"
    except Exception as e:
        return f"Error: directory listing: {e}"


@tool
def get_enhanced_signatures_from_module(file_path: str) -> str:
    """
    Extracts high-level signatures: Classes (inheritance, attributes),
    Methods, and Functions with types.
    """

    def get_type_name(node):
        return ast.unparse(node) if node else "Any"

    def get_summary_doc(node):
        doc = ast.get_docstring(node)
        if doc:
            return f" # {doc.splitlines()[0]}"
        return ""

    absolute_path: str = str(resolve_path(file_path=file_path))
    try:
        with open(absolute_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        return f"Error: {e}"
    output = []
    for item in tree.body:
        if isinstance(item, ast.FunctionDef):
            args = [f"{a.arg}: {get_type_name(a.annotation)}" for a in item.args.args]
            ret = get_type_name(item.returns)
            output.append(f"def {item.name}({', '.join(args)}) -> {ret}{get_summary_doc(item)}")
        elif isinstance(item, ast.ClassDef):
            bases = [ast.unparse(b) for b in item.bases]
            base_str = f"({', '.join(bases)})" if bases else ""
            output.append(f"class {item.name}{base_str}:{get_summary_doc(item)}")
            for sub in item.body:
                if isinstance(sub, ast.AnnAssign) and isinstance(sub.target, ast.Name):
                    output.append(f"  {sub.target.id}: {get_type_name(sub.annotation)}")
                elif isinstance(sub, ast.FunctionDef):
                    m_args = [f"{a.arg}: {get_type_name(a.annotation)}" for a in sub.args.args]
                    m_ret = get_type_name(sub.returns)
                    output.append(f"  def {sub.name}({', '.join(m_args)}) -> {m_ret}{get_summary_doc(sub)}")
    return "\n".join(output) if output else "Error: No definitions found."


@tool
def get_imports(file_path: str) -> str:
    """
    Extracts imports from .py file
    """
    absolute_path: str = str(resolve_path(file_path=file_path))
    try:
        with open(absolute_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.append(n.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        return "\n".join(imports) if imports else "No imports found."
    except Exception as e:
        return f"Error: Could not read imports from {absolute_path}: {e}"


@tool
def search_code(code_to_search: str, path: str = ".", max_results: int = MAX_SEARCH_RESULTS) -> str:
    """
    Finds a specific substring inside repository text files.
    """
    root_path = resolve_path(file_path=path)
    if max_results <= 0:
        return "Error: max_results must be greater than 0"
    results = []
    for root, dir_names, files in os.walk(root_path):
        dir_names[:] = [dir_name for dir_name in sorted(dir_names) if dir_name not in IGNORE_DIRS]
        for file_name in sorted(files):
            full_path = Path(root) / file_name
            if _is_ignored(full_path) or not _is_searchable_text_file(full_path):
                continue
            try:
                with open(full_path, encoding="utf-8") as f:
                    for index, line in enumerate(f, start=1):
                        if code_to_search in line:
                            relative_path = to_repository_relative_path(full_path)
                            results.append(f"{relative_path}:{index}: {line.strip()[:200]}")
                            if len(results) >= max_results:
                                return "\n".join(results)
            except UnicodeDecodeError:
                continue
            except OSError as e:
                results.append(f"Warning: could not read {to_repository_relative_path(full_path)}: {e}")
                if len(results) >= max_results:
                    return "\n".join(results)
    return "\n".join(results) if results else "Error: results not found on search code"


@tool
def find_files(file_glob: str, path: str = ".", max_results: int = MAX_FIND_RESULTS) -> str:
    """
    Find files matching a glob pattern with bounded output.
    """
    if not file_glob.strip():
        return "Error: file_glob cannot be empty"
    if max_results <= 0:
        return "Error: max_results must be greater than 0"

    root_path = resolve_path(file_path=path)
    matched: list[str] = []
    for root, dir_names, files in os.walk(root_path):
        dir_names[:] = [dir_name for dir_name in sorted(dir_names) if dir_name not in IGNORE_DIRS]
        for file_name in sorted(files):
            full_path = Path(root) / file_name
            if _is_ignored(full_path):
                continue
            relative_path = to_repository_relative_path(full_path)
            if fnmatch.fnmatch(relative_path, file_glob) or fnmatch.fnmatch(file_name, file_glob):
                matched.append(relative_path)
                if len(matched) >= max_results:
                    return "\n".join(matched) + f"\n... truncated after {max_results} results"

    return "\n".join(matched) if matched else "Error: no files matched pattern"


@tool
def read_file(file_path: str, start_line: int = 1, end_line: int = MAX_READ_LINES) -> str:
    """
    Read a bounded line range from a file inside the repository.

    The path must be relative to the repository root.
    """
    try:
        path = resolve_path(file_path)
        if not path.exists():
            return f"Error: {file_path} does not exist."
        if start_line < 1 or end_line < start_line:
            return "Error: invalid line range"

        bounded_end_line = min(end_line, start_line + MAX_READ_LINES - 1)
        lines = path.read_text(encoding="utf-8").splitlines()
        if start_line > len(lines):
            return f"Error: {file_path} has only {len(lines)} lines."

        selected_lines = lines[start_line - 1 : bounded_end_line]
        numbered_lines = [
            f"{line_number}: {line_content}"
            for line_number, line_content in enumerate(selected_lines, start=start_line)
        ]

        trailer = ""
        if bounded_end_line < len(lines):
            trailer = f"\n... truncated at line {bounded_end_line}. Read another range if needed."

        return (
            f"File: {to_repository_relative_path(path)}\n"
            f"Lines: {start_line}-{bounded_end_line} of {len(lines)}\n" + "\n".join(numbered_lines) + trailer
        )
    except Exception as e:
        return f"Error reading {file_path}: {e}"


@tool
def file_stats(file_path: str) -> str:
    """
    Return lightweight stats for a single file.
    """
    try:
        path = resolve_path(file_path)
        if not path.exists() or not path.is_file():
            return f"Error: {file_path} does not exist or is not a file."

        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()
        non_empty_lines = sum(1 for line in lines if line.strip())
        return (
            f"File: {to_repository_relative_path(path)}\n"
            f"Size bytes: {path.stat().st_size}\n"
            f"Total lines: {len(lines)}\n"
            f"Non-empty lines: {non_empty_lines}"
        )
    except UnicodeDecodeError:
        return f"Error: {file_path} is not a UTF-8 text file"
    except Exception as e:
        return f"Error: file stats {e}"


@tool
def preview_patch(old: str, new: str) -> str:
    """
    Show unified diff between old and new code.
    """
    diff = difflib.unified_diff(
        old.splitlines(),
        new.splitlines(),
        fromfile="before",
        tofile="after",
        lineterm="",
    )
    return "\n".join(diff)
