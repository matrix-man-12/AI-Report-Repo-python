import os

# Base directory for the tool
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directories
REPOS_DIR = os.path.join(BASE_DIR, "repos")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CACHE_DIR = os.path.join(BASE_DIR, ".cache")
LOG_DIR = os.path.join(BASE_DIR, "logs")
ALIASES_DIR = os.path.join(BASE_DIR, "aliases")

# Files
REPOS_FILE = os.path.join(BASE_DIR, "repos.txt")
ALIASES_FILE = os.path.join(ALIASES_DIR, "my_aliases.json")

# Identity Resolution Configuration
# Set to True to enable explicit fuzzy identity merging using ALIASES_FILE.
USE_ALIASES = False

# Commit matching config
SEARCH_MARKER = "added"

# If True, the search marker must match exactly (e.g. "Fix" won't match "fix").
# If False, the search is case-insensitive.
SEARCH_CASE_SENSITIVE = False

# Git options

# If True, completely filters out merge commits (e.g. PR approvals or developer git pulls) from the log.
# This prevents commit counts from artificially inflating when no actual code was written.
GIT_NO_MERGES = True

# If True, treats file renames as a full deletion of the old file and full addition of the new file.
# This makes the addition/deletion counts match GitHub Insights exactly.
# If False, git detects renames and only counts the specific lines modified during the rename.(this makes more sense here)
GIT_NO_RENAMES = True

# If True, performs a "blobless clone" (--filter=blob:none), which drastically speeds up
# repository cloning and saves disk space by only downloading the commit history, not file contents.
# If False, performs a standard full git clone.
GIT_FILTER_BLOB_NONE = True

# If True, calculates changes made to the target branch exclusively.
# It automatically filters out legacy commits from checkout branches 
# and pulled commits from other branches.
GIT_BRANCH_SPECIFIC_ONLY = True

# Target branch to analyze. If None, analyzes all branches. 
# Example: "main", "master", or 'origin/main'
TARGET_BRANCH = 'main'

# Output controls
OUTPUT_CSV = True
OUTPUT_TERMINAL = True

# Select which columns to include in the output reports.
# "Author" and "Email" will always be included.
REPORT_COLUMNS = {
    "Total Commits": True,
    "AI Commits": True,
    "Total Additions": True,
    "AI Additions": True,
    "Total Deletions": True,
    "AI Deletions": True,
    "AI Code %": True,
    "Aggregated AI Code %": True
}

# Date filters (Can be string in "YYYY-MM-DD" or None)
SINCE_DATE = "2025-01-01"
UNTIL_DATE = None

# Custom git log format delimiter to easily parse
GIT_LOG_DELIMITER = "---COMMITID---"
