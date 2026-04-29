import subprocess

from langchain.tools import tool
from tools.utilities import REPOSITORY_ROOT_PATH, resolve_path, to_repository_relative_path

MAX_GIT_OUTPUT_CHARS = 8000
MAX_GIT_ENTRIES = 40
MAX_GIT_TIMEOUT_SECONDS = 15


def _truncate_output(output: str, max_chars: int) -> str:
    if len(output) <= max_chars:
        return output
    return f"{output[:max_chars]}\n... output truncated at {max_chars} chars"


def _run_git_command(args: list[str], timeout_seconds: int = MAX_GIT_TIMEOUT_SECONDS) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT_PATH,
            timeout=timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip() or "Unknown git error"
            return f"Error: git {' '.join(args)} failed: {stderr}"

        stdout = (completed.stdout or "").strip()
        return stdout or "Success: no output"
    except subprocess.TimeoutExpired:
        return f"Error: git command timed out after {timeout_seconds}s"
    except Exception as e:
        return f"Error executing git command: {e}"


@tool
def git_status_short() -> str:
    """
    Return a compact git status suitable for low-context models.
    """
    branch = _run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
    status = _run_git_command(["status", "--short"])

    if branch.startswith("Error:"):
        return branch
    if status.startswith("Error:"):
        return status

    status_lines = [] if status == "Success: no output" else status.splitlines()[:MAX_GIT_ENTRIES]
    if not status_lines:
        return f"Branch: {branch}\nWorking tree: clean"

    clipped = "\n".join(status_lines)
    return f"Branch: {branch}\nChanged files:\n{clipped}"


@tool
def git_diff_summary(max_chars: int = 4000) -> str:
    """
    Return a compact diff summary using --stat only.
    """
    bounded_chars = max(300, min(max_chars, MAX_GIT_OUTPUT_CHARS))
    diff_stat = _run_git_command(["--no-pager", "diff", "--stat"])
    if diff_stat.startswith("Error:"):
        return diff_stat
    if diff_stat == "Success: no output":
        return "No unstaged changes detected."
    return _truncate_output(diff_stat, bounded_chars)


@tool
def git_file_history(file_path: str, max_count: int = 10) -> str:
    """
    Return compact commit history for one file.
    """
    bounded_count = max(1, min(max_count, MAX_GIT_ENTRIES))
    try:
        resolved = resolve_path(file_path)
        if not resolved.exists():
            return f"Error: {file_path} does not exist"
        relative_path = to_repository_relative_path(resolved)
    except Exception as e:
        return f"Error: {e}"

    output = _run_git_command(
        [
            "--no-pager",
            "log",
            f"-n{bounded_count}",
            "--pretty=format:%h %ad %an %s",
            "--date=short",
            "--",
            relative_path,
        ]
    )
    if output.startswith("Error:"):
        return output
    if output == "Success: no output":
        return f"No git history found for {relative_path}"
    return output
