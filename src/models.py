"""Data models for Daily AI Briefing."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Article:
    """Represents a single news article from any source."""

    id: str
    title: str
    url: str
    source: str  # e.g., "reddit", "rss", "hackernews", "arxiv"
    source_name: str  # e.g., "r/MachineLearning", "OpenAI Blog"
    published_at: datetime
    summary: Optional[str] = None
    score: Optional[int] = None  # Upvotes, points, etc.
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    computed_score: float = 0.0  # For ranking

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Article):
            return False
        return self.id == other.id
