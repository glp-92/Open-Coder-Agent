import tools.common.git
import tools.python.coder
import tools.python.inspector

TOOLS_REGISTRY: list[callable] = [
    tools.python.inspector.list_dir,
    tools.python.inspector.get_enhanced_signatures_from_module,
    tools.python.inspector.get_imports,
    tools.python.inspector.search_code,
    tools.python.inspector.read_file,
    tools.python.inspector.preview_patch,
    tools.python.coder.create_file,
    tools.python.coder.write_file,
    tools.python.coder.run_linting,
    tools.common.git.git_commit_and_push,
    tools.common.git.git_status,
    tools.common.git.git_switch,
]
