import tools.common.git
import tools.python.coder
import tools.python.inspector

TOOLS_REGISTRY: list[callable] = [
    tools.python.inspector.get_project_tree,
    tools.python.inspector.get_enhanced_signatures_from_module,
    tools.python.inspector.get_imports,
    tools.python.inspector.read_file,
    tools.python.inspector.preview_patch,
    tools.python.coder.create_file,
    tools.python.coder.replace_code_block,
    tools.python.coder.insert_after_line,
    tools.python.coder.append_to_file,
    tools.python.coder.apply_patch,
    tools.common.git.git_commit,
    tools.common.git.git_status,
    tools.common.git.git_switch,
]
