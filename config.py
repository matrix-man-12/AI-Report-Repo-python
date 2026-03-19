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
SEARCH_MARKER = "added"

# Date filters (Can be string in "YYYY-MM-DD" or None)
SINCE_DATE = "2026-01-01"
UNTIL_DATE = None

# Custom git log format delimiter to easily parse
GIT_LOG_DELIMITER = "---COMMITID---"
