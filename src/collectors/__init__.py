from .base import BaseCollector
from .rss import RSSCollector
from .hackernews import HackerNewsCollector
from .reddit import RedditCollector
from .arxiv import ArxivCollector
from .github_trending import GitHubTrendingCollector

__all__ = [
    "BaseCollector",
    "RSSCollector",
    "HackerNewsCollector",
    "RedditCollector",
    "ArxivCollector",
    "GitHubTrendingCollector",
]
