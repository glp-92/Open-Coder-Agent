import agent.src.tools.common.git
import agent.src.tools.python.coder
import agent.src.tools.python.inspector

TOOLS_REGISTRY: list[callable] = [
    agent.src.tools.python.inspector.get_project_tree,
    agent.src.tools.python.inspector.get_enhanced_signatures_from_module,
    agent.src.tools.python.inspector.get_imports,
    agent.src.tools.python.inspector.read_file,
    agent.src.tools.python.inspector.preview_patch,
    agent.src.tools.python.coder.create_file,
    agent.src.tools.python.coder.replace_in_file_all,
    agent.src.tools.python.coder.replace_in_file_first,
    agent.src.tools.python.coder.insert_in_file,
    agent.src.tools.common.git.git_commit,
    agent.src.tools.common.git.git_status,
    agent.src.tools.common.git.git_switch,
]
