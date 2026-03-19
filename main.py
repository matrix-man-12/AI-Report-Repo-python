import os
from typing import Dict
import config
import git_utils
import analyzer
import report
from models import UserStats

def main():
    print("Starting AI vs Human Code Contribution Analysis...")
    
    if not os.path.exists(config.REPOS_FILE):
        print(f"Error: {config.REPOS_FILE} not found. Please create it and add repository URLs.")
        return

    with open(config.REPOS_FILE, 'r', encoding='utf-8') as f:
        repo_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not repo_urls:
        print("No repositories found in repos.txt. Exiting.")
        return

    global_stats: Dict[str, UserStats] = {}

    for url in repo_urls:
        print(f"\nProcessing repository: {url}")
        
        try:
            repo_path = git_utils.sync_repo(url, config.REPOS_DIR)
            repo_name = os.path.basename(repo_path)
            
            # Invalidate cache if search marker or dates have changed
            analyzer.check_cache_validity(repo_name)
            
            print(f"Fetching logs for {repo_name}...")
            log_output = git_utils.get_commits_log(repo_path, config.SINCE_DATE, config.UNTIL_DATE)
            
            print("Parsing and identifying AI contributions...")
            commits, new_shas = analyzer.parse_git_log(log_output, repo_name)
            
            print(f"Found {len(new_shas)} new commits to process.")
            
            repo_stats = analyzer.load_cached_stats(repo_name)

            if commits:
                analyzer.aggregate_stats(commits, repo_stats)
                analyzer.save_cached_stats(repo_name, repo_stats)
            
            # Merge repo stats into global_stats
            for user_email, stats in repo_stats.items():
                if user_email not in global_stats:
                    global_stats[user_email] = UserStats(author=stats.author, email=stats.email)
                
                g_stats = global_stats[user_email]
                g_stats.ai_commits += stats.ai_commits
                g_stats.total_commits += stats.total_commits
                g_stats.ai_additions += stats.ai_additions
                g_stats.ai_deletions += stats.ai_deletions
                g_stats.total_additions += stats.total_additions
                g_stats.total_deletions += stats.total_deletions
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Failed to process {url}: {e}")

    if global_stats:
        print("\nGenerating final report...")
        report.generate_csv_report(global_stats)
    else:
        print("\nNo stats to report. (No commits found or no repos processed properly).")

if __name__ == "__main__":
    main()
