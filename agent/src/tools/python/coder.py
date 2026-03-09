import os

from langchain.tools import tool


@tool
def create_file(file_path: str, content: str) -> str:
    """
    Create a new file with the provided content.

    The file will not be overwritten if it already exists.
    """
    if os.path.exists(file_path):
        return f"error: {file_path} already exists"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content.strip() + "\n")
    return f"file {file_path} created successfully"


@tool
def add_import(file_path: str, import_line: str) -> str:
    """
    Add a Python import if it does not already exist.

    The import will be placed with the other imports at the top of the file.
    """
    if not os.path.exists(file_path):
        return f"Error: {file_path} does not exist."
    with open(file_path) as f:
        lines = f.readlines()
    if any(import_line.strip() == line.strip() for line in lines):
        return "import already exists"
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1
    lines.insert(insert_at, import_line.strip() + "\n")
    with open(file_path, "w") as f:
        f.writelines(lines)
    return "import added successfully"


@tool
def replace_code_block(file_path: str, old_block: str, new_block: str) -> str:
    """
    Replace a block of code in a file.

    The old_block must match the exact code returned by read_file.
    This is safer than partial string replacements.
    """
    if not os.path.exists(file_path):
        return f"Error: {file_path} does not exist."
    with open(file_path) as f:
        content = f.read()
    if old_block not in content:
        return "error: old block not found"
    updated = content.replace(old_block, new_block, 1)
    with open(file_path, "w") as f:
        f.write(updated)
    return "code block replaced successfully"


@tool
def insert_after_line(file_path: str, anchor: str, content: str) -> str:
    """
    Insert code after a line containing 'anchor'.

    The inserted content will automatically inherit the indentation
    of the anchor line to avoid syntax errors.
    """

    def _get_indent(line: str) -> str:
        return line[: len(line) - len(line.lstrip())]

    if not os.path.exists(file_path):
        return f"Error: {file_path} does not exist."
    with open(file_path) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if anchor in line:
            indent = _get_indent(line)
            adjusted = "\n".join(indent + line if line.strip() else line for line in content.splitlines()) + "\n"
            lines.insert(i + 1, adjusted)
            with open(file_path, "w") as f:
                f.writelines(lines)
            return "content insertion success"
    return "anchor not found for content insert after line"


@tool
def append_to_file(file_path: str, content: str) -> str:
    """
    Append content at the end of a file.

    Useful for adding new functions, classes, or code blocks without
    modifying existing code.
    """
    if not os.path.exists(file_path):
        return f"Error: {file_path} does not exist."

    with open(file_path, "a") as f:
        f.write("\n" + content.strip() + "\n")

    return "content appended successfully"


@tool
def apply_patch(file_path: str, old: str, new: str) -> str:
    """
    Apply a patch to a file.

    The agent must provide the previous content (old) and the updated
    content (new). The tool will verify that the current file matches
    'old' before applying the change.

    This prevents accidental overwrites if the file changed meanwhile.
    """
    if not os.path.exists(file_path):
        return f"error: {file_path} does not exist"
    with open(file_path) as f:
        current = f.read()
    if current != old:
        return "error: file content mismatch. read the file again before patching."
    with open(file_path, "w") as f:
        f.write(new)
    return "patch applied successfully"
