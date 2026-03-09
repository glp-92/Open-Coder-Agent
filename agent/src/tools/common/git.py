import subprocess

from langchain.tools import tool


@tool
def git_commit(branch_name: str, commit_message: str, files_to_commit: list[str]):
    """
    Add files, commit them into a branch and push them to remote
    Returns log from operation
    """
    files = [str(f) for f in files_to_commit]
    subprocess.run(["git", "add", *files], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True)
    subprocess.run(
        ["git", "push", "-u", "origin", branch_name],
        check=True,
        capture_output=True,
    )
    return f"commit success to branch {branch_name}"


@tool
def git_switch(branch_name: str) -> str:
    """
    Changes branch based on branch name
    """

    def get_current_branch() -> str:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    if get_current_branch() == branch_name:
        return f"Already on branch: {branch_name}"
    check = subprocess.run(
        ["git", "branch", "--list", branch_name],
        capture_output=True,
        text=True,
    )
    if check.stdout.strip():
        subprocess.run(["git", "switch", branch_name])
        return f"Switched to existing branch: {branch_name}"
    subprocess.run(["git", "switch", "-c", branch_name])
    return f"Created and switched to new branch: {branch_name}"


@tool
def git_status() -> str:
    """
    Shows new, modified and ready files for commit
    """
    result = subprocess.run(["git", "status", "-s"], check=True, capture_output=True, text=True)
    if not result.stdout.strip():
        return "nothing to commit"
    return f"current repo status: {result.stdout}"
