import os

# Base directory for the tool
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directories
REPOS_DIR = os.path.join(BASE_DIR, "repos")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CACHE_DIR = os.path.join(BASE_DIR, ".cache")

# Files
REPOS_FILE = os.path.join(BASE_DIR, "repos.txt")

# Commit matching config
SEARCH_MARKER = "AI-Agent: ClineSR"

# Git options

# If True, treats file renames as a full deletion of the old file and full addition of the new file.
# This makes the addition/deletion counts match GitHub Insights exactly.
# If False, git detects renames and only counts the specific lines modified during the rename.(this makes more sense here)
GIT_NO_RENAMES = True

# If True, performs a "blobless clone" (--filter=blob:none), which drastically speeds up
# repository cloning and saves disk space by only downloading the commit history, not file contents.
# If False, performs a standard full git clone.
GIT_FILTER_BLOB_NONE = True

# Date filters (Can be string in "YYYY-MM-DD" or None)
SINCE_DATE = "2020-01-01"
UNTIL_DATE = None

# Custom git log format delimiter to easily parse
GIT_LOG_DELIMITER = "---COMMITID---"
