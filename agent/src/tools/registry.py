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

TOOLS_REGISTRY: list[callable] = [
    git_commit,
    git_status,
    git_switch,
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
]
