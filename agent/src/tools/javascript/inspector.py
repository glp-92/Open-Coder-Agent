import fnmatch
import json
import re
from pathlib import Path

from langchain.tools import tool
from tools.utilities import IGNORE_DIRS, resolve_path, to_repository_relative_path

JS_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
MAX_JS_RESULTS = 30
MAX_JS_FILE_READ_CHARS = 40000

IMPORT_PATTERN = re.compile(r"^\s*import\s+.+", re.MULTILINE)
EXPORT_PATTERN = re.compile(r"^\s*export\s+.+", re.MULTILINE)


def _is_js_file(path: Path) -> bool:
    return path.suffix in JS_EXTENSIONS


@tool
def get_js_imports_exports(file_path: str, max_results: int = MAX_JS_RESULTS) -> str:
    """
    Extract compact import/export lines from a JS/TS module.
    """
    bounded_max = max(1, min(max_results, MAX_JS_RESULTS))
    path = resolve_path(file_path)
    if not path.exists() or not path.is_file():
        return f"Error: {file_path} does not exist or is not a file"
    if not _is_js_file(path):
        return f"Error: {file_path} is not a JS/TS file"

    content = path.read_text(encoding="utf-8")
    content = content[:MAX_JS_FILE_READ_CHARS]

    imports = IMPORT_PATTERN.findall(content)
    exports = EXPORT_PATTERN.findall(content)

    items = [*(f"IMPORT: {line.strip()}" for line in imports), *(f"EXPORT: {line.strip()}" for line in exports)]
    if not items:
        return "No import/export statements found."

    clipped = items[:bounded_max]
    if len(items) > bounded_max:
        clipped.append(f"... truncated after {bounded_max} results")
    return "\n".join(clipped)


@tool
def search_js_symbol(symbol: str, path: str = ".", max_results: int = MAX_JS_RESULTS) -> str:
    """
    Search a symbol in JS/TS files with bounded output.
    """
    if not symbol.strip():
        return "Error: symbol cannot be empty"
    bounded_max = max(1, min(max_results, MAX_JS_RESULTS))
    root = resolve_path(path)

    matches: list[str] = []
    for current_root, dir_names, file_names in __import__("os").walk(root):
        dir_names[:] = [name for name in sorted(dir_names) if name not in IGNORE_DIRS]
        for file_name in sorted(file_names):
            full_path = Path(current_root) / file_name
            if not _is_js_file(full_path):
                continue
            try:
                with open(full_path, encoding="utf-8") as file_obj:
                    for line_number, line in enumerate(file_obj, start=1):
                        if symbol in line:
                            matches.append(
                                f"{to_repository_relative_path(full_path)}:{line_number}: {line.strip()[:180]}"
                            )
                            if len(matches) >= bounded_max:
                                return "\n".join(matches)
            except (UnicodeDecodeError, OSError):
                continue

    return "\n".join(matches) if matches else "No symbol matches found in JS/TS files."


@tool
def get_package_scripts(package_json_path: str = "package.json") -> str:
    """
    Return scripts from package.json in a compact format.
    """
    path = resolve_path(package_json_path)
    if not path.exists() or not path.is_file():
        return f"Error: {package_json_path} does not exist or is not a file"

    if path.name != "package.json" and not fnmatch.fnmatch(path.name, "*.package.json"):
        return "Error: expected a package.json-like file"

    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return f"Error: invalid JSON: {e}"

    scripts = parsed.get("scripts")
    if not isinstance(scripts, dict) or not scripts:
        return "No scripts found."

    lines = [f"{name}: {command}" for name, command in list(scripts.items())[:MAX_JS_RESULTS]]
    if len(scripts) > MAX_JS_RESULTS:
        lines.append(f"... truncated after {MAX_JS_RESULTS} scripts")
    return "\n".join(lines)
