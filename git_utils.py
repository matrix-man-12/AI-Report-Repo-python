import os
import subprocess
import logging
from typing import List, Optional
import config

logger = logging.getLogger(__name__)

def run_git_command(args: List[str], cwd: str, check: bool = True, silent_error: bool = False) -> str:
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
        if not silent_error:
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
        try:
            run_git_command(["fetch", "--all"], cwd=repo_path)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Warning: Could not fetch updates for {repo_name}. Proceeding with existing local data.")
    else:
        logger.info(f"Cloning {repo_name}...")
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        
        clone_args = ["git", "clone"]
        if getattr(config, "GIT_FILTER_BLOB_NONE", False):
            clone_args.append("--filter=blob:none")
        clone_args.extend([repo_url, repo_path])

        try:
            subprocess.run(
                clone_args,
                check=True,
                env=env,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Error cloning {repo_name}. Skipping repo. (Network/Auth redirect blocked git clone)")
            logger.debug(e.stderr)
            return None

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
    branch_specific_only = getattr(config, "GIT_BRANCH_SPECIFIC_ONLY", False)

    if target_branch:
        args.append(target_branch)

        # Base branch name used for checking refs (strip origin/ if present)
        ref_branch = target_branch[7:] if target_branch.startswith("origin/") else target_branch

        if branch_specific_only and target_branch != "--all":
            # Determine if this is a primary trunk branch. Trunk branches shouldn't violently 
            # subtract other branches because feature branches naturally contain the trunk's history.
            is_trunk = False
            trunk_names = ['main', 'master', 'dev', 'develop']
            for name in trunk_names:
                if ref_branch == name or ref_branch.endswith(f"/{name}"):
                    is_trunk = True
                    break

            try:
                # We always add --first-parent to strictly track the branch's true direct lineage
                args.append("--first-parent")

                # Only subtract ancestor history if this is an isolated feature branch
                if not is_trunk:
                    refs_output = run_git_command(["for-each-ref", "--format=%(refname)", "refs/heads/", "refs/remotes/"], cwd=repo_path)
                    all_refs = [ref.strip() for ref in refs_output.splitlines() if ref.strip()]
                    
                    trunk_refs = [
                        ref for ref in all_refs 
                        if any(ref.endswith(f"/{t}") for t in trunk_names) and ref != target_branch and not ref.endswith(f"/{ref_branch}")
                    ]
                    
                    if trunk_refs:
                        # Find all commits strictly on the trunk lineages
                        trunk_fp = set()
                        for t in trunk_refs:
                            out = run_git_command(["rev-list", "--first-parent", t], cwd=repo_path, silent_error=True)
                            if out:
                                trunk_fp.update(c.strip() for c in out.splitlines() if c.strip())
                        
                        # Find the feature's commits
                        feature_commits = run_git_command(["rev-list", target_branch], cwd=repo_path).splitlines()
                        
                        # The first commit in feature's recent history that exists in a trunk's first-parent 
                        # history is our exact fork point! This safely handles merged and unmerged branches.
                        fork_point = None
                        for c in feature_commits:
                            c = c.strip()
                            if c in trunk_fp:
                                fork_point = c
                                break
                                
                        if fork_point:
                            args.append("--not")
                            args.append(fork_point)
            except Exception as e:
                logger.warning(f"Warning: Could not isolate branch fork point. Proceeding without strict branch filtering. {e}")
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

    try:
        # The first attempt suppresses debug errors because failing to find a local branch is expected
        return run_git_command(args, cwd=repo_path, silent_error=True)
    except subprocess.CalledProcessError as original_error:
        # If a branch like 'feature-xyz' fails because it isn't tracked locally,
        # automatically fallback to checking 'origin/feature-xyz' which is fetched in sync_repo.
        if target_branch and not target_branch.startswith("origin/") and target_branch != "--all":
            try:
                args[args.index(target_branch)] = f"origin/{target_branch}"
                return run_git_command(args, cwd=repo_path)
            except subprocess.CalledProcessError:
                pass
        
        # If we couldn't fallback successfully, log the original error
        logger.debug(f"Error running git {' '.join(args)} in {repo_path}:")
        logger.debug(original_error.stderr)
        raise original_error
