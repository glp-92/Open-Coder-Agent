import subprocess

from langchain.tools import tool


def _run_git_command(args: list[str]) -> str:
    """
    Function to run git commands on a safe way
    """
    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        return result.stdout.strip() or f"operation {args[1]} success"
    except subprocess.CalledProcessError as e:
        return f"Error ejecutando {' '.join(args)}: {e.stderr}"


@tool
def git_status() -> str:
    """
    Shows current repository state (new, modified or ready files).
    """
    status = _run_git_command(["git", "status", "-s"])
    return status if status else "El repositorio está limpio."


@tool
def git_switch(branch_name: str) -> str:
    """
    Changes to a branch or creates a new one if not exists
    """
    res = subprocess.run(["git", "switch", branch_name], capture_output=True, text=True)
    if res.returncode == 0:
        return f"Changing to existing branch: {branch_name}"
    return _run_git_command(["git", "switch", "-c", branch_name])


@tool
def git_commit_and_push(branch_name: str, commit_message: str, files: list[str] | None = None) -> str:
    """
    Add files to staging area, commit them and open a remote branch
    Returns log from operation
    """
    if files:
        _run_git_command(["git", "add", *files])
    else:
        _run_git_command(["git", "add", "."])

    commit_res = _run_git_command(["git", "commit", "-m", commit_message])
    if "Error" in commit_res:
        return commit_res

    push_res = _run_git_command(["git", "push", "-u", "origin", branch_name])
    return f"commit and push on: {commit_res}\n{push_res}"
