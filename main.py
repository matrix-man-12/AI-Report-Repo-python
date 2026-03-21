import os
import logging
from typing import Dict
import config
import logger  # Initializes logging
import git_utils
import analyzer
import report
from models import UserStats

logger_instance = logging.getLogger(__name__)

def main():
    logger_instance.info("Starting AI vs Human Code Contribution Analysis...")
    
    if not os.path.exists(config.REPOS_FILE):
        logger_instance.error(f"Error: {config.REPOS_FILE} not found. Please create it and add repository URLs.")
        return

    with open(config.REPOS_FILE, 'r', encoding='utf-8') as f:
        repo_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not repo_urls:
        logger_instance.warning("No repositories found in repos.txt. Exiting.")
        return

    alias_map = None
    if getattr(config, "USE_ALIASES", False) and getattr(config, "ALIASES_FILE", None):
        if os.path.exists(config.ALIASES_FILE):
            try:
                import json
                with open(config.ALIASES_FILE, 'r', encoding='utf-8') as f:
                    raw_aliases = json.load(f)
                alias_map = {}
                for primary_name, fragments in raw_aliases.items():
                    for frag in fragments:
                        if isinstance(frag, str):
                            alias_map[frag] = primary_name
                logger_instance.info(f"Loaded {len(alias_map)} identity aliases from {config.ALIASES_FILE}")
            except Exception as e:
                logger_instance.error(f"Failed to load ALIASES_FILE: {e}")
        else:
            logger_instance.warning(f"USE_ALIASES is True but {config.ALIASES_FILE} was not found.")

    repo_stats_map: Dict[str, Dict[str, UserStats]] = {}

    for url in repo_urls:
        logger_instance.info(f"\nProcessing repository: {url}")
        
        try:
            repo_path = git_utils.sync_repo(url, config.REPOS_DIR)
            repo_name = os.path.basename(repo_path)
            
            # Invalidate cache if search marker or dates have changed
            analyzer.check_cache_validity(repo_name)
            repo_stats = analyzer.load_cached_stats(repo_name)
            
            try:
                logger_instance.info(f"Fetching logs for {repo_name}...")
                log_output = git_utils.get_commits_log(repo_path, config.SINCE_DATE, config.UNTIL_DATE)
                
                logger_instance.info("Parsing and identifying AI contributions...")
                commits, new_shas = analyzer.parse_git_log(log_output, repo_name)
                
                logger_instance.info(f"Found {len(new_shas)} new commits to process.")
                
                if commits:
                    analyzer.aggregate_stats(commits, repo_stats, alias_map=alias_map)
                    analyzer.save_cached_stats(repo_name, repo_stats)
            except Exception:
                target = getattr(config, 'TARGET_BRANCH', None)
                msg_branch = f" branch '{target}'" if target else ""
                logger_instance.warning(f"Could not fetch/parse logs for {repo_name}. Check if{msg_branch} actually exists.")
            
            repo_stats_map[repo_name] = repo_stats
                
        except Exception as e:
            logger_instance.error(f"Critical error processing {url}: {e}", exc_info=True)

    if repo_stats_map:
        if getattr(config, "OUTPUT_CSV", True):
            logger_instance.info("\nGenerating final CSV report...")
            report.generate_csv_report(repo_stats_map)
        if getattr(config, "OUTPUT_TERMINAL", True):
            logger_instance.info("\nGenerating terminal report...")
            report.print_terminal_report(repo_stats_map)
    else:
        logger_instance.warning("\nNo stats to report. (No commits found or no repos processed properly).")

if __name__ == "__main__":
    main()
