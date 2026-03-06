import subprocess

from langchain.tools import tool


@tool
def git_commit(branch_name: str, commit_message: str, files_to_commit: list[str]):
    """
    add files, commit them into a branch and push them to remote
    returns log from operation
    """
    try:
        files = [str(f) for f in files_to_commit]
        subprocess.run(["git", "add", *files], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True)
        subprocess.run(
            ["git", "push", "-u", "origin", branch_name],
            check=True,
            capture_output=True,
        )
        return f"commit success to branch {branch_name}"
    except subprocess.CalledProcessError as e:
        return f"git commit err: {e.stderr.decode()}"


@tool
def git_switch(branch_name: str, create_new: bool = True) -> str:
    """
    branch change
    """
    command = ["git", "switch"]
    if create_new:
        command.append("-c")
    command.append(branch_name)
    try:
        result = subprocess.run(command, check=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"branch change err: {e.stderr.decode()}"


@tool
def git_status() -> str:
    """
    shows new, modified and ready files for commit
    """
    try:
        result = subprocess.run(["git", "status", "-s"], check=True, capture_output=True, text=True)
        if not result.stdout.strip():
            return "nothing to commit"
        return f"current repo status: {result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"error calling git status: {e.stderr}"
    except FileNotFoundError:
        return "git not found"
