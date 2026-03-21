import os
import csv
from datetime import datetime
from typing import Dict
import config
from models import UserStats

def _get_global_stats(repo_stats_map: Dict[str, Dict[str, UserStats]]) -> Dict[str, UserStats]:
    global_stats: Dict[str, UserStats] = {}
    for repo_name, stats_dict in repo_stats_map.items():
        for email, stats in stats_dict.items():
            if email not in global_stats:
                global_stats[email] = UserStats(author=stats.author, email=stats.email)
            g_stats = global_stats[email]
            g_stats.ai_commits += stats.ai_commits
            g_stats.total_commits += stats.total_commits
            g_stats.ai_additions += stats.ai_additions
            g_stats.ai_deletions += stats.ai_deletions
            g_stats.total_additions += stats.total_additions
            g_stats.total_deletions += stats.total_deletions
    return global_stats

def _build_csv_headers(report_columns: dict) -> list:
    headers = ["Author", "Email"]
    if report_columns.get("Total Commits", True): headers.append("Total Commits")
    if report_columns.get("AI Commits", True): headers.append("AI Commits")
    if report_columns.get("Total Additions", True): headers.append("Total Additions")
    if report_columns.get("AI Additions", True): headers.append("AI Additions")
    if report_columns.get("Total Deletions", True): headers.append("Total Deletions")
    if report_columns.get("AI Deletions", True): headers.append("AI Deletions")
    if report_columns.get("AI Code %", True): headers.append("AI Code %")
    if report_columns.get("Aggregated AI Code %", True): headers.append("Aggregated AI Code %")
    return headers

def _build_row_stats(stat: UserStats, report_columns: dict) -> list:
    row = [stat.author, stat.email]
    if report_columns.get("Total Commits", True): row.append(stat.total_commits)
    if report_columns.get("AI Commits", True): row.append(stat.ai_commits)
    if report_columns.get("Total Additions", True): row.append(stat.total_additions)
    if report_columns.get("AI Additions", True): row.append(stat.ai_additions)
    if report_columns.get("Total Deletions", True): row.append(stat.total_deletions)
    if report_columns.get("AI Deletions", True): row.append(stat.ai_deletions)
    if report_columns.get("AI Code %", True): row.append(f"{stat.ai_code_percentage:.2f}%")
    if report_columns.get("Aggregated AI Code %", True): row.append(f"{stat.aggregated_ai_code_percentage:.2f}%")
    return row

def generate_csv_report(repo_stats_map: Dict[str, Dict[str, UserStats]]):
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(config.OUTPUT_DIR, f"ai_coverage_report_{timestamp_str}.csv")

    branch_str = getattr(config, "TARGET_BRANCH", None) or "All Branches"
    search_str = config.SEARCH_MARKER
    since_str = config.SINCE_DATE if config.SINCE_DATE else "Beginning of time"
    until_str = config.UNTIL_DATE if config.UNTIL_DATE else "Now"

    report_columns = getattr(config, "REPORT_COLUMNS", {})
    headers = _build_csv_headers(report_columns)

    with open(report_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Top level info
        writer.writerow(["Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow(["Range:", f"{since_str} to {until_str}"])
        writer.writerow(["Branches:", branch_str])
        writer.writerow(["Search Text:", search_str])
        writer.writerow([])
        
        # Per-repo stats
        for repo_name, stats_dict in repo_stats_map.items():
            if not stats_dict:
                continue
            writer.writerow(["Repo Name:", repo_name])
            writer.writerow(["Branch Name:", branch_str])
            writer.writerow(headers)
            
            sorted_stats = sorted(stats_dict.values(), key=lambda x: x.total_additions, reverse=True)
            for stat in sorted_stats:
                writer.writerow(_build_row_stats(stat, report_columns))
            writer.writerow([])
            
        # Global stats
        global_stats = _get_global_stats(repo_stats_map)
        if global_stats:
            writer.writerow(["Aggregated Repos"])
            writer.writerow(["Branch Name:", branch_str])
            writer.writerow(headers)
            sorted_global = sorted(global_stats.values(), key=lambda x: x.total_additions, reverse=True)
            for stat in sorted_global:
                writer.writerow(_build_row_stats(stat, report_columns))

    print(f"CSV Report generated successfully: {report_file}")
    return report_file

def _build_terminal_headers(report_columns: dict) -> tuple:
    cols = [("Author", 15), ("Email", 12)]
    if report_columns.get("Total Commits", True): cols.append(("Cmt", 5))
    if report_columns.get("AI Commits", True): cols.append(("AI_C", 4))
    if report_columns.get("Total Additions", True): cols.append(("Add", 7))
    if report_columns.get("AI Additions", True): cols.append(("AI_Add", 6))
    if report_columns.get("Total Deletions", True): cols.append(("Del", 7))
    if report_columns.get("AI Deletions", True): cols.append(("AI_Del", 6))
    if report_columns.get("AI Code %", True): cols.append(("AI %", 6))
    if report_columns.get("Aggregated AI Code %", True): cols.append(("Agg AI %", 8))
    
    fmt = " | ".join([f"{{:<{w}}}" for _, w in cols])
    header_names = [n for n, _ in cols]
    header_str = fmt.format(*header_names)
    total_width = len(header_str)
    return fmt, header_str, total_width

def _build_terminal_row(stat: UserStats, report_columns: dict, fmt: str) -> str:
    email_short = (stat.email[:9] + "...") if stat.email and len(stat.email) > 12 else stat.email
    author_short = (stat.author[:12] + "...") if stat.author and len(stat.author) > 15 else stat.author
    
    vals = [author_short or "", email_short or ""]
    if report_columns.get("Total Commits", True): vals.append(stat.total_commits)
    if report_columns.get("AI Commits", True): vals.append(stat.ai_commits)
    if report_columns.get("Total Additions", True): vals.append(stat.total_additions)
    if report_columns.get("AI Additions", True): vals.append(stat.ai_additions)
    if report_columns.get("Total Deletions", True): vals.append(stat.total_deletions)
    if report_columns.get("AI Deletions", True): vals.append(stat.ai_deletions)
    if report_columns.get("AI Code %", True): vals.append(f"{stat.ai_code_percentage:.1f}%")
    if report_columns.get("Aggregated AI Code %", True): vals.append(f"{stat.aggregated_ai_code_percentage:.1f}%")
    
    return fmt.format(*vals)

def print_terminal_report(repo_stats_map: Dict[str, Dict[str, UserStats]]):
    report_columns = getattr(config, "REPORT_COLUMNS", {})
    fmt, header_str, total_width = _build_terminal_headers(report_columns)
    
    branch_str = getattr(config, "TARGET_BRANCH", None) or "All Branches"
    search_str = config.SEARCH_MARKER
    since_str = config.SINCE_DATE if config.SINCE_DATE else "Beginning of time"
    until_str = config.UNTIL_DATE if config.UNTIL_DATE else "Now"

    print("\n" + "="*total_width)
    print(" AI CODE COVERAGE REPORT ".center(total_width, "="))
    print("="*total_width)
    print(f"Date:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Range:       {since_str} to {until_str}")
    print(f"Branches:    {branch_str}")
    print(f"Search Text: {search_str}")
    print("="*total_width)

    def print_stats(stats_dict):
        print("-" * total_width)
        print(header_str)
        print("-" * total_width)
        sorted_stats = sorted(stats_dict.values(), key=lambda x: x.total_additions, reverse=True)
        for s in sorted_stats:
            print(_build_terminal_row(s, report_columns, fmt))
        print("-" * total_width)

    for repo_name, stats_dict in repo_stats_map.items():
        if not stats_dict:
            continue
        print(f"\n[ Repository: {repo_name} | Branch: {branch_str} ]")
        print_stats(stats_dict)

    global_stats = _get_global_stats(repo_stats_map)
    if global_stats:
        print(f"\n[ Aggregated Repos | Branch: {branch_str} ]")
        print_stats(global_stats)
    
    print("\n" + "="*total_width + "\n")
