import subprocess

from langchain.tools import tool
from tools.utilities import run_subprocess_from_root_path


@tool
def git_status() -> str:
    """
    Shows current repository state (new, modified or ready files).
    """
    status = run_subprocess_from_root_path(["git", "status", "-s"])
    return status if status else "El repositorio está limpio."


@tool
def git_switch(branch_name: str) -> str:
    """
    Changes to a branch or creates a new one if not exists
    """
    res = subprocess.run(["git", "switch", branch_name], capture_output=True, text=True)
    if res.returncode == 0:
        return f"Changing to existing branch: {branch_name}"
    return run_subprocess_from_root_path(["git", "switch", "-c", branch_name])


@tool
def git_commit_and_push(branch_name: str, commit_message: str, files: list[str] | None = None) -> str:
    """
    Add files to staging area, commit them and open a remote branch
    Returns log from operation
    """
    if files:
        run_subprocess_from_root_path(["git", "add", *files])
    else:
        run_subprocess_from_root_path(["git", "add", "."])
    commit_res = run_subprocess_from_root_path(["git", "commit", "-m", commit_message])
    if "Error" in commit_res:
        return commit_res
    push_res = run_subprocess_from_root_path(["git", "push", "-u", "origin", branch_name])
    return f"commit and push on: {commit_res}\n{push_res}"
