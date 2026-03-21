import os
import subprocess
import logging
from typing import List, Optional
import config

logger = logging.getLogger(__name__)

def run_git_command(args: List[str], cwd: str, check: bool = True) -> str:
    """Run a git command in the specified directory."""
    try:
        # Avoid hanging on interactive prompts if credentials are required
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.debug(f"Error running git {' '.join(args)} in {cwd}:")
        logger.debug(e.stderr)
        raise

def sync_repo(repo_url: str, repos_dir: str) -> str:
    """Clone or fetch a repository. Returns the path to the repository."""
    if repo_url.strip() == ".":
        logger.info("Using current directory as repository...")
        return os.getcwd()

    if not os.path.exists(repos_dir):
        os.makedirs(repos_dir, exist_ok=True)

    # Extract repo name from URL
    repo_name = repo_url.rstrip('/').split('/')[-1]
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]

    repo_path = os.path.join(repos_dir, repo_name)

    if os.path.exists(repo_path) and os.path.isdir(os.path.join(repo_path, '.git')):
        logger.info(f"Fetching updates for {repo_name}...")
        run_git_command(["fetch", "--all"], cwd=repo_path)
    else:
        logger.info(f"Cloning {repo_name}...")
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        
        clone_args = ["git", "clone"]
        if getattr(config, "GIT_FILTER_BLOB_NONE", False):
            clone_args.append("--filter=blob:none")
        clone_args.extend([repo_url, repo_path])

        subprocess.run(
            clone_args,
            check=True,
            env=env
        )

    return repo_path

def get_commits_log(repo_path: str, since: Optional[str] = None, until: Optional[str] = None) -> str:
    """
    Get the raw string output of git log.
    Includes custom delimiter to easily parse commits.
    """
    format_string = f"{config.GIT_LOG_DELIMITER}%n%H%n%an%n%ae%n%ad%n%B%n---ENDMESSAGE---"
    
    args = [
        "log",
        "--numstat",
        "--date=iso-strict",
        f"--format={format_string}"
    ]
    
    target_branch = getattr(config, "TARGET_BRANCH", None)
    if target_branch:
        args.append(target_branch)
    else:
        args.append("--all")

    if getattr(config, "GIT_NO_RENAMES", False):
        args.append("--no-renames")

    if getattr(config, "GIT_NO_MERGES", False):
        args.append("--no-merges")

    if since:
        args.append(f"--since={since}")
    if until:
        args.append(f"--until={until}")

    return run_git_command(args, cwd=repo_path)
