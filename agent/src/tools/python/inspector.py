import ast
import difflib
import os
from pathlib import Path

from langchain.tools import tool

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
}

IGNORE_EXTENSIONS: set = {
    ".pyc",
    ".pyo",
    ".log",
    ".lock",
}


@tool
def get_project_tree(root: str = ".", agent_ignore_path: str | None = None) -> str:
    """
    Obtain a directory tree from a root path.
    Some folders and extensions are ignored, by default and if agentignore file exists containing some files
    """
    root_path = Path(root)
    agent_ignores = set()
    if agent_ignore_path:
        ignore_file = root_path / agent_ignore_path
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

    if not root_path.exists():
        return "Error: Root path not found"
    output = [f"{root_path.name}/"]
    output.extend(build_tree(root_path))
    return "\n".join(output)


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

    try:
        with open(file_path, encoding="utf-8") as f:
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
    return "\n".join(output) if output else "No definitions found."


@tool
def get_imports(file_path: str) -> str:
    """
    Extracts imports from .py file
    """
    with open(file_path) as f:
        tree = ast.parse(f.read())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    return "\n".join(imports)


@tool
def search_code(query: str, path: str = ".") -> str:
    """
    Finds specific code inside project
    """
    results = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                with open(full_path) as f:
                    for i, line in enumerate(f.readlines()):
                        if query in line:
                            results.append(f"{full_path}:{i + 1}: {line.strip()}")
    return "\n".join(results[:50]) if results else "results not found on search code"


@tool
def read_file(file_path: str) -> str:
    """
    Read full file content
    """
    with open(file_path) as f:
        return f.read()


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
