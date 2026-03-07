import ast
import difflib
import os

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
def list_files(path: str = ".") -> str:
    """
    list project file structure
    """
    tree = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        level = root.replace(path, "").count(os.sep)
        indent = " " * 4 * level
        tree.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = " " * 4 * (level + 1)
        for f in files:
            if any(f.endswith(ext) for ext in IGNORE_EXTENSIONS):
                continue
            tree.append(f"{sub_indent}{f}")
    return "\n".join(tree)


@tool
def get_function_signatures(file_path: str) -> str:
    """
    extracts classes, functions and arguments of .py.
    """
    with open(file_path) as f:
        node = ast.parse(f.read())
    signatures = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            args = [a.arg for a in item.args.args]
            signatures.append(f"Function: {item.name}({', '.join(args)})")

        elif isinstance(item, ast.ClassDef):
            signatures.append(f"Class: {item.name}")

            for sub in item.body:
                if isinstance(sub, ast.FunctionDef):
                    args = [a.arg for a in sub.args.args]
                    signatures.append(f"  Method: {sub.name}({', '.join(args)})")
    return "\n".join(signatures) if signatures else "no classes or functions found."


@tool
def get_imports(file_path: str) -> str:
    """
    imports from .py file
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
def read_symbol(file_path: str, symbol_name: str) -> str:
    """
    reads specific code from class or fn
    """
    with open(file_path) as f:
        source = f.read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == symbol_name:
            start = node.lineno - 1
            end = node.end_lineno
            lines = source.splitlines()
            return "\n".join(lines[start:end])
    return f"symbol {symbol_name} not found."


@tool
def search_code(query: str, path: str = ".") -> str:
    """
    finds specific code inside project
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
    read file content
    """
    with open(file_path) as f:
        return f.read()


@tool
def create_file(file_path: str, content: str) -> str:
    """
    creates new file
    """
    if os.path.exists(file_path):
        return f"error: {file_path} already exists."
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)
    return f"File {file_path} created successfully."


@tool
def replace_in_file(file_path: str, old: str, new: str) -> str:
    """
    replace code segment on a file
    """
    if not os.path.exists(file_path):
        return f"Error: {file_path} does not exist."
    with open(file_path) as f:
        content = f.read()
    if old not in content:
        return "error: text to replace not found"
    updated = content.replace(old, new, 1)
    with open(file_path, "w") as f:
        f.write(updated)
    return "text replace success"


@tool
def insert_in_file(file_path: str, anchor: str, content: str, position: str = "after") -> str:
    """
    insert content before or after an specific line
    position: 'before' o 'after'
    """
    if not os.path.exists(file_path):
        return f"Error: {file_path} does not exist."
    with open(file_path) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if anchor in line:
            if position == "before":
                lines.insert(i, content + "\n")
            else:
                lines.insert(i + 1, content + "\n")
            with open(file_path, "w") as f:
                f.writelines(lines)
            return "content inserted success"
    return "anchor not found."


@tool
def preview_patch(old: str, new: str) -> str:
    """
    shows diff before apply patch
    """
    diff = difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="")
    return "\n".join(diff)
