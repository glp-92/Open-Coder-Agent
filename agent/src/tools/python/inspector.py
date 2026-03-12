import ast
import difflib
import os
from pathlib import Path

from langchain.tools import tool
from tools.utilities import IGNORE_DIRS, IGNORE_EXTENSIONS, REPOSITORY_ROOT_PATH, resolve_path


@tool
def get_repository_tree() -> str:
    """
    Obtain a directory tree from a root path.
    Some folders and extensions are ignored, by default and if agentignore file exists containing some files
    """
    agent_ignores = set()
    ignore_file: Path = REPOSITORY_ROOT_PATH / ".agentignore"
    if ignore_file.exists():
        with open(ignore_file) as f:
            agent_ignores = {line.strip() for line in f if line.strip() and not line.startswith("#")}

    def build_tree(current_path: Path, prefix: str = "") -> list[str]:
        lines = []
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
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{item.name}{'/' if item.is_dir() else ''}")
            if item.is_dir():
                new_prefix = prefix + ("    " if is_last else "│   ")
                lines.extend(build_tree(item, new_prefix))
        return lines

    if not REPOSITORY_ROOT_PATH.exists():
        return "Error: Root path not found"
    output = [f"{REPOSITORY_ROOT_PATH.name}/"]
    output.extend(build_tree(REPOSITORY_ROOT_PATH))
    return "\n".join(output)


@tool
def list_dir(path: str = ".") -> str:
    """
    Lists directory content (only files and folders)
    """
    absolute_path: str = str(resolve_path(file_path=path))
    try:
        items = os.listdir(str(absolute_path))
        return "\n".join(items)
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
def search_code(code_to_search: str, path: str = ".") -> str:
    """
    Finds specific code inside project
    """
    absolute_path: str = str(resolve_path(file_path=path))
    results = []
    for root, _, files in os.walk(absolute_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                with open(full_path) as f:
                    for i, line in enumerate(f.readlines()):
                        if code_to_search in line:
                            results.append(f"{full_path}:{i + 1}: {line.strip()}")
    return "\n".join(results[:50]) if results else "Error: results not found on search code"


@tool
def read_file(file_path: str) -> str:
    """
    Read the full content of a file inside the repository.

    The path must be relative to the repository root.
    """
    try:
        path = resolve_path(file_path)
        if not path.exists():
            return f"Error: {file_path} does not exist."
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading {file_path}: {e}"


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
