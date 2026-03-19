import os
import json
from datetime import datetime
from typing import List, Dict, Set, Tuple
import config
from models import CommitInfo, UserStats

def normalize_email(email: str) -> str:
    """Normalize GitHub noreply emails to a standard form."""
    email = email.lower().strip()
    if "noreply.github.com" in email:
        # e.g. 1234567+username@users.noreply.github.com
        parts = email.split('@')[0]
        if '+' in parts:
            return parts.split('+')[1]
        return parts
    return email

def normalize_name(name: str) -> str:
    return name.strip().title()

def check_cache_validity(repo_name: str):
    """Check if config changed. If so, clear cache for this repo."""
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    meta_file = os.path.join(config.CACHE_DIR, f"{repo_name}_meta.json")
    current_meta = {
        "search_marker": config.SEARCH_MARKER,
        "since_date": config.SINCE_DATE,
        "until_date": config.UNTIL_DATE
    }
    
    shas_file = os.path.join(config.CACHE_DIR, f"{repo_name}_shas.json")
    stats_file = os.path.join(config.CACHE_DIR, f"{repo_name}_stats.json")
    
    invalidate = False
    if os.path.exists(meta_file):
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                cached_meta = json.load(f)
            if cached_meta != current_meta:
                invalidate = True
        except Exception:
            invalidate = True
    else:
        invalidate = True
        
    if invalidate:
        if os.path.exists(shas_file): os.remove(shas_file)
        if os.path.exists(stats_file): os.remove(stats_file)
            
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(current_meta, f)

def load_cached_shas(repo_name: str) -> Set[str]:
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(config.CACHE_DIR, f"{repo_name}_shas.json")
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()

def save_cached_shas(repo_name: str, shas: Set[str]):
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(config.CACHE_DIR, f"{repo_name}_shas.json")
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(list(shas), f)

def load_cached_stats(repo_name: str) -> Dict[str, UserStats]:
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(config.CACHE_DIR, f"{repo_name}_stats.json")
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return {k: UserStats.from_dict(v) for k, v in data.items()}
            except ValueError:
                return {}
    return {}

def save_cached_stats(repo_name: str, stats: Dict[str, UserStats]):
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(config.CACHE_DIR, f"{repo_name}_stats.json")
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump({k: v.to_dict() for k, v in stats.items()}, f)

def parse_git_log(log_output: str, repo_name: str) -> Tuple[List[CommitInfo], Set[str]]:
    """Parse raw git log output and return a list of CommitInfo objects and new SHAs."""
    processed_shas = load_cached_shas(repo_name)
    new_shas = set()
    commits = []

    if not log_output.strip():
        return commits, new_shas

    raw_commits = log_output.split(config.GIT_LOG_DELIMITER)

    for raw_commit in raw_commits:
        raw_commit = raw_commit.strip()
        if not raw_commit:
            continue

        parts = raw_commit.split("\n---ENDMESSAGE---")
        if len(parts) < 1:
            continue

        header_and_body = parts[0].strip().split('\n', 4)
        if len(header_and_body) < 5:
            continue
            
        sha = header_and_body[0].strip()
        if sha in processed_shas:
            continue
            
        author = normalize_name(header_and_body[1].strip())
        email = normalize_email(header_and_body[2].strip())
        
        timestamp_str = header_and_body[3].strip()
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
        except ValueError:
            timestamp = datetime.now()

        message = header_and_body[4].strip()
        is_ai = config.SEARCH_MARKER.lower() in message.lower()

        additions = 0
        deletions = 0
        
        if len(parts) > 1:
            numstats = parts[1].strip().split('\n')
            for stat_line in numstats:
                stat_parts = stat_line.split('\t')
                if len(stat_parts) >= 2:
                    adds = stat_parts[0].strip()
                    dels = stat_parts[1].strip()
                    # Binary files output '-'
                    if adds != '-':
                        additions += int(adds)
                    if dels != '-':
                        deletions += int(dels)

        commit_info = CommitInfo(
            sha=sha,
            author=author,
            email=email,
            timestamp=timestamp,
            message=message,
            additions=additions,
            deletions=deletions,
            is_ai=is_ai
        )
        commits.append(commit_info)
        new_shas.add(sha)

    if new_shas:
        processed_shas.update(new_shas)
        save_cached_shas(repo_name, processed_shas)

    return commits, new_shas

def aggregate_stats(commits: List[CommitInfo], stats_dict: Dict[str, UserStats]):
    """Update user stats based on a list of new commits."""
    for commit in commits:
        user_key = commit.email if commit.email else commit.author
        
        if user_key not in stats_dict:
            stats_dict[user_key] = UserStats(author=commit.author, email=commit.email)
            
        stats = stats_dict[user_key]
        
        stats.total_commits += 1
        stats.total_additions += commit.additions
        stats.total_deletions += commit.deletions
        
        if commit.is_ai:
            stats.ai_commits += 1
            stats.ai_additions += commit.additions
            stats.ai_deletions += commit.deletions
