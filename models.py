from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class CommitInfo:
    sha: str
    author: str
    email: str
    timestamp: datetime
    message: str
    additions: int
    deletions: int
    is_ai: bool

@dataclass
class UserStats:
    author: str
    email: str
    ai_commits: int = 0
    total_commits: int = 0
    ai_additions: int = 0
    ai_deletions: int = 0
    total_additions: int = 0
    total_deletions: int = 0

    @property
    def ai_code_percentage(self) -> float:
        if self.total_additions == 0:
            return 0.0
        return (self.ai_additions / self.total_additions) * 100.0

    @property
    def aggregated_ai_code_percentage(self) -> float:
        total_changes = self.total_additions + self.total_deletions
        if total_changes == 0:
            return 0.0
        ai_changes = self.ai_additions + self.ai_deletions
        return (ai_changes / total_changes) * 100.0

    def to_dict(self):
        return {
            "author": self.author,
            "email": self.email,
            "ai_commits": self.ai_commits,
            "total_commits": self.total_commits,
            "ai_additions": self.ai_additions,
            "ai_deletions": self.ai_deletions,
            "total_additions": self.total_additions,
            "total_deletions": self.total_deletions
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
