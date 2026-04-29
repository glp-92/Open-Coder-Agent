import tools.bash.executor
import tools.git.inspector
import tools.javascript.inspector
import tools.python.coder
import tools.python.inspector

TOOLS_REGISTRY: list[callable] = [
    tools.python.inspector.get_repository_tree,
    tools.python.inspector.list_dir,
    tools.python.inspector.get_enhanced_signatures_from_module,
    tools.python.inspector.get_imports,
    tools.python.inspector.search_code,
    tools.python.inspector.find_files,
    tools.python.inspector.read_file,
    tools.python.inspector.file_stats,
    tools.python.coder.create_file,
    tools.python.coder.write_file,
    tools.python.coder.run_linting,
    tools.python.coder.make_dirs,
    tools.bash.executor.run_bash,
    tools.bash.executor.which_command,
    tools.git.inspector.git_status_short,
    tools.git.inspector.git_diff_summary,
    tools.git.inspector.git_file_history,
    tools.javascript.inspector.get_js_imports_exports,
    tools.javascript.inspector.search_js_symbol,
    tools.javascript.inspector.get_package_scripts,
]
