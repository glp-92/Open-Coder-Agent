import os
import subprocess
from pathlib import Path

from langchain.tools import tool


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
        return f"Error writing file {file_path}: {e!s}"


@tool
def add_import(file_path: str, import_line: str) -> str:
    """
    Add a Python import if it does not already exist.
    This tool uses isort to ensure import is correctly placed
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: {file_path} not exists."
    content = path.read_text(encoding="utf-8")
    if import_line.strip() in content:
        return "Success: Import already exists"
    new_content = import_line.strip() + "\n" + content
    path.write_text(new_content, encoding="utf-8")
    try:
        # isort ordena y agrupa (ej. stdlib arriba, locales abajo)
        subprocess.run(["isort", file_path], check=True, capture_output=True)
        return "Success: Import added and sorted"
    except Exception as e:
        return f"Error: isort error but import added: {e}"


@tool
def replace_code_block(file_path: str, old_block: str, new_block: str) -> str:
    """
    Replace a block of code in a file.

    The old_block must match the exact code returned by read_file.
    This is safer than partial string replacements.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: El archivo {file_path} no existe."
    content = path.read_text(encoding="utf-8")
    if old_block not in content:
        return "Error: Not found block to replace. Be careful with spaces and indentation"
    lines_old = old_block.splitlines()
    base_indent = ""
    for line in lines_old:
        if line.strip():
            base_indent = line[: len(line) - len(line.lstrip())]
            break
    lines_new = new_block.splitlines()
    normalized_new = []
    for line in lines_new:
        if line.strip():
            current_indent = line[: len(line) - len(line.lstrip())]
            if not current_indent.startswith(base_indent):
                normalized_new.append(base_indent + line.lstrip())
            else:
                normalized_new.append(line)
        else:
            normalized_new.append("")
    final_new_block = "\n".join(normalized_new)
    new_content = content.replace(old_block, final_new_block)
    path.write_text(new_content, encoding="utf-8")
    return f"Success: File {file_path} update"


@tool
def insert_after_line(file_path: str, anchor: str, content: str) -> str:
    """
    Insert code after a line containing 'anchor'.

    The inserted content will automatically inherit the indentation
    of the anchor line to avoid syntax errors.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: {file_path} does not exist."

    lines = path.read_text().splitlines()
    for i, line in enumerate(lines):
        if anchor in line:
            indent = line[: len(line) - len(line.lstrip())]
            extra_indent = "    " if line.strip().endswith(":") else ""
            new_lines = [indent + extra_indent + line if line.strip() else line for line in content.splitlines()]
            final_lines = lines[: i + 1] + new_lines + lines[i + 1 :]
            path.write_text("\n".join(final_lines) + "\n")
            return "Success: Content insert with correct indent"

    return "Error: anchor for content insert not found"


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

    return "Success: content appended"


@tool
def apply_patch(file_path: str, old_code: str, new_code: str) -> str:
    """
    Apply a patch to a file.

    The tool checks that the previous content roughly matches the
    provided `old` content before writing `new`.

    After applying the patch it runs Ruff format and Ruff check.
    """
    path = Path(file_path)
    content = path.read_text()
    if old_code.strip() not in content.strip():
        return "Error: Block does not match, try more precise fragment."
    new_content = content.replace(old_code.strip(), new_code.strip())
    path.write_text(new_content)
    try:
        subprocess.run(["ruff", "format", file_path], check=True)
        subprocess.run(["ruff", "check", "--fix", file_path], check=True)
        return f"Edition success and code placed on {file_path}"
    except subprocess.CalledProcessError as e:
        return f"Error: Code insert success but errors on ruff format and check: {e.stderr}"
