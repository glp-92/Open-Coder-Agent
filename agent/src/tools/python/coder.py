import os

from langchain.tools import tool


@tool
def create_file(file_path: str, content: str) -> str:
    """
    Creates new file with content
    """
    if os.path.exists(file_path):
        return f"error: {file_path} already exists."
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)
    return f"File {file_path} created successfully."


@tool
def replace_in_file_first(file_path: str, old: str, new: str) -> str:
    """
    Replaces one code segment on a file
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
def replace_in_file_all(file_path: str, old: str, new: str) -> str:
    """
    Replaces all found code segments on a file
    """
    if not os.path.exists(file_path):
        return f"Error: {file_path} does not exist."
    with open(file_path) as f:
        content = f.read()
    if old not in content:
        return "error: text to replace not found"
    updated = content.replace(old, new, -1)
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
