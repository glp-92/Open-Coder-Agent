from tools.git import git_commit, git_status, git_switch
from tools.inspector import (
    create_file,
    get_function_signatures,
    get_imports,
    insert_in_file,
    list_files,
    preview_patch,
    read_file,
    read_symbol,
    replace_in_file,
    search_code,
)

TOOL_REGISTRY = {
    "search_code": search_code,
    "read_file": read_file,
    "read_symbol": read_symbol,
    "insert_in_file": insert_in_file,
    "replace_in_file": replace_in_file,
    "create_file": create_file,
    "preview_patch": preview_patch,
    "git_status": git_status,
    "git_switch": git_switch,
    "git_commit": git_commit,
    "list_files": list_files,
    "get_imports": get_imports,
    "get_function_signatures": get_function_signatures,
}
