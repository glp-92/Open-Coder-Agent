import shlex
import shutil
import subprocess

from langchain.tools import tool
from tools.utilities import REPOSITORY_ROOT_PATH

MAX_BASH_TIMEOUT_SECONDS = 20
MAX_BASH_OUTPUT_CHARS = 8000
FORBIDDEN_SHELL_TOKENS = {"&&", "||", ";", "|", ">", "<", "$(", "`"}
READ_ONLY_COMMAND_ALLOWLIST = {
    "pwd",
    "ls",
    "cat",
    "head",
    "tail",
    "wc",
    "rg",
    "find",
    "stat",
    "du",
    "git",
    "python",
}


def _truncate_output(output: str, max_chars: int) -> str:
    if len(output) <= max_chars:
        return output
    return f"{output[:max_chars]}\n... output truncated at {max_chars} chars"


def _validate_bash_command(command: str) -> tuple[bool, str]:
    if not command.strip():
        return False, "Error: command cannot be empty"
    if any(token in command for token in FORBIDDEN_SHELL_TOKENS):
        return False, "Error: command contains forbidden shell operators"

    try:
        parsed = shlex.split(command)
    except ValueError as e:
        return False, f"Error: invalid command syntax: {e}"

    if not parsed:
        return False, "Error: command cannot be empty"

    executable = parsed[0]
    if executable not in READ_ONLY_COMMAND_ALLOWLIST:
        allowed = ", ".join(sorted(READ_ONLY_COMMAND_ALLOWLIST))
        return False, f"Error: command '{executable}' is not allowed. Allowed commands: {allowed}"

    if executable == "git" and len(parsed) > 1:
        forbidden_git_subcommands = {"reset", "clean", "checkout", "restore", "rebase", "push", "commit", "merge"}
        if parsed[1] in forbidden_git_subcommands:
            return False, f"Error: git subcommand '{parsed[1]}' is not allowed"

    return True, "OK"


@tool
def run_bash(command: str, timeout_seconds: int = 10, max_output_chars: int = MAX_BASH_OUTPUT_CHARS) -> str:
    """
    Run a single safe read-only bash command from repository root.
    """
    is_valid, reason = _validate_bash_command(command)
    if not is_valid:
        return reason

    bounded_timeout = max(1, min(timeout_seconds, MAX_BASH_TIMEOUT_SECONDS))
    bounded_chars = max(200, min(max_output_chars, MAX_BASH_OUTPUT_CHARS))

    args = shlex.split(command)
    try:
        result = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT_PATH,
            timeout=bounded_timeout,
        )
        output = (result.stdout or "") + (f"\nSTDERR:\n{result.stderr}" if result.stderr else "")
        output = output.strip() or "(no output)"
        return f"Exit code: {result.returncode}\n{_truncate_output(output, bounded_chars)}"
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {bounded_timeout}s"
    except Exception as e:
        return f"Error executing command: {e}"


@tool
def which_command(command_name: str) -> str:
    """
    Check whether a command is available in PATH.
    """
    if not command_name.strip():
        return "Error: command_name cannot be empty"
    path = shutil.which(command_name)
    if path:
        return f"Found: {command_name} -> {path}"
    return f"Not found: {command_name}"
