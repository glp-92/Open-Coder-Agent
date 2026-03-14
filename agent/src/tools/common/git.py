import json

from langchain.tools import tool
from tools.utilities import run_subprocess_from_root_path


@tool
def git_status() -> str:
    """
    Shows current repository state (modified, added, deleted, untracked files).
    Use this to see what files need to be committed.
    """
    # Usamos -u para ver también archivos untracked individuales
    status = run_subprocess_from_root_path(["git", "status", "-s", "-u"])
    files = {"modified": [], "added": [], "deleted": [], "untracked": []}
    for line in status.splitlines():
        if len(line) < 3:
            continue
        code, file = line[:2].strip(), line[3:].strip()
        if "M" in code:
            files["modified"].append(file)
        elif "A" in code:
            files["added"].append(file)
        elif "D" in code:
            files["deleted"].append(file)
        elif "??" in code:
            files["untracked"].append(file)
    return json.dumps(files, indent=2)


@tool
def git_diff() -> str:
    """
    Shows the actual code changes in the staged and unstaged files.
    IMPORTANT: Use this before committing to understand what you are saving.
    """
    diff = run_subprocess_from_root_path(["git", "diff", "HEAD"])
    if not diff.strip():
        return "No changes detected between HEAD and working directory."
    return diff[:4000]


@tool
def git_switch(branch_name: str, create_new: bool = False) -> str:
    """
    Switches to a branch. If create_new is True, it creates it (-c).
    """
    cmd = ["git", "switch", "-c", branch_name] if create_new else ["git", "switch", branch_name]
    try:
        res: str = run_subprocess_from_root_path(args=cmd)
        return f"{res}"
    except Exception as e:
        return f"Exception: {e!s}"


@tool
def git_commit_and_push(branch_name: str, commit_message: str, files: list[str] | None = None) -> str:
    """
    Add files to staging area, commit them and push to a remote branch
    Returns log from operation
    """
    if files:
        run_subprocess_from_root_path(["git", "add", *files])
    else:
        run_subprocess_from_root_path(["git", "add", "."])

    commit_res: str = run_subprocess_from_root_path(["git", "commit", "-m", commit_message])
    if "Error" in commit_res:
        return commit_res
    check_remote: str = run_subprocess_from_root_path(["git", "remote"])
    if "origin" not in check_remote:
        return f"Success: Committed locally as '{commit_message}'. NOTE: Push skipped because no remote 'origin' is configured."  # noqa: E501
    push_res = run_subprocess_from_root_path(["git", "push", "-u", "origin", branch_name])
    return f"commit and push on: {commit_res}\n{push_res}"
