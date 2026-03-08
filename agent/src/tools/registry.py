import tools.git
import tools.inspector

TOOLS_REGISTRY: list[callable] = [
    tools.inspector.get_project_tree,
    tools.inspector.get_enhanced_signatures_from_module,
    tools.inspector.get_imports,
    tools.inspector.read_file,
    tools.inspector.create_file,
    tools.inspector.replace_in_file_all,
    tools.inspector.replace_in_file_first,
    tools.inspector.insert_in_file,
    tools.inspector.preview_patch,
    tools.git.git_commit,
    tools.git.git_status,
    tools.git.git_switch,
]
