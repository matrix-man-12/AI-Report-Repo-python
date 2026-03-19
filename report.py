import os
import csv
from datetime import datetime
from typing import Dict, List
import config
from models import UserStats

def generate_csv_report(stats_dict: Dict[str, UserStats]):
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(config.OUTPUT_DIR, f"ai_coverage_report_{timestamp_str}.csv")

    headers = [
        "Author",
        "Email",
        "Total Commits",
        "AI Commits",
        "Total Additions",
        "AI Additions",
        "Total Deletions",
        "AI Deletions",
        "AI Code %",
        "Aggregated AI Code %"
    ]

    # Sort users by total additions descending
    sorted_stats = sorted(stats_dict.values(), key=lambda x: x.total_additions, reverse=True)

    with open(report_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Add metadata headers for Excel readability
        writer.writerow(["Report Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow(["Search Marker:", config.SEARCH_MARKER])
        since_str = config.SINCE_DATE if config.SINCE_DATE else "Beginning of time"
        until_str = config.UNTIL_DATE if config.UNTIL_DATE else "Now"
        writer.writerow(["Date Range:", f"{since_str} to {until_str}"])
        writer.writerow([])  # Empty row for spacing
        
        writer.writerow(headers)

        for stat in sorted_stats:
            writer.writerow([
                stat.author,
                stat.email,
                stat.total_commits,
                stat.ai_commits,
                stat.total_additions,
                stat.ai_additions,
                stat.total_deletions,
                stat.ai_deletions,
                f"{stat.ai_code_percentage:.2f}%",
                f"{stat.aggregated_ai_code_percentage:.2f}%"
            ])

    print(f"Report generated successfully: {report_file}")
    return report_file
