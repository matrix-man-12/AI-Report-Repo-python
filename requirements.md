# AI vs Human Code Contribution Reporting Tool

## 1. Overview

This tool is an internal analytics system designed to generate reports that quantify:
- AI-generated code vs human-written code
- Per-user contribution metrics
- Per-repository and aggregated insights

It operates exclusively using:
- Git CLI
- GitHub CLI (`gh`)
- Python
- Bash/Windows batch

No GitHub APIs are used.

---

## 2. Objectives

- Measure AI-assisted development usage across repositories
- Provide manager-level visibility into:
  - AI vs Human contribution ratio
  - Developer activity metrics
- Ensure data accuracy matches GitHub Insights

---

## 3. Core Features

### 3.1 Repository Processing
- Accept a file containing repository URLs
- Clone repositories if not present
- Fetch updates if already cloned
- Process multiple repositories

---

### 3.2 Commit Analysis

Each commit is analyzed for:
- Author
- Email
- Commit message
- Additions
- Deletions
- Commit SHA

---

### 3.3 AI Commit Detection

AI commits are identified via commit message markers.

#### Default Marker:
AI-Agent: ClineSR

#### Detection Logic:
- Case-insensitive search
- If marker exists → AI commit
- Else → Human commit

#### Configurable:
- Custom search string via CLI

---

### 3.4 Metrics Per User

For each user:

- AI Tagged Commit Count
- Total Commits
- AI Tagged Additions
- AI Tagged Deletions
- Total Additions
- Total Deletions
- AI Code %
- Aggregated AI Code %

---

### 3.5 AI Code % Calculations

#### AI Code %
AI Additions / Total Additions * 100

#### Aggregated AI Code %
(AI Additions + AI Deletions) / (Total Additions + Total Deletions) * 100

---

## 4. System Workflow

1. Read repository list file
2. For each repository:
   - Clone or fetch updates
   - Extract commit data
   - Deduplicate commits using SHA
   - Classify AI vs Human
   - Aggregate user stats
3. Maintain global aggregation across repos
4. Generate CSV report

---

## 5. Directory Structure

ai-report-tool/
│
├── ai-report.exe
├── repos.txt
│
├── repos/
├── output/
└── .cache/

---

## 6. Performance Optimizations

### 6.1 Shallow Data Fetching
git clone --filter=blob:none

### 6.2 No Checkout
- Use git -C repo log
- Avoid working directory checkout

### 6.3 Parallel Processing
- Process repos concurrently

### 6.4 Incremental Processing
- Cache last processed timestamp
- Process only new commits

### 6.5 SHA Deduplication
- Prevent duplicate commit counting
- Use commit hash as unique identifier

---

## 7. Caching Strategy

Cache Types:
- Processed commit SHAs
- Last processed timestamp

Storage:
.cache/
  repo-name.json
  repo-name-shas.txt

---

## 8. User Normalization

Problem:
John Doe <email>
John Doe <no-reply.github.com>

Solution:
- Normalize by author name (case-insensitive)
- Optionally strip GitHub noreply emails

---

## 9. CLI Inputs

Required:
- --file (repo list file)

Optional:
- --search
- --since
- --until

---

## 10. Accuracy Requirements

To match GitHub Insights:

- Use git log --all
- Include merge commits
- Do not use shallow clone (--depth)
- Use --numstat
- Use consistent date filters

---

## 11. Edge Cases

- Empty commits → ignored
- Binary files → treated as 0 changes
- Division by zero → return 0%
- Missing commit messages → skip AI detection

---

## 12. Platform Requirements

- Windows compatible
- Executable-based usage (.exe)
- No dependency installation required for users

---

## 13. Security Constraints

- No public API usage
- Works only with repos user has access to
- Uses gh auth login for authentication

---

## 14. Non-Functional Requirements

- Fast execution (parallel + caching)
- Deterministic output
- Reproducible results
- Minimal setup for users

---

## 15. Limitations

- Relies on commit discipline (AI tagging)
- Cannot detect AI code without marker
- Email normalization may not always be perfect

---

## 16. Future Enhancements

- Monthly trends
- Repo-level summaries
- Visualization dashboards
- Threshold alerts


## in git_utils.py @Line:53 add to shallow clone
"--filter=blob:none"